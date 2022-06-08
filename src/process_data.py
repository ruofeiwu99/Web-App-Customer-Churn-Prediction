import logging
from typing import List

import pandas as pd

# pylint: disable=locally-disabled, invalid-name

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
    except KeyError as e:
        logger.error('Error: target column %s not found in the dataset. Please check the target column name.', target)
        raise KeyError(f'{target} is not in the input dataframe.') from e

    return data


def validate_input(data: pd.DataFrame, int_cols: List[str], numeric_cols: List[str]) -> pd.DataFrame:
    """
    Validate user input data
    Args:
        data (obj: pd.DataFrame): raw dataframe containing user input
        int_cols (List[str]): list of integer columns
        numeric_cols (List[str]): list of numeric columns

    Returns:
        data (obj: pd.DataFrame): validated user input data
    """

    for col in data.columns:
        if col in int_cols:
            try:
                data[col] = data[col].astype(int)
            except ValueError:
                logger.error('Error: %s must be an integer', col)
                raise ValueError(f'{col} must be an integer')
            else:
                if data[col].item() < 0:
                    logger.error('Error: %s must be greater than or equal to 0', col)
                    raise ValueError(f'{col} must be greater than or equal to 0')
        elif col in numeric_cols:
            try:
                data[col] = data[col].astype(float)
            except ValueError:
                logger.error('Error: %s must be numeric', col)
                raise ValueError(f'{col} must be numeric')
            else:
                if data[col].item() < 0:
                    logger.error('Error: %s must be greater than or equal to 0', col)
                    raise ValueError(f'{col} must be greater than or equal to 0')
    return data
