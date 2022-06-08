import logging
import re
import typing

import boto3
import botocore

logger = logging.getLogger('s3-interaction')


def parse_s3(s3path: str) -> typing.Tuple[str, str]:
    """
    Parse s3 path to get bucket name and file path
    Args:
        s3path (str): path to s3

    Returns:
        s3bucket (str): bucket name
        s3_path (str): file path
    """
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    return s3bucket, s3path


def upload_file_to_s3(local_path: str, s3path: str) -> None:
    """
    Upload raw data to s3
    Args:
        local_path (str): local path to raw data
        s3path (str): s3 path

    Returns:
        None
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.upload_file(local_path, s3_just_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    except FileNotFoundError:
        logger.error('Please check if your local path contains the data you want to upload.')
    else:
        logger.info('Data uploaded from %s to %s', local_path, s3path)


def download_file_from_s3(local_path: str, s3path: str) -> None:
    """
    Download data from s3 and save to local path
    Args:
        local_path (str): local path to save data
        s3path (str): s3 path

    Returns:
        None
    """
    s3bucket, s3_just_path = parse_s3(s3path)

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(s3bucket)

    try:
        bucket.download_file(s3_just_path, local_path)
    except botocore.exceptions.NoCredentialsError:
        logger.error('Please provide AWS credentials via AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables.')
    else:
        logger.info('Data downloaded from %s to %s', s3path, local_path)