"""Configures the subparsers for receiving command line arguments for each
 stage in the model pipeline and orchestrates their execution."""
import argparse
import logging.config

from src.s3 import download_file_from_s3, upload_file_to_s3

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('__name__')

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(
        description="Create and/or add data to database")
    parser.add_argument('--download', default=False, action='store_true',
                        help="If True, will download the data from S3. If False, will upload data to S3")

    parser.add_argument('--s3_path', default='s3://2022-msia423-wu-ruofei/raw/raw_data.csv',
                        help="s3 data path to download or upload data")

    parser.add_argument('--local_path', default='data/raw/raw_data.csv',
                        help="local data path to store or upload data")

    args = parser.parse_args()

    if args.download:
        download_file_from_s3(args.local_path, args.s3_path)
    else:
        upload_file_to_s3(args.local_path, args.s3_path)



