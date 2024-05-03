import os
import pytest
import json
import requests
from api import app

# Fixture to initialize the Flask app for testing
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b'Hello, world!\n'

def test_handle_data(client):
    # Test POST request
    response_post = client.post('/data')
    assert response_post.status_code == 200

    # Test GET request
    response_get = client.get('/data')
    assert response_get.status_code == 200
    assert isinstance(response_get.json, list)

    # Test DELETE request
    response_delete = client.delete('/data')
    assert response_delete.status_code == 200

def test_all_values_for(client):
    response = client.get('/all_values_for/crime_type')
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'message' in response.json
    assert 'all values' in response.json

def test_all_data_for(client):
    response = client.get('/all_data_for/crime_type/THEFT')
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'message' in response.json
    assert 'all data' in response.json

def test_order(client):
    response = client.get('/order/ascend/occ_date')
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'data' in response.json
    assert 'message' in response.json

def test_jobs_general(client):
    # Test POST request
    data = {'job_type': 'histogram', 'params': {'param': 'crime_type'}}
    response_post = client.post('/jobs', json=data)
    assert response_post.status_code == 200
    assert isinstance(response_post.json, dict)
    assert 'job_id' in response_post.json

    # Test GET request
    response_get = client.get('/jobs')
    assert response_get.status_code == 200
    assert isinstance(response_get.json, list)

def test_get_job(client):
    # Get job id from previous test
    response_get_jobs = client.get('/jobs')
    assert response_get_jobs.status_code == 200
    assert isinstance(response_get_jobs.json, list)
    job_id = response_get_jobs.json[0]['job_id']

    response = client.get(f'/jobs/{job_id}')
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert 'job_id' in response.json

def test_calculate_result(client):
    # Get job id from previous test
    response_get_jobs = client.get('/jobs')
    assert response_get_jobs.status_code == 200
    assert isinstance(response_get_jobs.json, list)
    job_id = response_get_jobs.json[0]['job_id']

    response = client.get(f'/results/{job_id}')
    assert response.status_code == 200

def test_download(client):
    # Get job id from previous test
    response_get_jobs = client.get('/jobs')
    assert response_get_jobs.status_code == 200
    assert isinstance(response_get_jobs.json, list)
    job_id = response_get_jobs.json[0]['job_id']

    response = client.get(f'/download/{job_id}')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/png'

