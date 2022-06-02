import logging.config

import pandas as pd

# pylint: disable=locally-disabled, invalid-name

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('process-data')


def clean_data(data: pd.DataFrame, target: str) -> pd.DataFrame:
    """
    Clean raw dataframe
    Args:
        data (obj: pd.DataFrame): raw dataframe
        target (str): target column name
    Returns:
        data (obj: pd.DataFrame): cleaned dataframe
    """
    # change churn labels to Yes/No
    try:
        data[target] = data[target].map({0: 'No', 1: 'Yes'})
    except KeyError:
        logger.error("Error: target column not found in the dataset. Please check the target column name.")
        raise KeyError("%s is not in the input dataframe." % target)
    return data
