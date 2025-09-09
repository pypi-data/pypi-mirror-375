from django.shortcuts import render
from .models import DatabaseCred, DataEntry
import pandas as pd
import uuid
import logging
import numpy as np
import matplotlib.pyplot as plt
import io
import os
import base64
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.embed import components
from bokeh.io.export import export_png,export_svgs
from sqlalchemy import create_engine,text
from .forms import DataEntryForm,CustomFieldValueForm,CombinedDataEntryForm, ChartChooserForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from api.instagram.models import CustomFieldValue
from api.instagram.forms import CustomFieldValueForm
from django.forms import modelformset_factory
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy import create_engine
from .serializers import CombinedDataEntrySerializer
from django_tenants.utils import schema_context


@api_view(['GET', 'POST'])
@schema_context(os.getenv("SCHEMA_NAME"))
def get_sql_records(request):
    entries = DataEntry.objects.all()
    data = []
    for entry in entries:
        data.append({
            'id': entry.id,
            'name': entry.name,
            'query': entry.query,
            'chart_type': entry.chart_type
        })
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@schema_context(os.getenv("SCHEMA_NAME"))
def get_sql_record(request, pk):
    try:
        entry = DataEntry.objects.get(pk=pk)
    except DataEntry.DoesNotExist:
        return Response({'error': 'DataEntry not found.'}, status=status.HTTP_404_NOT_FOUND)

    data = {
        'id': entry.id,
        'name': entry.name,
        'query': entry.query,
        'chart_type': entry.chart_type
    }
    return Response(data, status=status.HTTP_200_OK)

