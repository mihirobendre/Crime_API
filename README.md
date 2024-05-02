
# Analyzing Austin TX Crimes dataset

## Project Objective
This project aims to create an API endpoint for querying and analyzing Austin, TX's crime dataset, which updates weekly.

## Folder Contents
- `api.py`: Contains the main routes for getting, posting and deleting data, as well as retreiving general and specific information about the dataset. This is the "front-end" portion of all our endpoints.
- `Dockerfile`: Contains commands for creating container.
- `docker-compose.yml`: Contains instructions for composing the flask app container, worker contianer, and redis database. 
- `requirements.txt`: Lists required packages and versions.
- `jobs.py`: Contains the entire "back-end" of the jobs endpoint. 
- `worker.py`: Contains the decorator and a simple function for launching the worker, to run each "job".

## Description of Data
The dataset contains records of incidents responded to by the Austin Police Department, with reports written from 2003 to the present. It's important to note that one incident may involve multiple offenses, but only the highest level offense is depicted in the dataset. The data is updated weekly, and due to methodological differences, results from different sources may vary. Comparisons between this dataset and other official police reports or Uniform Crime Report statistics should not be made, as the data represents only calls for police service where a report was written. Final totals may vary considerably following investigation and categorization, so caution should be exercised when interpreting the data for analytical purposes.

## Instructions to build a new image from your Dockerfile
- Build a docker image from your Dockerfile: `docker build -t crime_api .`
- Run the docker redis server: `docker run --rm -u $(id -u):$(id -g) -p 6379:6379 -d -v $PWD/data:/data redis:7 --save 1 1`
- (Optional) If data ownership transfer issue exists: `sudo chown ubuntu:ubuntu data/`

## Instructions to launch the containerized app and Redis using docker-compose
- `docker-compose up --build -d`: to start running the docker container (flask app + redis)
- `docker-compose down`: to stop docker container

Note: the environment variable in the Dockerfile is currently called to be 'redis-db' but it's modifiable. Therefore, it can be changed as long as it's changed in the Dockerfile and docker-compose.yml.

## Example Gene-API query commands and expected outputs in code blocks:

- `curl localhost:5000/`: Outputs "Hello, world!"
- `curl localhost:5000/data`: Outputs currently loaded data in database (initially, this should be empty "[]")
- `curl -X GET localhost:5000/data`: Same as the previous route.
- `curl -X POST localhost:5000/data`: Posts dataset to redis database
- `curl -X DELETE localhost:5000/data`: Deletes all data in database

Data querying routes:

See all the available values of the following categories in the dataset (will be generalizing this functionality in next iteration)
- `curl localhost:5000/data/incident_report_numbers`
- `curl localhost:5000/data/crime_types`

Filter the data to view all data where a certain category meets given value (need to generalize in next iteration)
- `curl localhost:5000/data/incident_report_number/<ir_num>`: Returns all data where the incident_report_number equals value <ir_num>
  - e.x. `curl localhost:5000/crimes/20212171325` returns: `{"incident_report_number": "20212171325", "crime_type": "THEFT", "ucr_code": "600", "family_violence": "N", "occ_date_time": "2021-06-07T10:24:00.000", "occ_date": "2021-06-07T00:00:00.000", "occ_time": "1024", "rep_date_time": "2021-06-07T10:24:00.000", "rep_date": "2021-06-07T00:00:00.000", "rep_time": "1024", "location_type": "RESIDENCE / HOME", "address": "500 BLOCK NATALI ST", "zip_code": "78748", "council_district": "2", "sector": "FR", "district": "3", "pra": "537", "census_tract": "24.37", "clearance_status": "N", "clearance_date": "2021-09-06T00:00:00.000", "ucr_category": "23H", "category_description": "Theft", "x_coordinate": "0", "y_coordinate": "0"}`

