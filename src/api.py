import os
import requests
from flask import Flask, request, jsonify, send_file
import redis
import json
from typing import Union, List, Dict
from jobs import add_job, get_job_by_id, rd, return_all_jobids
import logging
from datetime import datetime


# Read the value of the LOG_LEVEL environment variable
log_level = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(level=log_level)

app = Flask(__name__)

REDIS_IP = os.environ.get('REDIS_IP')

rd = redis.Redis(host=REDIS_IP, port=6379, db=0)
res = redis.Redis(host=REDIS_IP, port = 6379, db = 3)

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


@app.route('/all_values_for/<param>', methods=['GET'])
def all_values_for(param):
    """
    Endpoint to get all possible values for a specific parameter and their occurrences.

    Args:
        param (str): The parameter for which to retrieve values.

    Returns:
        Dict[str, Union[str, Dict[str, int]]]: A dictionary containing a message and a dictionary of values with their occurrences.
    """
    response = requests.get(url)
    dict_of_values = {}
    num_instances = 0
    message = None
    data = []
    for item in rd.keys():
        data.append(json.loads(rd.get(item)))

    for item in data:
       if param in list(item.keys()):
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

# for categorical parameter
@app.route('/all_data_for/<param>/<value>', methods=['GET'])
def all_data_for(param, value):
    """
    Endpoint to retrieve all data where a specific parameter equals a certain value.

    Args:
        param (str): The parameter to filter.
        value (str): The value to filter by.

    Returns:
        Dict[str, Union[str, List[Dict[str, str]]]]: A dictionary containing a message and the filtered data.
    """    
    limit = request.args.get('limit', None, type=int)
    offset = request.args.get('offset', 0, type=int)
    list_of_data = []
    num_instances = 0
    message = None
    data = []
    
    for item in rd.keys():
        data.append(json.loads(rd.get(item)))

    for item in data:
        if param in item.keys():
            if item[param] == value:
                num_instances += 1
                list_of_data.append(item)
    
    # Message formulation
    if num_instances == 0:
        message = "This field isn't present in the data"
    elif num_instances == len(data):
        message = "This field was present in all datapoints"
    elif num_instances <= len(data):
        num_instances = str(num_instances)
        total_instances = str(len(data))
        message = f"Out of a total of {total_instances} datapoints, {num_instances} contained the {value} value of the {param} field"
    
    if limit is not None:
        list_of_data = list_of_data[offset:offset+limit]

    return {"message": message,
            "all data": list_of_data}

# for sequential parameters, like date (will also work for id?)

