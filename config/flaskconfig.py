import os
DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5001
APP_NAME = "churn-prediction"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 10

# RDS credentials
conn_type = "mysql+pymysql"
host = os.environ.get("MYSQL_HOST")
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")
port = os.environ.get("MYSQL_PORT")
db_name = os.environ.get("DATABASE_NAME")

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
#host = None
#SQLALCHEMY_DATABASE_URI = None

if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif host is None:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///data/data.db'
else:
    SQLALCHEMY_DATABASE_URI = f"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"
