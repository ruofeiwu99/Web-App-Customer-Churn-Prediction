"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

from src.s3 import download_file_from_s3, upload_file_to_s3
from src.create_db import ChurnManager, create_db
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    subparsers = parser.add_subparsers(dest='command')

    sp_download = subparsers.add_parser("download_data", description="Download data from s3")
    sp_download.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data.csv',
                             help="s3 data path to download data")    # CHANGE THIS TO raw/raw_data.csv
    sp_download.add_argument('--local_path', default='data/raw/raw_data.csv',
                             help="local data path to store data")    # CHANGE THIS TO raw/raw_data.csv

    sp_upload = subparsers.add_parser("upload_data", description="Upload data from s3")
    sp_upload.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data.csv',
                           help="s3 data path to upload data")  # CHANGE THIS TO raw/raw_data.csv
    sp_upload.add_argument('--local_path', default='data/raw/raw_data.csv',
                           help="local data path to upload data")  # CHANGE THIS TO raw/raw_data.csv

    # subparser for creating a database
    sp_create = subparsers.add_parser("create_db", description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # subparser for ingesting data from cvs to the table in the database
    sp_ingest = subparsers.add_parser("ingest_data", description="Add data to database")
    sp_ingest.add_argument("--input_path", default="data/raw/raw_data.csv",
                           help="File path for data to be loaded into the database")
    sp_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.command

    if sp_used == 'download_data':
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'upload_data':
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest_data':
        cm = ChurnManager(engine_string=args.engine_string)
        cm.add_customer_data(args.input_path)
        cm.close()
    else:
        parser.print_help()
