# Developing focused customer retention program through a customer churn model
Author: Ruofei Wu

# Table of Contents
* [Project charter ](#Project-charter)
* [Directory structure ](#Directory-structure)
* [Running the model pipeline ](#Running-the-model-pipeline)
* [Running the app ](#Running-the-app)
    * [1. Initialize the database ](#1.-Initialize-the-database)
    * [2. Configure Flask app ](#2.-Configure-Flask-app)
    * [3. Run the Flask app ](#3.-Run-the-Flask-app)
* [Testing](#Testing)
* [Pylint](#Pylint)

## Project charter
### Background
The telecommunication industry is a highly competitive market 
where customers can choose from various service providers and actively 
switch from one operator to another. Based on some research, the telecom 
industry experiences 15-25% annual churn rate on average. Given the fact 
that it costs more to acquire a new customer than to retain an existing one, 
customer retention has become more important than customer acquisition. 
Therefore, it is highly important to predict which customers are at risk of 
churn so that the Orange Telecom company can come up with certain strategies
to retain existing customers.

### Vision
Retain existing customers, reduce customer churn

### Mission
Using the data provided (https://www.kaggle.com/datasets/mnassrib/telecom-churn-datasets), 
a customer churn prediction model that provides accurate predictions 
regarding which customers are at high risk of churn using customer 
activity data will be built to help the Orange Telecom company develop 
focused customer retention program. With the input of customer activity 
related features, the model will output a churn label indicating whether 
the customer is likely to cancel the subscription.

### Success Criteria
* Model Performance Metrics
  * Misclassification Rate 
  * Confusion Matrix
  * Accepted Criteria - Misclassification Rate < 20%, i.e., Accuracy > 80%
* Business Metrics
  * Fraction of customers retained for one year
  * Average customer lifetime

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs│    
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── final/                        <- Final data that has been cleaned and prepared for use in the model
│   ├── raw/                          <- Raw data that is not yet processed, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│   ├── final_presentation.pdf        <- Final presentation for the project
│   
├── dockerfiles/                      <- Directory for all project-related Dockerfiles 
│   ├── Dockerfile                    <- Dockerfile for building image to run the pipeline  
│   ├── Dockerfile.app                <- Dockerfile for building image to run web app
│   ├── Dockerfile.test               <- Dockerfile for building image to run unit tests
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project. No executable Python files should live in this folder.  
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the web app 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```

## Running the Model Pipeline
### 1. File Path Configurations (Optional)
By default:
* Raw data will be saved to the `data/raw` directory, final data after processing will be saved to the `data/final` directory,
and train/test data for modeling will be saved to the `models` folder.
* Trained random forest model object will be saved to the `models` directory.
* Prediction results and model evaluations will be saved to the `deliverables` directory.

If you want to make changes to file paths, you can change the corresponding command line arguments.

### 2. Running Entire Model Pipeline
To run the entire model pipeline, run the following command:
```bash
docker build -f dockerfiles/Dockerfile.pipeline -t final-project-pipeline .
```

```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project-pipeline run-pipeline.sh
```

### 3. Executing Each Step in the Model Pipeline
#### 3.1 Build docker image
```bash
docker build -f dockerfiles/Dockerfile -t final-project .
```
#### 3.2 Download data from S3 bucket
```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY final-project run.py acquire_data
```
#### 3.3 Clean raw data
The following command will clean the raw data and save it to the `data/final` directory:
```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py clean_data
```
#### 3.4 Train the model
The following command will perform train-test split, build a random forest model on the training 
set, and save the trained model object to the `models` directory:
```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py train_model
```
#### 3.5 Generate predictions
The following command will generate predictions on the test set and save them to the `deliverables` directory:
```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py predict
```
#### 3.6 Evaluate model performance
The following command will calculate accuracy, generate a classification report and a confusion
matrix to evaluate the model performance and save the evaluation metrics to the `deliverables` directory:
```bash
docker run --mount type=bind,source="$(pwd)",target=/app/ final-project run.py evalaute
```

## Running the app 

### 1. Initialize the database 
#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
docker build -f dockerfiles/Dockerfile -t final-project .
```
#### Create the database 
To create the database specified in the environment variable `SQLALCHEMY_DATABASE_URI`, 
run the following command:

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ -e SQLALCHEMY_DATABASE_URI final-project run.py create_db
```
The `--mount` argument allows the app to access your local `data/` folder and save the SQLite database there 
so that it is available after the Docker container finishes.

#### Defining your engine string 
A SQLAlchemy database connection is defined by a string with the following format:

`dialect://user:password@host:port/database`
 
##### Local SQLite database 

A local SQLite database can be created for development and local testing. It does not require a username or password and replaces the host and port with the path to the database file: 

`sqlite:///data/{databasename}.db`
The three `///` denote that it is a relative path to where the code is being run (which is from the root of this directory).


### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5001 # What port to expose app on. Must be the same as the port exposed in dockerfiles/Dockerfile.app 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 10 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

#### Build the image 

To build the image, run from this directory (the root of the repo): 

```bash
docker build -f dockerfiles/Dockerfile.app -t final-project-app .
```

This command builds the Docker image, with the tag `final-project-app`, based on the instructions in `dockerfiles/Dockerfile.app` and the files existing in this directory.

#### Running the app

To run the Flask app, run: 

```bash
docker run --mount type=bind,source="$(pwd)"/data,target=/app/data/ -p 5001:5001 -e SQLALCHEMY_DATABASE_URI final-project-app
```
You should be able to access the app at http://0.0.0.0:5001/ in your browser.

The arguments in the above command do the following: 

* The `--name test-app` argument names the container "test". This name can be used to kill the container once finished with it.
* The `--mount` argument allows the app to access your local `data/` folder so it can read from the SQLlite database created in the prior section. 
* The `-p 5001:5001` argument maps your computer's local port 5001 to the Docker container's port 5001 so that you can view the app in your browser. If your port 5000 is already being used for someone, you can use `-p 5001:5000` (or another value in place of 5001) which maps the Docker container's port 5000 to your local port 5001.

Note: If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5001` line in `dockerfiles/Dockerfile.app`)


#### Kill the container 

Once finished with the app, you will need to kill the container. If you named the container, you can execute the following: 

```bash
docker kill <container_name>
```
The container name can be found by running the following:

```bash 
docker container ls
```

The name will be provided in the right most column. 

## Testing

Run the following:
```bash
docker build -f dockerfiles/Dockerfile.test -t final-project-tests .
```

To run the tests, run:
```bash
docker run final-project-tests
```

The following command will be executed within the container to run the provided unit tests under `test/`:
```bash
python -m pytest
```

## Pylint

Run the following:

```bash
docker build -f dockerfiles/Dockerfile.pylint -t final-project-pylint .
```

To run pylint for a file, run:

```bash
docker run final-project-pylint run.py 
```

(or any other file name, with its path relative to where you are executing the command from)
