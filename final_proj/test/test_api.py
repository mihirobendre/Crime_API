import pytest
import os
from api import app, hello_world, handle_data, crime_info_by_type, crime_info_by_id, all_crime_ids, all_crime_types,jobs_general, get_job, calculate_result 
import requests
import json

def is_json_string(s):
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False

def test_hello_world():
    response = requests.get('http://localhost:5000/')
    assert response.status_code == 200
    assert response.content.decode('utf-8') == 'Hello, world!\n'


def test_handle_data_delete():
    response = requests.delete('http://localhost:5000/data')
    assert response.status_code == 200
    assert response.content.decode('utf-8') == 'Data deleted\n'

def test_handle_data_post():

    # Send a POST request to the '/data' endpoint
    response = requests.post('http://localhost:5000/data')
    
    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

    # Check if the response content matches the expected message
    assert response.content.decode('utf-8') == 'Data loaded\n'


def test_handle_data_get():
    response = requests.get('http://localhost:5000/data')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert all(isinstance(item, dict) for item in response.json())

def test_crime_info_by_id():
    response = requests.get('http://localhost:5000/data/incident_report_number/123')
    assert response.status_code == 500

def test_all_crime_ids():
    response = requests.get('http://localhost:5000/data/incident_report_numbers')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_all_crime_types():
    response = requests.get('http://localhost:5000/data/crime_types')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_crime_info_by_type():
    response = requests.get('http://localhost:5000/data/crime_type/THEFT')
    assert response.status_code == 200
    assert all(isinstance(item, dict) for item in response.json())

def test_jobs_get():
    response = requests.get('http://localhost:5000/jobs')
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_jobs_post():
    # Define the payload data
    data = '{"crime_type":"THEFT"}'
    # Define the headers
    headers = {'Content-Type': 'application/json'}
    # Make the POST request using requests.post
    response = requests.post('http://localhost:5000/jobs', data=data, headers=headers)
    assert response.status_code == 200

def test_job_specific():
    job_id = "9033e47b-aa35-4038-ba6c-0587ba86842c"
    response = requests.get(f'http://localhost:5000/jobs/{job_id}')
    assert response.status_code == 200

def test_result():
    job_id = "9033e47b-aa35-4038-ba6c-0587ba86842c"
    response = requests.get(f'http://localhost:5000/results/{job_id}')
    assert response.status_code == 200