- `curl localhost:5000/data/crime_type/<crime_type>`: Returns all data where the crime_type equals value <crime_type>
  - e.x. `curl localhost:5000/data/crime_type/PROTECTIVE%20ORDER` returns:
  - [{"incident_report_number": "20135057728", "crime_type": "PROTECTIVE ORDER", "ucr_code": "3829", "family_violence": "N", "occ_date_time": "2013-12-17T09:26:00.000", "occ_date": "2013-12-17T00:00:00.000", "occ_time": "926", "rep_date_time": "2013-12-17T09:26:00.000", "rep_date": "2013-12-17T00:00:00.000", "rep_time": "926", "location_type": "RESIDENCE / HOME", "address": "UNKNOWN", "sector": "AD", "district": "4", "clearance_status": "N", "clearance_date": "2013-12-17T00:00:00.000"}, ... , {"incident_report_number": "20145027129", "crime_type": "PROTECTIVE ORDER", "ucr_code": "3829", "family_violence": "N", "occ_date_time": "2014-06-18T16:09:00.000", "occ_date": "2014-06-18T00:00:00.000", "occ_time": "1609", "rep_date_time": "2014-06-18T16:09:00.000", "rep_date": "2014-06-18T00:00:00.000", "rep_time": "1609", "location_type": "RESIDENCE / HOME", "address": "UNKNOWN", "sector": "ED", "district": "2", "clearance_status": "N", "clearance_date": "2014-06-18T00:00:00.000"}]
 

## Instructions and Examples for Jobs-API (query commands w/ expected outputs):

First, use this POST method to add a new job to the queue, which also shows the job's current status and values. The program is currently only capable of handling the "crime_type" (required) parameter, which must be one of the crime-types in the dataset:
- `curl localhost:5000/jobs -X POST -d '{"crime_type":"THEFT"}' -H "Content-Type: application/json"`
- Example output: `{
  "crime_type": "THEFT",
  "id": "0db41abb-73c7-4e2d-beee-591f8594add3",
  "status": "submitted"
}`

Now, use this GET method along with the specific <jobid> you just received (replace <jobid> with the "id" you received above):
- `curl localhost:5000/jobs/<jobid>`
- Example Output: `{
  "crime_type": "THEFT",
  "id": "0db41abb-73c7-4e2d-beee-591f8594add3",
  "status": "in progress"
}`

You can also use this GET method to show all the running jobs ids:
- `curl localhost:5000/jobs`
- Example output: 
`["6543cfad-94fb-42d0-be89-80e6e836ac1d", "592e39bd-81cf-4f94-9152-700d004fa263", "33c8d95a-fe64-4b0f-b9fe-5ba6df76abc1", "cd4f7a7d-16a9-4dec-89cb-fb21595f4da7", "de9d5aae-762a-4884-80cc-0ffa44af7837", "a6c4ecf3-845d-4bde-a67b-fc51a6f654a0", "38766745-9f55-409c-9ff3-f27585c594da", "78eb42d0-7b7b-44d5-ae51-7d4caa9e7c68", "654edc7d-ea4a-4904-b313-14fa1bb3f9cd", "1e78cdd8-757c-4b19-be19-1e2bc1433a52", "7a6b1bcd-8819-4edb-b2e3-77d099d3402c", "a68ec66f-9d7b-4dfa-aa7b-bf66bd891d03", "99994d99-dc8c-4b37-b6ce-4e9d86f6b5d4", "77b820e3-205e-40a4-80ee-f724cb958a83", "33b55189-f622-4f93-8fd4-4b673d4657e1", "34b2bec1-449d-4571-9337-2b7fb72181ce"]`

Finally, once the results have been loaded, you can use this GET method to load the result:
- `curl localhost:5000/results/<jobid>`
- Example output: `33` (meaning there were 33 instances in the data where crime_type equaled 'THEFT')

## Software Diagram:

![SW diagram](homework08/sw_diagram.png)

## Prerequisites
Before getting started, please ensure that you have the following installed on your system:
- Docker: Install Docker according to your operating system. You can find instructions on the [official Docker website](https://docs.docker.com/get-docker/).
- Redis: enter the following in your CLI: `pip install redis`
- Flask: enter the following in your CLI: `pip install flask`


