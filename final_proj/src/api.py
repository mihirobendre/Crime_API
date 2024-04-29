
import os
import requests
from flask import Flask, request, jsonify
import redis
import json
from typing import Union, List, Dict
from jobs import add_job, get_job_by_id, rd, return_all_jobids
import logging

# Read the value of the LOG_LEVEL environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=log_level)

app = Flask(__name__)

#_redis_ip = os.environ.get('REDIS_IP')
_redis_ip = 'redis-db'

rd = redis.Redis(host=_redis_ip, port=6379, db=0)
res = redis.Redis(host=_redis_ip, port = 6379, db = 3)

url = "https://data.austintexas.gov/resource/fdj4-gpfu.json"


@app.route('/', methods=['GET'])
def hello_world() -> str:
    """
    Root endpoint returning a simple greeting message.

    Returns:
        str: Greeting message.
    """
    return 'Hello, world!\n'


@app.route('/data', methods=['GET', 'POST', 'DELETE'])
def handle_data() -> Union[str, List[Dict[str, str]]]:
    """
    Endpoint to handle data operations (GET, POST, DELETE).

    Returns:
        Union[str, List[Dict[str, str]]]: Response message or data.
    """
    if request.method == 'POST':
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            my_id = 0
            for item in data:
                rd.set(str(my_id), json.dumps(item))
                my_id += 1
            return 'Data loaded\n'
        else:
            print("Failed to fetch data:", response.status_code)
    elif request.method == 'GET':
        return_value = []
        for item in rd.keys():
            return_value.append(json.loads(rd.get(item)))
        return return_value
    elif request.method == 'DELETE':
        # Delete everything in redis
        for item in rd.keys():
            rd.delete(item)
        return 'Data deleted\n'
    else:
        return 'Not possible\n'




@app.route('/data/all_values_for/<param>', methods=['GET'])
def all_values_for(param):
    response = requests.get(url)
    
    dict_of_values = {}
    num_instances = 0
    message = None
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if param in item.keys():
                num_instances +=1
                value = item[param]
                if isinstance(value, str) and not isinstance(value, dict):
                    if value not in dict_of_values:
                        dict_of_values[value] = 1
                    else:
                        dict_of_values[value] += 1
    
    if num_instances == 0:
        message = "This field isn't present in the data"
    elif num_instances == len(data):
        message = "This field was present in all datapoints"
    elif num_instances <= len(data):
        num_instances = str(num_instances)
        total_instances = str(len(data))
        message = f"Out of a total of {total_instances} datapoints, {num_instances} contained the {param} field" 
    return {"message": message,
            "all values": dict_of_values}


@app.route('/data/all_data_for/<param>/<value>', methods=['GET'])
def all_data_for(param, value):
    response = requests.get(url)
    list_of_data = []
    num_instances = 0
    message = None
    if response.status_code == 200:
        data = response.json()
        for item in data:
            if param in item.keys():
                if item[param] == value:
                    num_instances += 1
                    list_of_data.append(item)
    if num_instances == 0:
        message = "This field isn't present in the data"
    elif num_instances == len(data):
        message = "This field was present in all datapoints"
    elif num_instances <= len(data):
        num_instances = str(num_instances)
        total_instances = str(len(data))
    return {"message": message,
            "all data": list_of_data}


'''
@app.route('/data/crime_type/<crime_type>', methods=['GET'])
def crime_info_by_type(crime_type: str) -> str:
    """
    Endpoint to retrieve information about specific crime based on type.

    Returns:
        str: JSON formatted list of crime IDs.
    """
    # Get data from web
    response = requests.get(url)
    list_of_crimes = []
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        for item in data:
            if item["crime_type"] == crime_type:
                list_of_crimes.append(item)
        return json.dumps(list_of_crimes)
    else:
        print("Failed to fetch data:", response.status_code)
        return None
'''

@app.route('/jobs', methods = ['GET','POST'])
def jobs_general():
    if request.method == 'POST':
        data = request.get_json()
        crime_type = None
        # add more parameters here        
        try:
            crime_type = data['crime_type']
            # add more parameters here
        except KeyError:
            return "The data doesn't contain the parameter(s) you requested'\n"
        
        job_dict = add_job(crime_type)
        return job_dict
    elif request.method == 'GET':
        ret_string = return_all_jobids() + '\n'
        return ret_string

@app.route('/jobs/<jobid>', methods = ['GET'])
def get_job(jobid):
    return get_job_by_id(jobid)

@app.route('/results/<jobid>', methods = ['GET'])
def calculate_result(jobid):
    # return computed outcome for that jobid
    try:
        result = res.get(jobid) 
        return result
    except TypeError:
        return "Cannot find key in results database"


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
