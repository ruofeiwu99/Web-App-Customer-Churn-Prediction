import os
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

# RDS credentials
conn_type = "mysql+pymysql"
host = os.environ.get("MYSQL_HOST")
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
port = os.environ.get("MYSQL_PORT")
db_name = os.environ.get("DATABASE_NAME")

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    if host is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'
    else:
        SQLALCHEMY_DATABASE_URI = "{conn_type}://{user}:{password}@{host}:{port}/{db_name}"

# file paths
DATA_PATH = os.environ.get('DATA_PATH')
if DATA_PATH is None:
    DATA_PATH = 'raw/telecom_churn_data.csv'
