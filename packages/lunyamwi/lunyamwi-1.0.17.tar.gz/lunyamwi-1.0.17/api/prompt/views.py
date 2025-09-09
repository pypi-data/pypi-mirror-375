import json
from django.shortcuts import render
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from django_tenants.utils import schema_context

from django.shortcuts import redirect, get_object_or_404
from api.instagram.models import Account
from .serializers import CreatePromptSerializer, CreateRoleSerializer, PromptSerializer, RoleSerializer,RunDataSerializer
from .factory import PromptFactory
from .models import Prompt, Role, ChatHistory
from .forms import PromptForm
import os
import openai
import base64
import time
import random
import uuid
import logging
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from dotenv import load_dotenv, find_dotenv
from langchain.tools import tool
import requests
import re
import wandb
from typing import Dict, Any, Type,Union
from pydantic import BaseModel, Field
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.schema.runnable import RunnableMap
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.agents import AgentExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from .constants import MSSQL_AGENT_FORMAT_INSTRUCTIONS,MSSQL_AGENT_PREFIX


from crewai_tools import BaseTool
#from crewai_tools import tool
from crewai import Agent, Task, Crew, Process,LLM
from django.core.mail import send_mail
# from api.instagram.tasks import send_logs
from .models import Agent as AgentModel,Task as TaskModel,Tool, Department
import os
from typing import List,Optional
from crewai.flow.flow import Flow, and_, listen, start
import asyncio
import inspect


openai_api_key = os.getenv('OPENAI_API_KEY')
os.environ["OPENAI_MODEL_NAME"] = 'gpt-4-1106-preview'
os.environ["SERPER_API_KEY"] = os.getenv('SERPER_API_KEY')
db_url = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}"
print(db_url)

def index(request):
    # with schema_context(os.getenv("SCHEMA_NAME")):
    prompts = Prompt.objects.all()
    return render(request, 'prompt/index.html', {'prompts': prompts})


def add(request):
    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('prompt_index')
    else:
        form = PromptForm()
    return render(request, 'prompt/add.html', {'form': form})


def detail(request, prompt_id):
    prompt = get_object_or_404(Prompt, id=prompt_id)

    return render(request, 'prompt/detail.html', {
        'prompt': prompt,
    })


def update(request, prompt_id):
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    if request.method == 'POST':
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            return redirect('prompt_index')
    else:
        form = PromptForm(instance=prompt)
    return render(request, 'prompt/update.html', {'form': form, 'prompt': prompt})


def delete(request, prompt_id):
    prompt = get_object_or_404(Prompt, pk=prompt_id)
    prompt.delete()
    return redirect('prompt_index')


class saveResponse(APIView):

    def post(self, request):

        return Response({
            "success": True,
        }, status=status.HTTP_200_OK)

def retrieve_prompt(userInput):
    resp = requests.get("https://promptemplate.booksy.us.boostedchat.com/prompts/")
    prompts = [prompt['text_data'] for prompt in resp.json()]
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=1000,
        chunk_overlap=0
    )
    character_split_texts = character_splitter.split_text('\n\n'.join(prompts))
    token_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0, tokens_per_chunk=256)

    token_split_texts = []
    for text in character_split_texts:
        token_split_texts += token_splitter.split_text(text)

    embedding_function = SentenceTransformerEmbeddingFunction()
    chroma_client = chromadb.Client()
    chroma_collection = chroma_client.create_collection(f"prompts-{random.randint(1,1000)}", embedding_function=embedding_function)

    ids = [str(i) for i in range(len(token_split_texts))]

    chroma_collection.add(ids=ids, documents=token_split_texts)
    chroma_collection.count()
    results = chroma_collection.query(query_texts=[userInput], n_results=5)
    retrieved_documents = results['documents'][0]
    return retrieved_documents

def model_with_extra_info(data):
    template = """Answer the user based only on the following context and information and remember to conceal your identity as a robot, you are a sales representative:
            {context}
        information: {information}
        userInput: {userInput}
        """
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatOpenAI(temperature=0)
    output_parser = StrOutputParser()
    chain = RunnableMap({
        "context": lambda x: retrieve_prompt(x["userInput"]),
        "userInput": lambda x: x["userInput"],
        "information": lambda x: x["information"]
    }) | prompt | model | output_parser
    result = chain.invoke(data)
    get_prompt = RunnableMap({
        "context": lambda x: retrieve_prompt(x["userInput"]),
        "userInput": lambda x: x["userInput"],
        "information": lambda x: x["information"]
    }) | prompt
    return {
        "result":result,
        "prompt":get_prompt.invoke(data),
        "model":model
    }

import string

def remove_punctuation(sentence):
    punctuation_to_keep = {'.', ',', '\''}
    punctuation_to_remove = ''.join(p for p in string.punctuation if p not in punctuation_to_keep) + '{}[]'
    table = str.maketrans('', '', punctuation_to_remove)
    return sentence.translate(table)

import sqlite3

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()
def save_message(role, content):
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role, content FROM chat_history')
    messages = cursor.fetchall()
    conn.close()
    return messages

@tool
def get_sales_representative_data(userInput):
    """this function returns the sales representative data and information about their role"""
    resp = requests.get("https://promptemplate.booksy.us.boostedchat.com/roles/-NmvqgR8ySgPtYKXiQ1c/")
    result = model_with_extra_info({"userInput":userInput,"information":resp.json()['description']})
    return result['result']

