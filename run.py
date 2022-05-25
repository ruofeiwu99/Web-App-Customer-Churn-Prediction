"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

import yaml

from src.s3 import download_file_from_s3, upload_file_to_s3
from src.data_handling import process_data
from src.create_db import ChurnManager, create_db
from src.modeling import train_model, make_predictions, eval_performance
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    parser.add_argument('--config', default='config/config.yaml',
                        help='Path to configuration file')

    subparsers = parser.add_subparsers(dest='command')

    sp_download = subparsers.add_parser("download_data", description="Download data from s3")
    sp_download.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data.csv',
                             help="s3 data path to download data")    # CHANGE THIS TO raw/raw_data.csv
    sp_download.add_argument('--local_path', default='data/raw/raw_data.csv',
                             help="local data path to store data")    # CHANGE THIS TO raw/raw_data.csv

    sp_upload = subparsers.add_parser("upload_data", description="Upload data from s3")
    sp_upload.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data.csv',
                           help="s3 data path to upload data")
    sp_upload.add_argument('--local_path', default='data/raw/raw_data.csv',
                           help="local data path to upload data")
    # subparser for processing data
    sp_process = subparsers.add_parser("process_raw", description="Process raw data")

    # subparser for creating a database
    sp_create = subparsers.add_parser("create_db", description="Create database")
    sp_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # subparser for ingesting data from cvs to the table in the database
    sp_ingest = subparsers.add_parser("ingest_data", description="Add data to database")
    sp_ingest.add_argument("--input_path", default="data/final/final_data.csv",
                           help="File path for data to be loaded into the database")
    sp_ingest.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # subparser for training the model
    sp_train = subparsers.add_parser("train_model",
                                     description="Train model and save trained model object")
    # subparser for making predictions on the test set
    sp_predict = subparsers.add_parser("predict",
                                       description="Produce predictions from saved model")
    # subparser for evaluating the model performance
    sp_evaluate = subparsers.add_parser("evaluate",
                                        description="Evaluate the model performance and save the result")

    args = parser.parse_args()
    sp_used = args.command

    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if sp_used == 'download_data':
        download_file_from_s3(args.local_path, args.s3_path)
    elif sp_used == 'upload_data':
        upload_file_to_s3(args.local_path, args.s3_path)
    elif sp_used == 'process_raw':
        process_data(**config['data_handling']['process_data'])
        logger.info("Final data saved.")
    elif sp_used == 'create_db':
        create_db(args.engine_string)
    elif sp_used == 'ingest_data':
        cm = ChurnManager(engine_string=args.engine_string)
        cm.add_customer_data(args.input_path)
        cm.close()

    elif sp_used == 'train_model':
        train_model(**config['modeling']['train_model'])
        logger.info("Random forest model saved.")
    elif sp_used == 'predict':
        make_predictions(**config['modeling']['make_predictions'])
        logger.info("Prediction results saved.")
    elif sp_used == 'evaluate':
        eval_performance(**config['modeling']['eval_performance'])
        logger.info("Model performance metrics saved.")

    else:
        parser.print_help()
