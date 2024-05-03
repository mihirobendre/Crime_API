import pytest
from api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_hello_world(client):
    response = client.get('/')
    assert response.data == b'Hello, world!\n'

def test_handle_data_post(client, mocker):
    mocker.patch('api.requests.get')
    response_mock = mocker.MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = [{'key': 'value'}]
    api.requests.get.return_value = response_mock

    response = client.post('/data')
    assert response.data == b'Data loaded\n'

def test_handle_data_get(client):
    response = client.get('/data')
    assert response.status_code == 200

def test_handle_data_delete(client):
    response = client.delete('/data')
    assert response.data == b'Data deleted\n'

def test_all_values_for(client):
    response = client.get('/all_values_for/key')
    assert response.status_code == 200

def test_all_data_for(client):
    response = client.get('/all_data_for/key/value')
    assert response.status_code == 200

def test_org_by(client):
    response = client.get('/order/ascend/key')
    assert response.status_code == 200

def test_jobs_general_post(client):
    response = client.post('/jobs', json={'job_type': 'type', 'params': 'params'})
    assert response.status_code == 200

def test_jobs_general_get(client):
    response = client.get('/jobs')
    assert response.status_code == 200

def test_get_job(client):
    response = client.get('/jobs/jobid')
    assert response.status_code == 200

def test_calculate_result(client):
    response = client.get('/results/jobid')
    assert response.status_code == 200

def test_download(client):
    response = client.get('/download/jobid')
    assert response.status_code == 200