# Create your views here.
@api_view(['GET', 'POST'])
@schema_context(os.getenv("SCHEMA_NAME"))
def dashboard_api(request):
    df_html = None
    df = pd.DataFrame()

    if request.method == 'POST':
            # Get the DataEntry instance based on the provided ID if it exists
            # or fetch the last entry if the ID is not provided
            entry = None
            try:
                entry = DataEntry.objects.get(id=request.data['id'])
            except Exception as err:
                logging.warning(f"Error fetching DataEntry: {err}")
                try:
                    entry = DataEntry.objects.last()
                except Exception as err:
                    logging.error(f"Error fetching DataEntry: {err}")
                    return Response({'error': 'DataEntry not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            query = entry.query  # Assuming there's a query field in DataEntry
            
            if query:
                # Database connection parameters
                db_params = {
                    'username': os.getenv('POSTGRES_USERNAME'),
                    'password': os.getenv('POSTGRES_PASSWORD'),
                    'host': os.getenv('POSTGRES_HOST'),
                    'port': os.getenv('POSTGRES_PORT'),
                    'database': os.getenv('POSTGRES_DBNAME')
                }

                # Create a connection string
                connection_string = f"postgresql+psycopg2://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
                engine = create_engine(connection_string)

                try:
                    df_temp = pd.read_sql(query, engine)  # Execute the query
                    df = pd.concat([df, df_temp], ignore_index=True)  # Combine results if multiple queries are executed
                    df_html = df_temp.to_html(classes='table table-striped', index=False)
                    # df.columns = [f'col{i+1}' for i in range(df.shape[1])]

                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
            chart_data = generate_charts(entry, df)  # Implement this function based on your charting logic
            
            return Response({
                'dataframe': df_html,
                'charts': chart_data,
            }, status=status.HTTP_201_CREATED)

        
    else:
        return Response({'message': 'GET method not supported for this endpoint.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

def generate_charts(entry, df):
    """ Generate charts based on entry.chart_type and return chart data. """
    chart_data = {}
    
    if entry.chart_type == 'line':
        chart_data['mpl'] = plot_matplotlib(df)  # Your existing plotting function for matplotlib
        chart_data['chart_type'] = 'matplotlib'
    elif entry.chart_type == 'bar':
        chart_data['bokeh_div'], chart_data['bokeh_script'] = plot_bokeh(df)  # Your existing plotting function for bokeh
        chart_data['chart_type'] = 'bokeh'
    return chart_data



def dashboard_two(request):
    df = None
    df_html = None        
    chart_bokeh_div = None
    chart_bokeh_script = None
    chart_mpl = None
    form  = ChartChooserForm()
    if request.method == 'POST':
        form = ChartChooserForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data['name']
            entry = DataEntry.objects.filter(name=entry).last()
            
            query = entry.query  # Assuming there's a query field in DataEntry  
            if query:
                # Database connection parameters
                db_params = {
                    'username': os.getenv('POSTGRES_USERNAME'),
                    'password': os.getenv('POSTGRES_PASSWORD'),
                    'host': os.getenv('POSTGRES_HOST'),
                    'port': os.getenv('POSTGRES_PORT'),
                    'database': os.getenv('POSTGRES_DBNAME')
                }

                # Create a connection string
                connection_string = f"postgresql+psycopg2://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

                # Create an engine and fetch data using the provided query
                engine = create_engine(connection_string)

                try:
                    df_temp = pd.read_sql(query, engine)  # Execute the query
                    df = pd.concat([df, df_temp], ignore_index=True)  # Combine results if multiple queries are executed
                    df_html = df.to_html(classes='table table-striped', index=False)
                    df.columns = [f'col{i+1}' for i in range(df.shape[1])]
                
                except Exception as e:
                    print(f"Error executing query: {e}")  # Handle exceptions appropriately

            if entry.chart_type:
                chart_type = entry.chart_type
                
                if chart_type == 'line':
                    chart_mpl = plot_matplotlib(df)  # Matplotlib for line charts
                elif chart_type == 'bar':
                    chart_bokeh_div, chart_bokeh_script = plot_bokeh(df)  # Bokeh for bar charts
        else:
            form = ChartChooserForm()

    return render(request, 'analyst/dashboard_two.html', {
        'form': form,
        'chart_mpl': chart_mpl,
        'chart_bokeh_div': chart_bokeh_div,
        'chart_bokeh_script': chart_bokeh_script,
        'dataframe': df_html
    })
    


def dashboard(request):
    chart_mpl = None
    chart_bokeh_div = None
    chart_bokeh_script = None
    df_html = None

    if request.method == 'POST':
        form = CombinedDataEntryForm(request.POST)

        if form.is_valid():
            # Save DataEntry instance
            entry = form.save()

            # Save associated CustomFieldValue using selected field and input value
            # custom_field_value = CustomFieldValue()
            # custom_field_value.content_object = entry  # Link to the newly created entry
            # custom_field_value.field = form.cleaned_data['field']  # Get the selected custom field
            # custom_field_value.value = form.cleaned_data['value']  # Get the value from the form
            # custom_field_value.save()

            # Initialize an empty DataFrame for results (if needed)
            df = pd.DataFrame()
            
            # Execute queries and generate plots based on user input
            query = entry.query  # Assuming there's a query field in DataEntry
            
            if query:
                # Database connection parameters
                db_params = {
                    'username': os.getenv('POSTGRES_USERNAME_ETL'),
                    'password': os.getenv('POSTGRES_PASSWORD_ETL'),
                    'host': os.getenv('POSTGRES_HOST_ETL'),
                    'port': os.getenv('POSTGRES_PORT_ETL'),
                    'database': os.getenv('POSTGRES_DBNAME_ETL')
                }

                # Create a connection string
                connection_string = f"postgresql+psycopg2://{db_params['username']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"

                # Create an engine and fetch data using the provided query
                engine = create_engine(connection_string)

                try:
                    df_temp = pd.read_sql(query, engine)  # Execute the query
                    df = pd.concat([df, df_temp], ignore_index=True)  # Combine results if multiple queries are executed
                    df_html = df.to_html(classes='table table-striped', index=False)
                    df.columns = [f'col{i+1}' for i in range(df.shape[1])]
                
                except Exception as e:
                    print(f"Error executing query: {e}")  # Handle exceptions appropriately

            # Generate plots based on chart type from the entry
            if entry.chart_type:
                chart_type = entry.chart_type
                
                if chart_type == 'line':
                    chart_mpl = plot_matplotlib(df)  # Matplotlib for line charts
                elif chart_type == 'bar':
                    chart_bokeh_div, chart_bokeh_script = plot_bokeh(df)  # Bokeh for bar charts

    else:
        form = CombinedDataEntryForm()

    return render(request, 'analyst/dashboard.html', {
        'form': form,
        'chart_mpl': chart_mpl,
        'chart_bokeh_div': chart_bokeh_div,
        'chart_bokeh_script': chart_bokeh_script,
        'dataframe': df_html
    })




def plot_matplotlib_bar(df):
    # Create a bar plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size if needed
    bars = ax.bar(df['col1'], df['col2'], color='skyblue')
    ax.set_title('Title', fontsize=16)
    ax.set_xlabel('Col1', fontsize=12)
    ax.set_ylabel('Col2', fontsize=12)

    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)
    ax.tick_params(axis='y', labelsize=10)

    # Add values on top of the bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # X-coordinate (center of the bar)
            height,  # Y-coordinate (top of the bar)
            f'{int(height)}',  # The value (formatted as integer)
            ha='center',  # Horizontal alignment
            va='bottom',  # Vertical alignment
            fontsize=10,  # Font size
            color='black'  # Text color
        )

    # Adjust layout to prevent clipping of x-axis labels
    fig.tight_layout()

    # Save it to a BytesIO object and encode it to base64 for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Ensure nothing gets cut off
    buf.seek(0)
    plt.close(fig)  # Close the figure to free memory
    return base64.b64encode(buf.getvalue()).decode()

def plot_matplotlib(df):
    # Create a line plot with Matplotlib from the DataFrame
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size if needed
    
    # Plot the line graph
    # ax.plot(df['col1'], df['col2'], marker='o', linestyle='-', color='skyblue', label='total outreach')
    columns = df.columns
    ax.plot(df[columns[0]], df[columns[1]], marker='o', linestyle='-', color='skyblue', label='total outreach')
    # Add labels on the line points
    for x, y in zip(df[columns[0]], df[columns[1]]):
        ax.text(
            x, y + 0.1,  # Position slightly above the point
            f'{int(y)}',  # Display the value as an integer
            ha='center', fontsize=10, color='black'
        )
    
    # Set titles and labels
    ax.set_title('Total Outreach', fontsize=16)
    ax.set_xlabel(columns[0], fontsize=12)
    ax.set_ylabel(columns[1], fontsize=12)
    
    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)
    
    # Add a legend
    ax.legend()
    
    # Adjust layout to prevent clipping of x-axis labels
    fig.tight_layout()
    
    # Save it to a BytesIO object and encode it to base64 for rendering in HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')  # Ensure nothing gets cut off
    buf.seek(0)
    plt.close(fig)  # Close the figure to free memory
    return base64.b64encode(buf.getvalue()).decode()


def plot_bokeh(df):
    # Create a ColumnDataSource for the data
    # source = ColumnDataSource(data=dict(col1=df['col1'].tolist(), col2=df['col2'].tolist()))
    columns = df.columns
    source = ColumnDataSource(data=dict(col1=df[columns[0]].astype(str).tolist(), col2=df[columns[1]].tolist()))


    # Create the Bokeh plot
    p = figure(
        title="Total outreach", 
        x_axis_label=columns[0], 
        y_axis_label=columns[1], 
        x_range=[str(x)for x in df[columns[0]].tolist()], 
        y_range=(0, df[columns[1]].max() + 5), 
        width=800, 
        height=400
    )

    # Add bars to the plot
    p.vbar(x='col1', top='col2', width=0.9, source=source, color="skyblue")

    # Add labels on top of the bars
    labels = LabelSet(
        x='col1', 
        y='col2', 
        text='col2', 
        level='glyph', 
        x_offset=-13,  # Adjust for better alignment
        y_offset=3,  # Slightly above the bar
        source=source, 
        text_font_size="10pt", 
        text_color="black"
    )
    p.add_layout(labels)

    # Generate script and div for embedding in HTML template
    script, div = components(p)
    return div,script
    
    # return div, script