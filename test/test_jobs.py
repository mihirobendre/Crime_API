import pytest
import json
import redis
from jobs import (
    _generate_jid,
    _instantiate_job,
    _save_job,
    _queue_job,
    add_job,
    get_job_by_id,
    update_job_status,
    return_all_jobids
)

_redis_ip = 'redis-db'
_redis_port = '6379'
# Fixture to set up Redis connection for testing
@pytest.fixture(scope='module')
def redis_connection():
    rd = redis.Redis(host=_redis_ip, port=_redis_port, db=0)
    yield rd
    # Clean up Redis database after tests
    rd.flushdb()

# Test _generate_jid function
def test_generate_jid():
    jid = _generate_jid()
    assert isinstance(jid, str)

# Test _instantiate_job function
def test_instantiate_job():
    jid = _generate_jid()
    job_type = "test"
    params = {"param": "value"}
    job_dict = _instantiate_job(jid, "submitted", job_type, params)
    assert isinstance(job_dict, dict)
    assert job_dict['id'] == jid
    assert job_dict['status'] == "submitted"
    assert job_dict['job_type'] == job_type
    assert job_dict['params'] == params

# Test _save_job and get_job_by_id functions
def test_save_and_get_job(redis_connection):
    jid = _generate_jid()
    job_dict = {'id': jid, 'status': 'submitted', 'job_type': 'test', 'params': {"param": "value"}}
    _save_job(jid, job_dict)
    retrieved_job_dict = get_job_by_id(jid)
    assert retrieved_job_dict == job_dict

# Test _queue_job function
def test_queue_job(redis_connection):
    jid = _generate_jid()
    _queue_job(jid)
    assert q.contains(jid)

# Test add_job function
def test_add_job(redis_connection):
    job_type = "test"
    params = {"param": "value"}
    job_dict = add_job(job_type, params)
    assert isinstance(job_dict, dict)
    assert 'id' in job_dict
    assert 'status' in job_dict
    assert 'job_type' in job_dict
    assert 'params' in job_dict
    assert job_dict['status'] == "submitted"

# Test update_job_status function
def test_update_job_status(redis_connection):
    jid = _generate_jid()
    job_dict = {'id': jid, 'status': 'submitted', 'job_type': 'test', 'params': {"param": "value"}}
    _save_job(jid, job_dict)
    update_job_status(jid, "processing")
    retrieved_job_dict = get_job_by_id(jid)
    assert retrieved_job_dict['status'] == "processing"

# Test return_all_jobids function
def test_return_all_jobids(redis_connection):
    jid1 = _generate_jid()
    jid2 = _generate_jid()
    job_dict1 = {'id': jid1, 'status': 'submitted', 'job_type': 'test', 'params': {"param": "value"}}
    job_dict2 = {'id': jid2, 'status': 'submitted', 'job_type': 'test', 'params': {"param": "value"}}
    _save_job(jid1, job_dict1)
    _save_job(jid2, job_dict2)
    all_job_ids = json.loads(return_all_jobids())
    assert jid1 in all_job_ids
    assert jid2 in all_job_ids