class generateResponse(APIView):
    def post(self, request):
        userInput = request.data.get("userInput")
        username_from_id = request.data.get("username_from_id","")
        username_to_id = request.data.get("username_to_id","")
        tools = [get_sales_representative_data]
        functions = [convert_to_openai_function(f) for f in tools]
        # model_with_extra_info = ChatOpenAI(temperature=0).bind(functions=functions)
        
        # Load existing conversation history
        chat_history = ChatHistory.objects.filter(Q(username_from_id=username_from_id)&Q(username_to_id=username_to_id))
        print(chat_history)
        
        # Initialize memory
        memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

        # Add loaded messages to memory
        for chat in chat_history:
            if chat.role == 'user':
                memory.chat_memory.add_user_message(chat.content)
            elif chat.role == 'assistant':
                memory.chat_memory.add_ai_message(chat.content)

        # Construct the initial result with extra information
        result = model_with_extra_info({"userInput": userInput, "information": "Conceal your identity as a robot, you are a sales representative"})
        print(result)
        
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", remove_punctuation(result['prompt'].messages[0].content)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{userInput}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # Create the chain
        model = ChatOpenAI(temperature=0).bind(functions=functions)
        
        chain = RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
        ) | final_prompt | model | OpenAIFunctionsAgentOutputParser()
        
        # Create the agent executor with memory integration
        qa = AgentExecutor(agent=chain, tools=tools, verbose=False, memory=memory)
        
        # Invoke the chain and get the response
        response = qa.invoke({"userInput": userInput})
        
        # Save user input and AI response to SQLite
        ChatHistory.objects.create(role='user', content=userInput,username_from_id=username_from_id,username_to_id=username_to_id)
        ChatHistory.objects.create(role='assistant',content= response['output'],username_from_id=username_from_id,username_to_id=username_to_id)
        
        # Save the updated memory context
        memory.save_context({"input": userInput}, {"output": response['output']})
        
        return Response({
            "response": response
        }, status=status.HTTP_200_OK)



class ScrappingTheCutTool(BaseTool):
    name: str = "scrapping_thecut_tool"
    description: str = """Allows one to be able to scrap from the cut effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapTheCut/"


    def _run(self,number_of_leads):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "record":None,
            "refresh":False,
            "number_of_leads":number_of_leads
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class InstagramSearchingUserTool(BaseTool):
    name: str = "search_instagram_tool"
    description: str = """Allows one to be able to scrap from instagram effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapUsers/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "query":None
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class InstagramScrapingProfileTool(BaseTool):
    name: str = "scrapping_instagram_profile_tool"
    description: str = """Allows one to be able to scrap from instagram effectively either,
                        per single or multiple records"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/scrapInfo/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134,
            "index":0,
            "delay_before_requests":18,
            "delay_after_requests":4,
            "step":3,
            "accounts":18,
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()

class LeadScreeningTool(BaseTool):
    name: str = "fetch_leads"
    description: str = """Allows one to be able to fetch sorted leads that meet certain
                        criterion"""
    
    def _run(self,question,**kwargs):
        # import pdb;pdb.set_trace()
        db = SQLDatabase.from_uri(db_url)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", 
                                        verbose=True,prefix=MSSQL_AGENT_PREFIX, 
                                        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS)

        result = agent_executor.invoke(question)
        return Response({"message":result.get("output","")},status=status.HTTP_200_OK)
        

class FetchLeadTool(BaseTool):
    name: str = "fetch_lead"
    description: str = """Allows one to be able to fetch a lead that meet certain
                        criterion"""
    # number_of_leads: Optional[str] = None
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/getAccount/"

    def _run(self,**kwargs):
        # import pdb;pdb.set_trace()
        headers = {"Content-Type": "application/json"}
        payload = {
            "chain":True,
            "round":134
        }
        # import pdb;pdb.set_trace()
        response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
        return response.json()


class SlackTool(BaseTool):
    name: str = "slack_tool"
    description: str = """This tool triggers slacks message"""

    def _run(self, message, **kwargs):
        # send the message to the following email -- chat-quality-aaaamvba2tskkthmspu2nrq5bu@boostedchat.slack.com
        db = SQLDatabase.from_uri(db_url)

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", 
                                        verbose=True,prefix=MSSQL_AGENT_PREFIX, 
                                        format_instructions=MSSQL_AGENT_FORMAT_INSTRUCTIONS)

        result = agent_executor.invoke(message)
        send_mail(subject="Scrapping Monitoring Agent Summary",message=result.get("output",""),from_email="lutherlunyamwi@gmail.com",recipient_list=["chat-quality-aaaamvba2tskkthmspu2nrq5bu@boostedchat.slack.com"])
        return Response({"message":result.get("output","")},status=status.HTTP_200_OK)

class AssignSalesRepTool(BaseTool):
    name: str = "assign_sales_rep_tool"
    description: str = """This tool will assign a lead to a salesrepresentative"""

    endpoint: str = "https://api.booksy.us.boostedchat.com/v1/sales/assign-salesrep/"

    def _run(self,**kwargs):
        headers = {"Content-Type": "application/json"}
        payload = {"username": ""}
        try:
            response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


class AssignInfluencerTool(BaseTool):
    name: str = "assign_influencer_tool"
    description: str = """This tool will assign a lead to an influencer"""

    endpoint: str = "https://api.booksy.us.boostedchat.com/v1/sales/assign-influencer/"

    def _run(self,**kwargs):
        headers = {"Content-Type": "application/json"}
        payload = {"username": ""}
        try:
            response = requests.post(self.endpoint, data=json.dumps(payload), headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"This error is because there is an issue with the endpoint and this is the issue:{str(e)}")
            return {"error": str(e)}


class FetchDirectPendingInboxTool(BaseTool):
    name: str = "fetch_pending_inbox_tool"
    description: str = ("Allows fetching of inbox pending requests in instagram")
    endpoint: str = "https://mqtt.booksy.us.boostedchat.com"


    def extract_inbox_data(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        
        threads = data
        result = []

        for thread in threads:
            users = thread.get('users', [])
            for user in users:
                username = user.get('username')
                thread_id = thread.get('thread_id')
                items = thread.get('items', [])

                for item in items:
                    item_id = item.get('item_id')
                    user_id = item.get('user_id')
                    item_type = item.get('item_type')
                    timestamp = item.get('timestamp')
                    message = item.get('text')

                    data_dict = {
                        'username': username,
                        'item_id': item_id,
                        'user_id': user_id,
                        'item_type': item_type,
                        'timestamp': timestamp,
                        'round': 1908,
                        'pending': True,
                        'info': {**user}
                    }

                    # Save the lead information to the lead database - scrapping microservice
                    response = requests.post(
                        "https://scrapper.booksy.us.boostedchat.com/instagram/instagramLead/",
                        headers=headers,
                        data=json.dumps(data_dict)
                    )
                    if response.status_code in [200, 201]:
                        print("right track")

                    if item_type == 'text':
                        # Save the message
                        # Create an account for it/ also equally save outsourced info for it
                        account_dict = {

                            "igname": username
                        }
                        # Save account data
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/account/",
                            headers=headers,
                            data=json.dumps(account_dict)
                        )
                        account = response.json()
                        # Save outsourced data
                        outsourced_dict = {
                            "results": {
                                **user
                            },
                            "source": "instagram"
                        }
                        response = requests.post(
                            f"https://api.booksy.us.boostedchat.com/v1/instagram/account/{account['id']}/add-outsourced/",
                            headers=headers,
                            data=json.dumps(outsourced_dict)
                        )
                        # Create a thread and store the message
                        data_dict['thread_id'] = thread_id
                        data_dict['message'] = message
                        
                        thread_dict = {
                            "thread_id": thread_id,
                            "account_id": account['id'],
                            "unread_message_count": 0,
                            "last_message_content": message,
                            "last_message_at": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/dm/create-with-account/",
                            headers=headers,
                            data=json.dumps(thread_dict)
                        )

                        thread_pk = response.json()['id']

                        # Save the message in the thread
                        message_dict = {
                            "content": message,
                            "sent_by": "Client",
                            "thread": thread_pk,
                            "sent_on": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/message/",
                            headers=headers,
                            data=json.dumps(message_dict)
                        )
                    
                    result.append(data_dict)

        return result



    def _run(self, **kwargs):

        # Set the username for which to fetch the pending inbox
        username = 'barbersince98'
        
        # Send a POST request to the fetchPendingInbox endpoint
        response = requests.post(f'{self.endpoint}/fetchPendingInbox', json={'username_from': username})
        
        # Check the status code of the response
        if response.status_code == 200:
            # Print the response JSON
            print("all is well")
            print(json.dumps(response.json(), indent=2))
            inbox_data = response.json()
            inbox_dataset = self.extract_inbox_data(inbox_data)
            print(inbox_dataset)
            
        else:
            print(f'Request failed with status code {response.status_code}')
        return response.json()

class ApproveRequestTool(BaseTool):  
    name: str = "approve_request_tol"
    description: str = ("Allows approval of requests from pending requests in instagram")
    endpoint: str = "https://mqtt.booksy.us.boostedchat.com"

    def _run(self, username, thread_id, **kwargs):
        # Send a POST request to the approve endpoint
        username = username
        thread_id = thread_id
        response = requests.post(f'{self.endpoint}/approve', json={'username_from': username,'thread_id':thread_id})
        
        # Check the status code of the response
        if response.status_code == 200:
            print('Request approved')
        else:
            print(f'Request failed with status code {response.status_code}')
        return response.json()
    

class LeadQualifierArgs(BaseModel):
    input_text: str = Field(..., description="The text to process")
    threshold: int = Field(10, description="A threshold value for processing")
    username: str = Field(..., description="The username of the lead")
    qualify_flag: bool = Field(..., description="A boolean flag to qualify lead set to true/false")
    relevant_information:Dict[str, Any] = Field(..., description="A dictionary/json containing the relevant information about the lead that is needed")

#class LeadQualifierTool(BaseTool):
class LeadQualifierTool():
    #args_schema: Type[BaseModel] = LeadQualifierArgs
    name: str = "lead_qualify_tool"
    description: str = ("Switches the qualifying flag to true for qualified leads and false to unqualified leads")
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"

@tool
#def lead_qualify_tool(*args,**kwargs):
def lead_qualify_tool(payload):
        """
