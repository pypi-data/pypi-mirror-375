import os
import json
import yaml
import logging
import pandas as pd
import random
import requests

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Q
from .models import SimpleHttpOperatorModel, WorkflowModel, Endpoint, CustomFieldValue, CustomField, DagModel,HttpOperatorConnectionModel,Account, Message, OutSourced, StatusCheck, Thread, UnwantedAccount
from django.conf import settings

from api.helpers.dag_generator import generate_dag
from django_tenants.utils import schema_context
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework.response import Response
from api.outreaches.serializers import PeriodicTaskGetSerializer
from api.outreaches.serializers import PeriodicTaskPostSerializer
from api.sales_rep.models import SalesRep
from rest_framework import status
from hikerapi import Client, AsyncClient
from datetime import datetime, timedelta
from celery import shared_task

@schema_context(os.getenv('SCHEMA_NAME'))
def assign_salesrep(account):
    salesrep = None
    try:
        available_sales_reps = SalesRep.objects.filter(available=True)
        random_salesrep_index = random.randint(0,len(available_sales_reps)-1)
        available_sales_reps[random_salesrep_index].instagram.add(account)
        salesrep = available_sales_reps[random_salesrep_index]
    except Exception as err:
        print(err)
    return salesrep


@schema_context(os.getenv('SCHEMA_NAME'))
def get_account(usernames=None):
    """
    Recursively iterates through a list of usernames to find a suitable account.
    If no usernames are provided, it fetches the qualified usernames internally.

    Args:
        usernames (list, optional): A list of usernames to check. Defaults to None.

    Returns:
        Account or None: An Account object if found, otherwise None.
    """
    yesterday = timezone.now().date() - timezone.timedelta(days=1)
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
    unwanted_usernames = UnwantedAccount.objects.values_list('username', flat=True)

    # Filter accounts that are qualified and created from yesterday onwards, and exclude accounts that are not wanted
    accounts = Account.objects.filter(
        Q(qualified=True) & Q(created_at__gte=yesterday_start) & Q(created_at__lte=tomorrow)
    ).exclude(
        status__name="sent_compliment"
    ).exclude(
        igname__in=unwanted_usernames
    ).filter(dormant_profile_created=True)

    usernames_list = list(accounts.values_list('igname', flat=True))
    if usernames is None or usernames not in usernames_list:
        # Fetch qualified usernames internally
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        unwanted_usernames = UnwantedAccount.objects.values_list('username', flat=True)

        # Filter accounts that are qualified and created from yesterday onwards, and exclude accounts that are not wanted
        accounts = Account.objects.filter(
            Q(qualified=True) & Q(created_at__gte=yesterday_start) & Q(created_at__lte=tomorrow)
        ).exclude(
            status__name="sent_compliment"
        ).exclude(
            igname__in=unwanted_usernames
        ).filter(dormant_profile_created=True)

        usernames = list(accounts.values_list('igname', flat=True))
        random.shuffle(usernames)  # Shuffle the usernames to randomize the selection

    if not usernames:
        return None  # Base case: no usernames left to check


    username = usernames.pop(0)  # Get the first username from the list

    # Check if the username is unwanted
    check_unwanted = UnwantedAccount.objects.filter(username__icontains=username.split('-')[0])
    if check_unwanted.exists():
        # Skip this username and recurse with the remaining list
        return get_account(usernames)

    try:
        accounts = Account.objects.filter(igname__icontains=username.split('-')[0]).exclude(status__name='sent_compliment')
        if accounts.exists():
            account = accounts.latest('created_at')
            if not account.salesrep_set.exists():
                assign_salesrep(account)
            return account
        else:
            # No account found for this username, recurse with remaining usernames
            return get_account(usernames)

    except Exception as error:
        print(f"Error processing username {username}: {error}")
        # On error, recurse with remaining usernames
        return get_account(usernames)


# @schema_context(os.getenv('SCHEMA_NAME'))
# def get_account(username):
#     account = None
#     check_unwanted = UnwantedAccount.objects.filter(username__icontains=''.join(username).split('-')[0])
#     if check_unwanted.exists():
#         return 
#     try:
#         accounts = Account.objects.filter(igname__icontains=''.join(username).split('-')[0]).exclude(status__name='sent_compliment') 
#         account = accounts.latest('created_at')
#         if account.salesrep_set.exists():
#             account = account
#         else:
#             assign_salesrep(account)
            

#     except Exception as error:
#         print(error)

#     # if account is None:
#     #     get_account(username)
#     return account

@schema_context(os.getenv('SCHEMA_NAME'))
def get_account_for_salesrep(username):
    account = None
    try:
        accounts = Account.objects.filter(igname__icontains=''.join(username).split('-')[0])
        account = accounts.latest('created_at')
        if account.salesrep_set.exists():
            account = account
        else:
            assign_salesrep(account)
            

    except Exception as error:
        print(error)
    return account

