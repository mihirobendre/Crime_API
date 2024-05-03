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
import matplotlib.pyplot as plt

# Read the value of the LOG_LEVEL environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=log_level)

#_redis_ip = os.environ.get('REDIS_IP')
_redis_ip = 'redis-db'
_redis_port = '6379'
_list_of_jobs = []

# These might not be needed, as we're importing them from jobs:
'''
rd = redis.Redis(host=_redis_ip, port=6379, db=0)
q = HotQueue("queue", host=_redis_ip, port=6379, db=1)
jdb = redis.Redis(host=_redis_ip, port=6379, db=2)
'''

res = redis.Redis(host=_redis_ip, port=6379, db = 3)

url = 'https://data.austintexas.gov/resource/fdj4-gpfu.json'


def all_values_for(param, data):
    dict_of_values = {}
    num_instances = 0
    for item in data:
        if param in item.keys():
            num_instances += 1    
            value = item[param]
            if isinstance(value, str) and not isinstance(value, dict):
                if value not in dict_of_values:
                    dict_of_values[value] = 1
                else:
                    dict_of_values[value] += 1

    return dict_of_values


def hist_plotter(param):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        dict_of_values = all_values_for(param, data)

    # Extracting keys (variables) and values (occurrences) from the dictionary
    variables = list(dict_of_values.keys())
    occurrences = list(dict_of_values.values())

    # Plotting the histogram
    plt.bar(variables, occurrences, color='skyblue', edgecolor='black')

    # Adding labels and title
    plt.xlabel(f"Values for {param}")
    plt.ylabel('Occurrences')
    plt.title('Histogram for {param}')

    # Rotating x-axis labels for better readability (optional)
    plt.xticks(rotation=45)

    # Save the plot
    plt.savefig('/output_image.png')


@q.worker
def worker(jobid):
    update_job_status(jobid, 'in progress')

    try:
        job_data = get_job_by_id(jobid)
    except ValueError:
        logging.error("This jobid is no longer in the queue")
        print("This jobid isn't in queue!") 
    
    job_type = job_data.get('job_type')
    
    if job_type == "histogram":
        param = job_data.get('params')['param']
        #param = "crime_type"
        hist_plotter(param)

        

        with open('/output_image.png', 'rb') as f:
            img = f.read()
        res.hset(jobid, 'image', img)
    
    update_job_status(jobid, 'completed')
    
worker()


