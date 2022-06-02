"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import os
import argparse
import logging.config

import pickle
import pandas as pd
import yaml

from src.s3 import download_file_from_s3, upload_file_to_s3
from src.process_data import clean_data
from src.create_db import ChurnManager, create_db
from src.modeling import train_model, make_predictions, eval_performance, save_model, save_train_test, save_model_eval
from config.flaskconfig import SQLALCHEMY_DATABASE_URI

logging.config.fileConfig('config/logging/local.conf', disable_existing_loggers=False)
logger = logging.getLogger('run-pipeline')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Running individual step')
    # specify which step to run
    parser.add_argument('step', help='Which step to run',
                        choices=['upload_data', 'acquire_data', 'clean_data',
                                 'create_db', 'ingest_data',
                                 'train_model', 'predict', 'evaluate'])
    parser.add_argument('--config', default='config/config.yaml', help='Path to configuration file')

    parser.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data_test.csv',
                        help="s3 data path to upload/download data")

    parser.add_argument('--local_data_dir', default='data/raw',
                        help='Path to save raw data downloaded from s3')

    parser.add_argument('--cleaned_data_dir', default='data/final', help='Directory to save cleaned data')

    parser.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                        help="SQLAlchemy connection URI for database")

    parser.add_argument("--input_path", default="data/final/final_data_test.csv",
                        help="File path for data to be loaded into the database")

    parser.add_argument("--model_dir", default='models', help='Directory to save trained model object')

    parser.add_argument('--X_train_dir', default='models', help='Directory to save features from training data')

    parser.add_argument('--X_test_dir', default='models',
                        help='Directory to save target column from training data')

    parser.add_argument('--y_train_dir', default='models', help='Directory to save features from test data')

    parser.add_argument('--y_test_dir', default='models', help='Directory to save target column from test data')

    parser.add_argument('--pred_result_dir', default='deliverables', help='Directory to save prediction results')

    # specify directory to save model evaluation results
    parser.add_argument('--model_eval_dir', default='deliverables',
                        help='Directory to save model evaluation results')

    args = parser.parse_args()

    # Load configuration file
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if args.step == 'upload_data':
        upload_file_to_s3(os.path.join(args.local_data_dir, config['s3']['raw_data_name']), args.s3_path)

    elif args.step == 'acquire_data':
        download_file_from_s3(os.path.join(args.local_data_dir, config['s3']['raw_data_name']), args.s3_path)
        logger.info("Raw data acquired and saved to %s",
                    os.path.join(args.local_data_dir, config['s3']['raw_data_name']))
    elif args.step == 'clean_data':
        try:
            data = pd.read_csv(os.path.join(args.local_data_dir, config['s3']['raw_data_name']))
        except FileNotFoundError:
            logger.error("File not found, please run the previous acquire_data step")
        else:
            cleaned_data = clean_data(data, config['process_data']['clean_data']['target'])
            cleaned_data.to_csv(os.path.join(args.cleaned_data_dir, config['process_data']['cleaned_data_filename']),
                                index=False)
            logger.info("Cleaned dataframe saved to %s",
                        os.path.join(args.cleaned_data_dir, config['process_data']['cleaned_data_filename']))
    elif args.step == 'create_db':
        create_db(args.engine_string)

    elif args.step == 'ingest_data':
        cm = ChurnManager(engine_string=args.engine_string)
        cm.add_customer_data(args.input_path)
        cm.close()

    elif args.step == 'train_model':
        try:
            data = pd.read_csv(os.path.join(args.cleaned_data_dir, config['process_data']['cleaned_data_filename']))
        except FileNotFoundError:
            logger.error("File not found, please run each step in order starting from acquire_data")
        else:
            rf, X_train, X_test, y_train, y_test = train_model(data, **config['modeling']['train_model'])
            save_model(rf, os.path.join(args.model_dir, config['modeling']['model_filename']))
            save_train_test(X_train, X_test, y_train, y_test,
                            os.path.join(args.X_train_dir, config['modeling']['X_train_filename']),
                            os.path.join(args.X_test_dir, config['modeling']['X_test_filename']),
                            os.path.join(args.y_train_dir, config['modeling']['y_train_filename']),
                            os.path.join(args.y_test_dir, config['modeling']['y_test_filename']))

    elif args.step == 'predict':
        try:
            with open(os.path.join(args.model_dir, config['modeling']['model_filename']), 'rb') as f:
                rf_model = pickle.load(f)
        except FileNotFoundError:
            logger.error("File not found, please check if model object is saved")

        try:
            X_test = pd.read_csv(os.path.join(args.X_test_dir, config['modeling']['X_test_filename']))
        except FileNotFoundError:
            logger.error("File not found, please check the directory")
        else:
            pred_df = make_predictions(rf_model, X_test)
            # save prediction results
            pred_df.to_csv(os.path.join(args.pred_result_dir, config['modeling']['pred_result_filename']), index=False)
            logger.info("Prediction results saved to %s",
                        os.path.join(args.pred_result_dir, config['modeling']['pred_result_filename']))

    elif args.step == 'evaluate':
        try:
            y_test = pd.read_csv(os.path.join(args.y_test_dir, config['modeling']['y_test_filename']))
            pred_result = pd.read_csv(os.path.join(args.pred_result_dir, config['modeling']['pred_result_filename']))
        except FileNotFoundError:
            logger.error("File not found, please run each step in order or check the directory")
        else:
            accuracy, class_report, conf_mat = eval_performance(pred_result, y_test)
            save_model_eval(accuracy, class_report, conf_mat,
                            os.path.join(args.model_eval_dir, config['modeling']['model_eval_filename']))
            logger.info("Model performance metrics saved to %s",
                        os.path.join(args.model_eval_dir, config['modeling']['model_eval_filename']))