@schema_context(os.getenv('SCHEMA_NAME'))
def get_sales_rep_for_account(username):
    salesrep = None
    username = username
    account = get_account_for_salesrep(username)
    if account:
        if account.salesrep_set.exists():
            salesrep = account.salesrep_set.latest('created_at')
        
    return salesrep

@schema_context(os.getenv('SCHEMA_NAME'))
def lead_is_for_salesrep(username, salesrep_to_check):
    ret = False
    account_salesrep = get_sales_rep_for_account(username)
    account_sales_rep_igname = account_salesrep.ig_username

    if account_sales_rep_igname == salesrep_to_check:
        ret = True 
    return ret


@schema_context(os.getenv('SCHEMA_NAME'))
def tasks_by_sales_rep(task_name, sales_rep, task_status="any", order=1, number=-1, ret_tasks = False):
    tasks = PeriodicTask.objects.filter(task=task_name).order_by('start_time')

    if task_status == "enabled":
        tasks = tasks.filter(enabled=True)
    elif task_status == "disabled":
        tasks = tasks.filter(enabled=False)
    
    if order == -1:
        tasks = tasks.reverse()

    populated_tasks = []
    count = 0

    task_objs = []

    for task in tasks:
        lead_user_name = task.name.replace("SendFirstCompliment-", "")
        if lead_is_for_salesrep(lead_user_name, sales_rep):
            # any status
            serializer = PeriodicTaskGetSerializer(task)
            serialized_task = serializer.data
            # Populate object to return
            populated_task = {
                'task': serialized_task,
                'sales_rep': sales_rep,
            }
            populated_tasks.append(populated_task)
            task_objs.append(task)
            count += 1
            if number != -1 and count == number:
                break
    if ret_tasks:
        return task_objs
    return Response({'tasks': populated_tasks}, status=status.HTTP_200_OK)



@schema_context(os.getenv('SCHEMA_NAME'))
def generate_time_slots(start_datetime, end_datetime, interval):
    start = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M")
    time_slots = []

    while start <= end:
        time_slots.append(start)
        start += timedelta(minutes=interval)

    return time_slots


def get_token():
    try:
        response = requests.post("https://api.thecut.co/v1/auth/token", headers={
            "Authorization": "Basic YzgwMWE2NmEtNDJlMC00ZTZhLThiZTMtOTIwYzExNWY4NWJkOjU1NTM0MTFjLWIxNjMtNDYyNi1iYWU2LTk2YTczMjMzNzMyMQ==",
            "Auth-Client-Version": "1.25.1",
            "Device-Name": "Tm9raWEgQzMy",
            "Installation-Id": "17E229B5-41B7-4F4D-B44A-C76559665E54",
            "Device-Operating-System": "TIRAMISU (33)",
            "Device-Model": "Nokia Nokia C32",
            "Auth-Client-Name": "android-app",
            "Device-Fingerprint": "3a3f05ba6c66de6a",
            "Device-Platform": "android",
            "Signature": "v1 MTcwODMyNTg5NjpKSjltTUVSZjNmMXhtMUNLWHEzOHR1U0RUdDQxQmNpYTo4V09jZTUrS0dNa21ZR0doSGNmbmlxVlR1R0RFbmZIUkRSd1h0RXJua0FzPQ==",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": "77",
            "Host": "api.thecut.co",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.11.0"
        }, json={
            "grant_type": "password",
            "username": "surgbc@gmail.com",
            "password": "ca!kacut"
        })
        data = response.json()
        return data["access_token"]
    except Exception as e:
        print("Error fetching access token:", e)
        raise e

def get_the_cut_info(thecut_username):
    access_token = get_token()
    response = requests.get(f"https://api.thecut.co/v2/barbers/{thecut_username}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Auth-Client-Version": "1.25.1",
        "Device-Name": "Tm9raWEgQzMy",
        "Installation-Id": "17E229B5-41B7-4F4D-B44A-C76559665E54",
        "Device-Operating-System": "TIRAMISU (33)",
        "Device-Model": "Nokia Nokia C32",
        "Auth-Client-Name": "android-app",
        "Device-Fingerprint": "3a3f05ba6c66de6a",
        "Session-Id": "f822af9b4e3a61e0d5b71eacbca9c5a686fba9d2b968792e729a6138f4fde7e8122528f7230406f75ed335f6b822c732",
        "Device-Platform": "android",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Id": "65d2df444fd2435e639c4b43",
        "Signature": "v1 MTcwODMzNTg5NzprTFVKNmxjNFpiUzU4aXdUTFFsTENWQTFWNUlGSVFLMDpLQlhiand2bVpCeFppZmZieGFtYnd5bzh6aWp3c3FpSUU4ZHd6azViRHRrPQ=="
    })
    return response.json()


def combine_dicts(group):
    combined_dict = {}
    for _, row in group.iterrows():
        combined_dict.update(row.dropna().to_dict())
    return combined_dict