# organize from date lowest to highest
@app.route('/order/<order>/<param>', methods=['GET'])
def org_by(param, order):
    """
    This endpoint organizes the data by a quantitative variable <param>. Although designed primarily for datetime variables, this function works on other quantitative variables as well.
    
    Parameters: param, order. 
        param: the parameter which we're ordering the dataset by (for this function, this is a quantitative parameter)
        order: this is either 'ascend' or 'descend'
        limit: (Optional) Specifies the maximum number of items to return (default is None, which means no limit).
        offset: (Optional) Specifies the number of items to skip before starting to return items (default is 0).

    Result: a json object containing the ordered 'data' along with a 'message' w/ information on how many of the datapoints contained <param>, the starting and ending values of the ordered dataset.

    """
    
    limit = request.args.get('limit', None, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    try:
        if order not in ["ascend", "descend"]:
            raise ValueError("Invalid value for 'order'. Please use 'ascend' or 'descend'.")
        else:
            print("Valid value for 'order'.")
    except ValueError as e:
        print(e)
    
    
    # declaring variables
    my_list_of_data = []
    num_instances = 0
    message = None

    data = []
    for item in rd.keys():
        data.append(json.loads(rd.get(item)))


    list_of_dates = []
    starting_date = None
    ending_date = None
    
    # populating list_of_dates
    for item in data:
        if param in list(item.keys()):
            num_instances += 1
            list_of_dates.append(item[str(param)])
    
    # sorting in ascending or descending order
    if order == 'ascend':
        sorted_list = sorted(list_of_dates)
    elif order == 'descend':
        sorted_list = sorted(list_of_dates, reverse=True)
    
    # sorting list of data in order
    new_list = []
    for date in sorted_list:
        for item in data:
            if param in list(item.keys()):
                if item[str(param)] == str(date):
                    new_list.append(item)
                    break
    
    # sorting list of data with limit and offset parameters in place
    new_list = []
    if limit is not None:
        for date in sorted_list[offset:offset+limit]:
            for item in data:
                if param in list(item.keys()):
                    if item[str(param)] == str(date):
                        new_list.append(item)
                        starting_date = str(sorted_list[offset])
                        ending_date = str(sorted_list[offset+limit])
                        break
    else:
        for date in sorted_list:
            for item in data:
                if param in list(item.keys()):
                    if item[str(param)] == str(date):
                        new_list.append(item)
                        starting_date = str(sorted_list[0])
                        ending_date = str(sorted_list[-1])
                        break

    # formulating message, and associated params
    if num_instances == 0:
        message = f"The field {param} isn't present in the data"
    elif num_instances == len(data):
        message = f"The field {param} was present in all datapoints. The starting value of {param} was {starting_date} and the ending value of {param} was {ending_date}, and the data was ordered in {order}ing order."
    elif num_instances <= len(data):
        num_instances = str(num_instances)
        total_instances = str(len(data))
        message = f"Out of a total of {total_instances} datapoints, {num_instances} contained the {param} field. The starting value of {param} was {starting_date} and the ending value of {param} was {ending_date}, and the data was ordered in {order}ing order."
    
    
    # returning resulting data and message
    return {'data': new_list,
            'message': message}


@app.route('/jobs', methods = ['GET','POST'])
def jobs_general():
    """
    Endpoint to handle general job operations (POST for adding a job, GET for getting all job IDs).

    Returns:
        Union[str, Dict[str, str]]: Response message or dictionary containing job information.
    """
    if request.method == 'POST':
        data = request.get_json()
        try:
            job_type = data['job_type']
            params = data['params']
        except ValueError:
            return "Parameter not supported by jobs endpoint"
        job_dict = add_job(job_type, params)
        return job_dict
    elif request.method == 'GET':
        ret_string = return_all_jobids() + '\n'
        return ret_string
    

@app.route('/jobs/<jobid>', methods = ['GET'])
def get_job(jobid):
    """
    Endpoint to get specific information for a job ID.

    Args:
        jobid (str): The ID of the job to retrieve information for.

    Returns:
        Union[str, Dict[str, str]]: Response message or dictionary containing job information.
    """
    return get_job_by_id(jobid)

@app.route('/results/<jobid>', methods = ['GET'])
def calculate_result(jobid):
    """
    Endpoint to retrieve computed outcome for a job ID.

    Args:
        jobid (str): The ID of the job to retrieve results for.

    Returns:
        Union[str, bytes]: Result of the computation or an error message.
    """
    # return computed outcome for that jobid
    try:
        result = res.get(jobid)
        return result
    except TypeError:
        return "Cannot find key in results database"

@app.route('/download/<jobid>', methods=['GET'])
def download(jobid):
    """
    Endpoint to download the resulting image for a job ID.

    Args:
        jobid (str): The ID of the job whose image to download.

    Returns:
        send_file: Response containing the image file.
    """
    path = f'/{jobid}.png'
    with open(path, 'wb') as f:
        f.write(res.hget(jobid, 'image'))   # 'results' is a client to the results db
    return send_file(path, mimetype='image/png', as_attachment=True)

@app.route('/help', methods=['GET'])
def help_route():
    ret_string = """{
    General routes:
        /data POST: Posts data to rd database
        /data GET: Gets data from rd database
        /data DELETE: Deletes data from rd database

        /all_values_for/<param> : Gets all possible values for a specific parameter (along w/ # occurences)
        
        /all_data_for/<param>/<value> : Returns all datapoints where a specific parameter equals a certain value. Works best for 
        /all_data_for/<param>/<value>?limit=int&offset=int : Same, with limit, offset functionality

        /order/<order>/<param> : Organizing data in <order> 'ascend' or 'descend', for quantitative <param>
        /order/<order>/<param>?limit=int&offset=int : Same, with limit, offset functionality
        

    Jobs routes:
        /jobs POST : Can post job with parameters 'job_type'(str) and 'params'(dict) 
        /jobs : Gets list of all jobids
        /jobs/<jobid> : Gets specific info for jobid
        /download/<jobid> : Downloads specific jobid's resulting image.
    }
    """
    return ret_string

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)