Switches the qualifying flag to true for qualified leads and false to unqualified leads.

:param payload: dict, a dictionary containing the following keys:

    username: str, the username of the lead
    qualify_flag: bool, a True/False flag showing if user is qualified or not
    relevant_information: dict, a dictionary containing additional information about the lead. The dictionary can contain the following keys:

        most_probable_name: str, the most probable name of the lead
        most_probable_country_and_location: list of str, the most probable country and location of the lead
        most_probable_venue/salon/barbershop&their_role: list of str, the most probable venue, salon, barbershop, and the lead's role
        what_to_compliment_in_a_lead: list of str, what to compliment in the lead
        other_relevant_insights: list of str, other relevant insights about the lead
        persona: str, the persona of the lead
        outreach_tactic: str, the outreach tactic for the lead

example payload:
{
    "username": "tombarber",
    "qualify_flag": True,
    "relevant_information": {
        "most_probable_name": "Jimmy",
        "most_probable_country_and_location": ["USA", "Miami"],
        "most_probable_venue/salon/barbershop&their_role": ["Top Barber Jimmy", "Owner/Barber"],
        "what_to_compliment_in_a_lead": ["Dedication to craft", "Unique styling", "Positive customer reviews"],
        "other_relevant_insights": ["Fully booked on weekends", "Available slots on weekdays", "Occasional last-minute cancellations", "Active engagement on social media platforms"],
        "persona": "Top-tier Barber",
        "outreach_tactic": "Personalized compliment on dedication and unique styling, highlighting collaboration opportunities on weekdays and promoting tools/products for top-tier barbers."
    }
}
        """
        endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"
        print(payload)
        payload = json.dumps(payload)
        print(json.loads(payload)['relevant_information'])
        outbound_qualifying_data={
            "username": json.loads(payload)['username'],
            "qualify_flag": json.loads(payload)['qualify_flag'],
            "relevant_information": json.dumps(json.loads(payload)['relevant_information']),
            "scraped":True
        }
        response = requests.post("https://scrapper.booksy.us.boostedchat.com/instagram/instagramLead/qualify-account/",data=outbound_qualifying_data)
        if response.status_code in [200,201]:
            print("good")
        # inbound qualifying
        inbound_qualify_data = {
            "username": json.loads(payload)['username'],
            "qualify_flag": json.loads(payload)['qualify_flag'],
            "relevant_information": json.dumps(json.loads(payload)['relevant_information']),
            "scraped":True
        }
        response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/qualify-account/",data=inbound_qualify_data)
        if response.status_code in [200,201]:
            print("best")
        return

class HumanTakeOverTool(BaseTool):
    name: str = "human_takeover_tool"
    description: str = ("Perform a human takeover when the respondent feels that they are conversing with a robot")
    
    def _run(self, username:str, **kwargs):
        data = {
            "username":username,
            "assigned_to": "Human"
        }
        response = requests.post(f"https://api.booksy.us.boostedchat.com/v1/instagram/fallback/{username}/assign-operator/",data=data)
        if response.status_code in [201,200]:
            print(response)
        return "assigned to human"


class WorkflowTool(BaseTool):
    name: str = "workflow_tool"
    description: str = ("Allows the composition of workflows "
         "in order to create as many workflows as possible")
    endpoint: str = "https://scrapper.booksy.us.boostedchat.com/instagram/workflows/"

    def _run(self, workflow_data: dict, **kwargs) -> str:
        print('==========here is workflow data==========')
        print(workflow_data)
        print('==========here is workflow data==========')
        """
        Sends a POST request to the specified endpoint with the provided workflow data and API key.
        """
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(self.endpoint, data=json.dumps(workflow_data), headers=headers)
        print('we are here------------',response)
        if response.status_code not in [200,201]:
            raise ValueError(f"Failed to send workflow data: {response.text}")

        return response.status_code

    
    

TOOLS = {
    "workflow_tool" : WorkflowTool(),
    "scrapping_thecut_tool" : ScrappingTheCutTool(),
    "fetch_lead_tool":FetchLeadTool(),
    "lead_screening_tool":LeadScreeningTool(),
    "search_instagram_tool":InstagramSearchingUserTool(),
    "instagram_profile_tool":InstagramScrapingProfileTool(),
    "slack_tool":SlackTool(),
    "assign_salesrep_tool":AssignSalesRepTool(),
    "assign_influencer_tool":AssignInfluencerTool(),
    "fetch_pending_inbox_tool":FetchDirectPendingInboxTool(),
    "approve_requests_tool":ApproveRequestTool(),
    "qualifying_tool":lead_qualify_tool,
    "human_takeover_tool":HumanTakeOverTool()

}

class GeneratedTextOutput(BaseModel):
    text: Optional[str] = ""
    active_stage: Optional[str] = ""
    confirmed_problems: Optional[str] = ""
    human_takeover: Optional[bool] = False


def remove_duplicate_content_keys(json_string: str) -> dict:
    """
    Parses a JSON string, removes duplicate "content" keys, and returns a dictionary.
    """
    try:
        data = json.loads(json_string)
        if "content" in data and isinstance(data["content"], str):
            data["content"] = [data["content"]]
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {"success":False}
    
def clean_json_output(raw_output: str) -> dict:
    """
    Parses a raw JSON string and ensures 'content' is a list.
    If 'content' is a string, it converts it into a list.
    """
    try:
        # Extract JSON from raw output (if wrapped in additional text)
        start_index = raw_output.find("{")
        end_index = raw_output.rfind("}")
        if start_index == -1 or end_index == -1:
            raise ValueError("Invalid JSON structure in raw output")

        json_string = raw_output[start_index:end_index + 1]
        data = json.loads(json_string)

        # Check if 'content' exists and is a string; convert to list if so
        if "content" in data:
            if isinstance(data["content"], str):
                data["content"] = [data["content"]]  # Convert string to list

        return data

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error decoding or cleaning JSON: {e}")
        return {}

class PrequalifyingOutput(BaseModel):
   prequalified: Optional[bool] = None
   name: Optional[str] = None
   media_details: Optional[List[str]] = None 
   strengths: Optional[Union[str, List[str]]] = None
   biography: Optional[str] = None
   area: Optional[str] = None
   contact_details: Optional[Union[dict, str]] = None
   external_url: Optional[str] = None
   desired_provider: Optional[bool] = None
   desired_size: Optional[bool] = None
   desired_location: Optional[bool] = None
   desired_category: Optional[bool] = None
   desired_visibility: Optional[bool] = None
   desired_activity: Optional[bool] = None
   lead_score: Optional[Union[int,str]] = None

OUTPUT_MODELS = {
    "GeneratedTextOutput": GeneratedTextOutput,
    "PrequalifiedTextOutput": PrequalifyingOutput
}

class WandbLoggingHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        wandb.log({"langchain_log": log_entry})





department = "Qualifying Department"
null = None
false, true = False, True

class PrequalifyingWorkflow(Flow):
   
   
   def __init__(self, agents, tasks, inputs):
      super().__init__()
      self.agents = agents
      self.tasks = tasks
      self.inputs = inputs
      self.headers = {"Content-Type": "application/json"}


   def clean_json_output(self, raw_output: str) -> dict:
      """
      Parses a raw JSON string and ensures 'content' is a list.
      If 'content' is a string, it converts it into a list.
      Handles nested JSON structures recursively.
      """
      try:
         # Extract JSON from raw output (if wrapped in additional text)
         start_index = raw_output.find("{")
         end_index = raw_output.rfind("}")
         if start_index == -1 or end_index == -1:
               raise ValueError("Invalid JSON structure in raw output")

         json_string = raw_output[start_index:end_index + 1]
         no_newlines = json_string.replace("\n", " ")

         data  = None
         try:
            data = json.loads(no_newlines)
         except json.decoder.JSONDecodeError as err:
            logging.warning("Error loading JSON")
            try:
               data = eval(no_newlines)
            except Exception as e:
               logging.warning(e, "Error evaluating JSON")
               try:
                  data = no_newlines
               except Exception as e:
                  logging.error(e, "Error converting JSON to string")
                  data = {}


         
         # Check if 'content' exists and is a string; convert to list if so
         if "content" in data:
               if isinstance(data["content"], str):
                  data["content"] = [data["content"]]  # Convert string to list
         return data

      except (json.JSONDecodeError, ValueError) as e:
         print(f"Error decoding or cleaning JSON: {e}")
         return {}
 

   
   def get_agents(self,filter_value):
      filtered_dict = [agent for agent in self.agents if any(v == filter_value for _, v in agent.items())]
      return [v for filtered_dict_ in filtered_dict for _, v in filtered_dict_.items() if isinstance(v, Agent)]


   def get_tasks(self, filter_value):
      filtered_tasks = [task for task in self.tasks if task.agent.goal == filter_value]
      return filtered_tasks
   
   @schema_context(os.getenv('SCHEMA_NAME'))
   def patch_account_request(self, output, username):
      username = self.inputs["outsourced_info"]["username"]
      
      get_id_account_data = {
         "username": username
      }
      response = requests.post(f"{os.getenv('API_URL')}/instagram/account/get-id/",data=get_id_account_data)
      # import pdb;pdb.set_trace()
      print(response.json())
      account_id = response.json()['id']
      prequalified_flag = False
      try:
         prequalified_flag = output['prequalified']['prequalified']
      except Exception as e:
         logging.warning(e)
         try:
            prequalified_flag = output['prequalified'] if isinstance(output['prequalified'],bool) else output['prequalified']['desired_category']
         except Exception as err:
            logging.warning(err)
            try:
               prequalified_flag = False
            except Exception as err:
               logging.error(err)
               prequalified_flag = False

      # import pdb;pdb.set_trace()
      # print(prequalified_flag)
      account_dict = {
         "igname": username,
         "is_manually_triggered":True,
         "relevant_information": output if output else {},
         "qualified": prequalified_flag,
      }

      response = requests.patch(
         f"{os.getenv('API_URL')}/instagram/account/{account_id}/",
         headers=self.headers,
         data=json.dumps(account_dict)
      )
      # let us try our new patch below

      try:
        account_ = Account.objects.get(id=account_id)
        logging.warning(f"account-->{account_.igname}")
        account_.is_manually_triggered = True
        account_.relevant_information = output if output else {}
        account_.qualified = prequalified_flag
        account_.save()    
      except Exception as err:
        logging.error(err)
        print(f"Error saving account information to the database --{err}")
      logging.warning(f"running-->{response.json()}")
      return response

   @start()
   def prequalifying_flag_assessor(self):
      agents = self.get_agents(inspect.currentframe().f_code.co_name)
      first_agent = next(iter(agents))
      tasks = self.get_tasks(first_agent.goal)
      desired_category = None
      desired_location = None
      desired_visibility = None
      desired_activity = None
      desired_provider = None
      desired_size = None

      for task in tasks: # we iterate through each task and handle them separately if needed
         crew = Crew(agents=agents, tasks=[task], verbose=True, memory=True)
         # self.inputs['outsourced_info'] = {"preqaulified":self.state.get("prequalified_result",{})}
         result = crew.kickoff(inputs=self.inputs)
         if result.json_dict:
            if result.json_dict.get("desired_location") is not None and isinstance(result.json_dict.get("desired_location"),bool):
               desired_location = result.json_dict.get("desired_location")
            
            if result.json_dict.get("desired_category") is not None and isinstance(result.json_dict.get("desired_category"),bool):
               desired_category = result.json_dict.get("desired_category")

            if result.json_dict.get("desired_visibility") is not None and isinstance(result.json_dict.get("desired_visibility"),bool):
               desired_visibility = result.json_dict.get("desired_visibility")
            
            if result.json_dict.get("desired_activity") is not None and isinstance(result.json_dict.get("desired_activity"),bool):
               desired_activity = result.json_dict.get("desired_activity")

            if result.json_dict.get("desired_provider") is not None and isinstance(result.json_dict.get("desired_provider"),bool):
               desired_provider = result.json_dict.get("desired_provider")

            if result.json_dict.get("desired_size") is not None and isinstance(result.json_dict.get("desired_size"),bool):
               desired_size = result.json_dict.get("desired_size")

      conditions = [desired_location, desired_category, desired_visibility, desired_activity, desired_provider, desired_size]
      print(conditions)
      if any(conditions):
         self.state["prequalified_result"] = {
            "prequalified":True,
            "desired_location":desired_location, 
            "desired_category": desired_category, 
            "desired_visibility":desired_visibility, 
            "desired_activity": desired_activity, 
            "desired_provider": desired_provider, 
            "desired_size": desired_size
         }
      else:
         self.state["prequalified_result"] = {
            "prequalified":False,
            "desired_location":desired_location, 
            "desired_category": desired_category, 
            "desired_visibility":desired_visibility, 
            "desired_activity": desired_activity, 
            "desired_provider": desired_provider, 
            "desired_size": desired_size
         }
      # import pdb;pdb.set_trace()
         # crew_result = result.json_dict
      # self.state["prequalified_result"] = result.json_dict
      # self.inputs['outsourced_info'].update(result.json_dict)
      # print(crew_result)
      print(self.state)
      print(1)
      biography = self.inputs['outsourced_info']['biography']
      external_url = self.inputs['outsourced_info']['external_url']
      city_name = self.inputs['outsourced_info']['city_name']
      full_name = self.inputs['outsourced_info']['full_name']
      public_email = self.inputs['outsourced_info']['public_email']
      public_phone_number = self.inputs['outsourced_info']['public_phone_number'],
      contact_phone_number = self.inputs['outsourced_info']['contact_phone_number']
      if self.state["prequalified_result"]["prequalified"]:
         # print(self.state["output"])
         self.patch_account_request(
            {
               "prequalified":self.state["prequalified_result"]["prequalified"],
               "name":full_name if full_name else "",
               "full_name":full_name if full_name else "",
               "bio": biography if biography else "",
               "external_url": external_url if external_url else "",
               "strengths": result.json_dict.get("strengths",""),
               "area": result.json_dict.get("area") if result.json_dict.get("area") else city_name,
               "contact_details": {
                  "public_email": public_email if public_email else "",
                  "public_phone_number": public_phone_number if public_phone_number else "",
                  "contact_phone_number": contact_phone_number if contact_phone_number else ""
               }

            }, self.inputs["outsourced_info"]["username"])
      

      # patch the output to the database
      print(3)
      
   # @listen(prequalifying_flag_assessor)
   # def lead_score_calculator(self):
   #    agents = self.get_agents(inspect.currentframe().f_code.co_name)
   #    first_agent = next(iter(agents))
   #    tasks = self.get_tasks(first_agent.goal)
   #    crew = Crew(agents=agents, tasks=tasks, verbose=True, memory=True)
   #    result = crew.kickoff(inputs=self.inputs)
   #    crew_result = result.json_dict
   #    self.state["score_result"] = crew_result
   #    print(2)

   

   @listen(and_(prequalifying_flag_assessor))
   def prequalifying_output_extractor(self):
      print("---- Logger ----")
      agents = self.get_agents(inspect.currentframe().f_code.co_name)
      first_agent = next(iter(agents))
      tasks = self.get_tasks(first_agent.goal)
      crew = Crew(agents=agents, tasks=tasks, verbose=True, memory=True)
      # self.inputs['outsourced_info'].update({"lead_score":self.state.get("score_result",{}), "preqaulified":self.state.get("prequalified_result",{})})
      biography = self.inputs['outsourced_info']['biography']
      external_url = self.inputs['outsourced_info']['external_url']
      city_name = self.inputs['outsourced_info']['city_name']
      full_name = self.inputs['outsourced_info']['full_name']
      public_email = self.inputs['outsourced_info']['public_email']
      public_phone_number = self.inputs['outsourced_info']['public_phone_number'],
      contact_phone_number = self.inputs['outsourced_info']['contact_phone_number']
      self.inputs['outsourced_info'] = {"username":self.inputs['outsourced_info']['username'],"bio":self.inputs['outsourced_info']['biography']}
      # self.inputs['outsourced_info'].update({"preqaulified":self.state.get("prequalified_result",{})})
      # self.inputs['outsourced_info'] = {"preqaulified":self.state.get("prequalified_result",{})}
      result = crew.kickoff(inputs=self.inputs)
      # import pdb;pdb.set_trace()
      # crew_result = result.json_dict
      self.state["output"] = result.json_dict

      # import pdb;pdb.set_trace()
      # print(self.state["output"])
      if self.state["prequalified_result"]["prequalified"]:
         # print(self.state["output"])
         self.patch_account_request(
            {
               "prequalified":self.state["prequalified_result"]["prequalified"],
               "name":self.state["output"]["name"],
               "full_name":full_name if full_name else "",
               "bio": biography if biography else "",
               "external_url": external_url if external_url else "",
               "strengths": result.json_dict.get("strengths",""),
               "area": result.json_dict.get("area") if result.json_dict.get("area") else city_name,
               "contact_details": {
                  "public_email": public_email if public_email else "",
                  "public_phone_number": public_phone_number if public_phone_number else "",
                  "contact_phone_number": contact_phone_number if contact_phone_number else ""
               }

            }, self.inputs["outsourced_info"]["username"])
      

      # patch the output to the database
      print(3)


      
class SetupAgent(APIView):
    def post(self, request):
        data = None
        print("Request---",request.data)
        if not request.data:
            return Response({"error": "No data provided"}, status=400)
        # import pdb;pdb.set_trace()
        content = request.data.get('_content')
        if content is None:
            print({"error": f"'_content' not found in request data - {request.data}"})
        
        # else:
            content = request.data
        # corrected_content = content.replace("\\'", "'")

        try:
            data = json.loads(content)
        except Exception as err:
            try:
                data = request.data
            except Exception as err:
                print(err)

        

        # with schema_context("lunyamwi"):

        # workflow_data = data.get("workflow_data")
        workflow = None
        opensource = False    
        agents = []
        tasks = []
        department_name = data.get("department")
        with schema_context(os.getenv("SCHEMA_NAME")):
            print(Department.objects.filter(name=department_name))
            department = Department.objects.filter(name=department_name).latest("created_at")
            
            agents_ = department.agents.all()
            tasks_ = department.tasks.all()
            payload = data.get(department.baton.start_key)
            if isinstance(payload, str):
                import ast
                payload = ast.literal_eval(payload)
            print(payload)
            # print(tasks_)
            for i, agent in enumerate(agents_):
                print(agent.llm)
                agents.append({f"agent_{i}":Agent(
                                    role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else "Qualifying department",
                                    goal=agent.goal,
                                    backstory=agent.prompt.last().text_data,
                                    allow_delegation=False,
                                    verbose=True,
                                    llm=agent.llm
                                ),
                                f"workflow_step_{i}":agent.workflow
                                })
            for i,task in enumerate(tasks_):              
                tasks.append(Task(
                                description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                expected_output=task.expected_output,
                                tools=[TOOLS.get(tool.name) for tool in task.tools.all()],
                                agent=Agent(
                                    role=task.agent.role.description + " " + task.agent.role.tone_of_voice if task.agent.role else "Qualifying department",
                                    goal=task.agent.goal,
                                    backstory=task.agent.prompt.last().text_data,
                                    allow_delegation=False,
                                    verbose=True,
                                    llm=task.agent.llm
                                ),
                                output_json=OUTPUT_MODELS.get(task.output)
                            ))
                            
            # print(tasks)
            flow = PrequalifyingWorkflow(agents = agents,tasks = tasks,inputs = payload)
            asyncio.run(flow.kickoff())

        return Response({"result": flow.state}, status=200)


class agentSetup(APIView):
    # @schema_context("lunyamwi")
    def log_scrapping_logs(self, log_file_path):
        """Logs the contents of scrappinglogs.txt to W&B and deletes the file."""
        try:
            with open(log_file_path, 'r') as file:
                logs = file.read()
                # Log the entire content of the log file
                wandb.log({"scrapping_logs": logs})
                print("Scrapping logs logged successfully.")
            
            # Delete the log file after logging
            os.remove(log_file_path)
            print(f"{log_file_path} has been deleted.")
        
        except Exception as e:
            print(f"Error logging scrapping logs: {e}")

    def post(self,request):
        # print(request.tentant.schema_name)
        # print(f"Received request data: {request.data}")
        # print(f"Current tenant schema: {request.tenant.schema_name}")
        data = None
        print("Request---",request.data)
        if not request.data:
            return Response({"error": "No data provided"}, status=400)
        # import pdb;pdb.set_trace()
        content = request.data.get('_content')
        if content is None:
            print({"error": f"'_content' not found in request data - {request.data}"})
        
        # else:
            content = request.data
        # corrected_content = content.replace("\\'", "'")

        try:
            data = json.loads(content)
        except Exception as err:
            try:
                data = request.data
            except Exception as err:
                print(err)

        

        # with schema_context("lunyamwi"):

        # workflow_data = data.get("workflow_data")
        workflow = None
        opensource = False    
        llm_val = LLM(model="gpt-3.5-turbo")
        with schema_context(os.getenv("SCHEMA_NAME")):

            # import pdb;pdb.set_trace()          
            department = Department.objects.filter(name = data.get("department")).get(version = data.get("version"))
            logging.warning(f"Department: {data.get('department')}")
            logging.warning(f"Department: {department}")
            logging.warning(f"Schema: {os.getenv('SCHEMA_NAME')}")
            info = data.get(department.baton.start_key)
            if isinstance(info, str):
                import ast
                info = ast.literal_eval(info)
            print(info)
            
            agents = []
            tasks = []
            
            department_agents = None
            if department.agents.filter(name = data.get('agent_name','agent')).exists():
                department_agents = department.agents.filter(name = data.get('agent_name'))
            else:
                department_agents = department.agents.exclude(name__icontains='monitoring')
            for agent in department_agents:
                print(agent)
                # import pdb;pdb.set_trace()
               
                if agent.tools.filter().exists():
               
                    if agent.is_opensource:
                        opensource = agent.is_opensource

                        agents.append(Agent(
                            role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                            goal=agent.goal,
                            backstory=agent.prompt.last().text_data,
                            tools = [TOOLS.get(tool.name) for tool in agent.tools.all()],
                            allow_delegation=False,
                            verbose=True,
                            llm=llm_val
                        ))
                    else:
                        agents.append(Agent(
                            role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                            goal=agent.goal,
                            backstory=agent.prompt.last().text_data,
                            tools = [TOOLS.get(tool.name) for tool in agent.tools.all()],
                            allow_delegation=False,
                            verbose=True,
                            llm=llm_val
                        ))
                else:
                    if agent.is_opensource:
                        opensource = agent.is_opensource
                        agents.append(Agent(
                            role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                            goal=agent.goal,
                            backstory=agent.prompt.last().text_data,
                            allow_delegation=False,
                            verbose=True,
                            # llm="huggingface/mistralai/Mistral-7B-Instruct-v0.3"
                            llm=llm_val
                        ))
                    else:
                        agents.append(Agent(
                            role=agent.role.description + " " + agent.role.tone_of_voice if agent.role else department.name,
                            goal=agent.goal,
                            backstory=agent.prompt.last().text_data,
                            allow_delegation=False,
                            verbose=True,
                            llm=llm_val
                        ))
                
            tasks = []
            department_agent_tasks = None
            if department.tasks.filter(agent__name = data.get('agent_name')).order_by('index'):
                department_agent_tasks = department.tasks.filter(name = data.get('agent_task')).order_by('index')
            else:
                department_agent_tasks = department.tasks.exclude(name__icontains='monitoring').order_by('index')
            
            for task in department_agent_tasks:
                print(task)
                agent_ = None
                for agent in agents:
                    if task.agent.goal == agent.goal:
                        agent_ = agent
                if  agent_:
                    if task.tools.filter().exists():
                        if task.agent.is_opensource:
                            try:
                                tasks.append(Task(
                                    description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                    expected_output=task.expected_output,
                                    tools=[TOOLS.get(tool.name) for tool in task.tools.all()],
                                    agent=agent_,
                                    output_json=OUTPUT_MODELS.get(task.output)
                                ))
                            except Exception as e:
                                logging.warning(f"No json pydantic model found-->{e}")
                                try:
                                    tasks.append(Task(
                                        description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                        expected_output=task.expected_output,
                                        tools=[TOOLS.get(tool.name) for tool in task.tools.all()],
                                        agent=agent_
                                    ))
                                except Exception as e:
                                    print(e)

                        else:
                            try:
                                tasks.append(Task(
                                    description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                    expected_output=task.expected_output,
                                    tools=[TOOLS.get(tool.name) for tool in task.tools.all()],

                                agent=agent_,
                                output_json=OUTPUT_MODELS.get(task.output)
                                ))
                            except Exception as e:
                                print(e)
                        
                            
                    else:
                        if task.agent.is_opensource:
                            print("are we reaching here................****")
                            try:
                                print("ok this is the condition we are using--------------------***")
                                # import pdb;pdb.set_trace()
                                tasks.append(Task(
                                    description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                    expected_output=task.expected_output,
                                    agent=agent_
                                    # output_json=OUTPUT_MODELS.get(task.output)
                                ))
                            except Exception as e:
                                print(f"Issue with json when tools switched off {e}")
                        else:
                            try:
                                tasks.append(Task(
                                    description=task.prompt.last().text_data if task.prompt.exists() else "perform agents task",
                                    expected_output=task.expected_output,
                                    agent=agent_,
                                    output_json=OUTPUT_MODELS.get(task.output),
                                    output_parser=lambda json_string: PrequalifyingOutput(**remove_duplicate_content_keys(json_string)))
                                )
                            except Exception as e:
                                print(e)
                    
                
            logging_filename = f"scrappinglogs-{str(uuid.uuid4())}.txt"
            crew = Crew(
                agents=agents,
                cache=False,
                tasks=tasks,
                # process=Process.sequential,
                verbose=True,
                memory=True,
                # output_log_file=logging_filename
            )
            
            
            # if workflow_data:
                # workflow_tool = TOOLS.get("workflow_tool")
                # response = workflow_tool._run(workflow_data)
                # inputs.update({"workflow_data":workflow_data})
            result = crew.kickoff(inputs=info)
        
            
            # if isinstance(result, dict):
                # kickstart new workflow
            # send_logs.delay(data,result.json_dict)
            # with wandb.init(
            #         project="boostedchat",  # replace with your WandB project name
            #         entity="lutherlunyamwi",       # replace with your WandB username or team
            #         name=f"crewai_run_{data.get('department')}",  # custom name for each run
            #         config=data,           # optionally log the request data as run config
            #         settings=wandb.Settings(
            #             _service_wait=1200,  # Increase service wait time to 600 seconds
            #             init_timeout=1200     # Increase initialization timeout to 600 seconds
            #         )
                    
            #     ) as run:
            #     wandb_handler = WandbLoggingHandler()
            #     wandb_handler.setLevel(logging.INFO)
            #     wandb_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

            #     langchain_logger = logging.getLogger("langchain")
            #     langchain_logger.addHandler(wandb_handler)
            #     langchain_logger.setLevel(logging.INFO)
                
            #     if opensource:
            #         try:
            #             wandb.log({"result":result.raw})
            #         except Exception as err:
            #             print(err)
            #     else:
            #         try:
            #             wandb.log({"result": result.json_dict})  # log the final result
            #         except Exception as e:
            #             print(e)
                # Optionally, log additional information about agents and tasks
                # with wandb.init(
                #     project="boostedchat",  # replace with your WandB project name
                #     entity="lutherlunyamwi",       # replace with your WandB username or team
                #     name=f"crewai_run_{data.get('department')}",  # custom name for each run
                #     config=data,           # optionally log the request data as run config
                #     settings=wandb.Settings(
                #         _service_wait=1200,  # Increase service wait time to 600 seconds
                #         init_timeout=1200     # Increase initialization timeout to 600 seconds
                #     )
                    
                # ) as run:
                #     wandb.log({
                #         "agents": [{"role": agent.role, "goal": agent.goal, "tools": str(agent.tools)} for agent in agents],
                #         "tasks": [{"description": task.description, "expected_output": task.expected_output} for task in tasks]
                #     })

                #     # End wandb run
                #     time.sleep(2)
                #     self.log_scrapping_logs(logging_filename)
                #     wandb.finish()
            # import pdb;pdb.set_trace()
            if opensource:
                # import pdb;pdb.set_trace()
                try:
                    cleaned_json = clean_json_output(result.raw)
                    return Response({"result":cleaned_json},status=status.HTTP_200_OK)
                except Exception as err:

                    logging.warning(f"Problem with json --> {err}")
                    try:
                        return Response({"result":result.raw})
                    except Exception as e:
                        logging.warning(f"Problem with raw --> {e}")
            else:
                try:
                    return Response({"result":result.json_dict})
                except Exception as e:
                    print(e)

        # else:
        #     return Response({"result":result})


from django.shortcuts import render


def fetch_logs(request):
    api = wandb.Api()
    entity = "lutherlunyamwi"
    project = "boostedchat"
    # runs = api.runs(f"{entity}/{project}")
    runs = api.runs(f"{entity}/{project}", order="-created_at")[:15]

    run_data = []
    for run in runs:
        if run.state == "finished":
            timestampobj = run.summary.get('_timestamp')
            datetime_obj = datetime.fromtimestamp(timestampobj)
            history = run.history()
            run_data.append({
                'name': run.name,
                'summary': run.summary,
                'datetime_obj': datetime_obj,
                'history': history.to_dict(orient='records'),
            })

    return render(request, 'prompt/logs.html', {'run_data': run_data})



class getAgent(APIView):
    def post(self, request, *args,**kwargs):
        transition_prompt = Prompt.objects.filter(name="ED_Stage_Transition_P").latest('created_at')
        template = transition_prompt.text_data
        all_tasks = [{"task_name":task.name,"task_description":task.prompt.last().text_data,"agent_name":task.agent.name,"agent_goal":task.agent.goal} for task in Department.objects.filter(name="Engagement Department").latest('created_at').tasks.all()]
        prompt = ChatPromptTemplate.from_template(template)
        model = ChatOpenAI(model="gpt-3.5-turbo",temperature=0)
        output_parser = StrOutputParser()
        chain = RunnableMap({
                "userInput": lambda x: x["userInput"],
                "information": lambda x: x["information"]
            }) | prompt | model | output_parser
        
        data = {"information":
                { 
                    "tasks":all_tasks,
                    "conversations":request.data.get("conversations",""),
                    "active_stage": request.data.get("active_stage","")
                },"userInput":request.data.get("message")}
        chain.invoke(data)
        result = chain.invoke(data)

        return Response(json.loads(result),status=status.HTTP_200_OK)
        




class PromptViewSet(viewsets.ModelViewSet):
    queryset = Prompt.objects.all()
    serializer_class = PromptSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return CreatePromptSerializer
        return super().get_serializer_class()


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_serializer_class(self):
        if self.action == "update":
            return CreateRoleSerializer
        return super().get_serializer_class()


@api_view(['GET'])
def fetch_logs_api(request):
    api = wandb.Api()
    entity = "lutherlunyamwi"
    project = "boostedchat"
    runs = api.runs(f"{entity}/{project}")

    run_data = []
    for run in runs:
        if run.state == "finished":
            timestampobj = run.summary.get('_timestamp')
            datetime_obj = datetime.fromtimestamp(timestampobj)
            history = run.history()

            run_data.append({
                'name': run.name,
                'summary': run.summary,
                'datetime_obj': datetime_obj,
                'history': history.to_dict(orient='records'),
            })

    serializer = RunDataSerializer(run_data, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)