def merge_lists_by_timestamp(dict_list):
    df = pd.DataFrame(dict_list)
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Round the created_at values to the nearest minute
    df['created_at'] = df['created_at'].dt.round('min')
    return df.groupby('created_at').apply(combine_dicts).tolist()



def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if not parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flatten_dict_list(dict_list, parent_key='', sep='_'):
    items = []
    for d in dict_list:
        if isinstance(d, dict):
            items.extend(flatten_dict(d, parent_key, sep=sep).items())
        else:
            items.append((parent_key, d))
    return dict(items)

def remove_timestamp(dict_):
    if "_created_at" in dict_:
        try:
            del dict_['_created_at']
        except Exception as err:
            print(err)
    return dict_


@shared_task()
@schema_context(os.getenv('SCHEMA_NAME'))
def generate_dag_script(workflow_id):
    # if "trigger_url" in dag_data:
        
    #     data = {
    #         "dag":[entry for entry in DagModel.objects.filter(id = workflow.dag.id).values()],
    #         "operators":[entry for entry in workflow.simplehttpoperators.values()],
    #         "data_seconds":workflow.delay_durations,
    #         "trigger_url":dag_data.get("trigger_url"),
    #         "trigger_url_expected_response":dag_data.get("trigger_url_expected_response")
    #     }
    # else:
    workflow = WorkflowModel.objects.get(id=workflow_id)
    print(workflow.workflow_type)
    print(workflow)
    dag_ = DagModel.objects.filter(workflow__id = workflow.id)
    dag = dag_.latest('created_at')
    print(dag.dag_id)
    operators = [entry for entry in dag.simplehttpoperatormodel_set.filter().values()]
    data_points = []
    for operator in operators:
        try:
            print(operator['connection_id'])
            operator['http_conn_id'] = HttpOperatorConnectionModel.objects.get(id=operator['connection_id']).connection_id
            endpoint = Endpoint.objects.get(id=operator['endpointurl_id'])
            operator['endpoint'] = endpoint.url
            operator['method'] = endpoint.method
            # Get the content type for the Endpoint model
            endpoint_content_type = ContentType.objects.get_for_model(Endpoint)
            # Query to get all custom fields and their values for the given end
            custom_fields_with_value = CustomFieldValue.objects.filter(
                content_type=endpoint_content_type,
                object_id=endpoint.id
            ).select_related('field')

            for custom_field_value in custom_fields_with_value:
                data_points.append({
                    custom_field_value.field.name: custom_field_value.value,
                    "created_at": custom_field_value.created_at
                })

            operator['data'] = remove_timestamp(flatten_dict_list(merge_lists_by_timestamp(data_points)))
            
        except Exception as error:
            print(str(error))

    dags = [entry for entry in dag_.values()]
    for x in dags:
        x['http_conn_id'] = HttpOperatorConnectionModel.objects.get(id=x['connection_id']).connection_id

    data = {
        "dag":dags,
        "operators":operators,
        "data_seconds":[str(workflow.delay_durations)]
    }

    print(dag.dag_id)
    # print(data)
    # Write the dictionary to a YAML file
    yaml_file_path = os.path.join(settings.BASE_DIR, 'api', 'helpers', 'include', 'dag_configs', f"{dag.dag_id}_config.yaml")
    with open(yaml_file_path, 'w') as yaml_file:
        try:
            yaml.dump(data, yaml_file, default_flow_style=False)
        except Exception as error:
            print(str(error))

    try:
        generate_dag(workflow_type=workflow.workflow_type)
    except Exception as error:
        print(str(error))


def dag_fields_to_exclude():
    return [
            "id",
            "timetable",
            "start_date",
            "end_date",
            "full_filepath",
            "template_searchpath",
            "template_undefined",
            "user_defined_macros",
            "user_defined_filters",
            "default_args",
            "concurrency",
            "max_active_tasks",
            "max_active_runs",
            "dagrun_timeout",
            "sla_miss_callback",
            "default_view",
            "orientation",
            "catchup",
            "on_success_callback",
            "on_failure_callback",
            "doc_md",
            "params",
            "access_control",
            "is_paused_upon_creation",
            "jinja_environment_kwargs",
            "render_template_as_native_obj",
            "tags",
            "owner_links",
            "auto_register",
            "fail_stop",
            "trigger_url_expected_response",
            "workflow",
        ]



def initialize_hikerapi_client(is_async=False):
    
    if is_async:
        try:
            client = AsyncClient(
                token=os.getenv('HIKER_API_KEY'),
            )
            return client
        except Exception as e:
            logging.warning("Error initializing Hiker API async client:", e)
            return None
    else:
        try:
            client = Client(
                token=os.getenv('HIKER_API_KEY'),
            )
            return client
        except Exception as e:
            logging.warning("Error initializing Hiker API client:", e)
            return None
