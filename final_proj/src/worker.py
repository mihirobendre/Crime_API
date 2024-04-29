import json
import uuid
import redis
from hotqueue import HotQueue
import os
import logging
import requests
from flask import Flask, request, jsonify
from jobs import return_all_jobids, get_job_by_id, update_job_status, q, rd, jdb
import time

# Read the value of the LOG_LEVEL environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=log_level)

#_redis_ip = os.environ.get('REDIS_IP')
_redis_ip = 'redis-db'
_redis_port = '6379'
_list_of_jobs = []

rd = redis.Redis(host=_redis_ip, port=6379, db=0)
q = HotQueue("queue", host=_redis_ip, port=6379, db=1)
jdb = redis.Redis(host=_redis_ip, port=6379, db=2)
res = redis.Redis(host=_redis_ip, port=6379, db = 3)

url = 'https://data.austintexas.gov/resource/fdj4-gpfu.json'

def count_crimes_for_crime_type(crime_type: str) -> int:
    """
    Function to count the number of crimes for a certain crime_type
    """
    # Get crime data from the URL
    response = requests.get(url)
    if response.status_code == 200:
        crime_data = response.json()
        # Filter crime data between start_time and end_time
        filtered_crime_data = [crime for crime in crime_data if crime_type == crime.get('crime_type')]
        # Count the number of crimes
        num_crimes = len(filtered_crime_data)
        #num_crimes = 3
        logging.info("Successfully fetched and counted crimes for crime_type %s. Count: %d", crime_type, num_crimes)
        return num_crimes
    else:
        logging.error("Failed to fetch crime data. Status code: %d", response.status_code)
        return 404  # Return to indicate failure

@q.worker
def worker(jobid):
    update_job_status(jobid, 'in progress')

    try:
        job_data = get_job_by_id(jobid)
    except ValueError:
        logging.error("This jobid is no longer in the queue")
        print("This jobid isn't in queue!") 
    crime_type = job_data.get('crime_type')
    
    num_crimes = count_crimes_for_crime_type(crime_type)
    
    res.set(str(jobid), str(num_crimes))
    # Update job status with results
    update_job_status(jobid, 'completed')
    
worker()


