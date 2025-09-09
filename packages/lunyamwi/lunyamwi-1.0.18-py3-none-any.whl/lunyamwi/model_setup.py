import requests
import os
import json
from .constants import LUNYAMWI_ML_BASE_URL


def setup_agent(payload = None):
    url = LUNYAMWI_ML_BASE_URL + '/agentSetup/'
    print(url)
    response = None
    try:
      resp = requests.post(url, data=json.dumps(payload),headers = {'Content-Type': 'application/json'})
      response = resp.json()
    except Exception as err:
      print(err)
    return response



def setup_agent_workflow(payload = None):
    url = LUNYAMWI_ML_BASE_URL + '/setupAgent/'
    print(url)
    response = None
    try:
      resp = requests.post(url, data=json.dumps(payload),headers = {'Content-Type': 'application/json'})
      response = resp.json()
    except Exception as err:
      print(err)
    return response

def fetch_logs():
    url = LUNYAMWI_ML_BASE_URL + '/api/fetch-logs/'
    response = None
    try:
        resp = requests.get(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def get_agent(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/getAgent/'
    print(url)
    response = None
    try:
      resp = requests.post(url, data=json.dumps(payload),headers = {'Content-Type': 'application/json'})
      response = resp.json()
    except Exception as err:
      print(err)
    return response
