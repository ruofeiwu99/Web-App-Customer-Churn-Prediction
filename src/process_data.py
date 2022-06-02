import logging.config

import pandas as pd

# pylint: disable=locally-disabled, invalid-name

logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('process-data')


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw dataframe
    Args:
        data (obj: pd.DataFrame): raw dataframe
    Returns:
        data (obj: pd.DataFrame): cleaned dataframe
    """
    # change churn labels to Yes/No
    data['churn'] = data['churn'].map({0: 'No', 1: 'Yes'})
    return data
