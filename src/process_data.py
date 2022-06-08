import logging

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


def validate_input(data: pd.DataFrame) -> pd.DataFrame:
    """
    Validate input dataframe
    Args:
        data (obj: pd.DataFrame): user input data

    Returns:
        data (obj: pd.DataFrame): validated dataframe
    """
    try:
        data['id'] = data['id'].astype(int)
    except ValueError:
        logger.error("Error: ID must be an integer")
        raise ValueError("ID must be an integer")

    try:
        data['number_vmail_messages'] = data['number_vmail_messages'].astype(int)
    except ValueError:
        logger.error("Error: Number of voicemail messages must be an integer")
        raise ValueError("Number of voicemail messages must be an integer")

    try:
        data['total_day_minutes'] = data['total_day_minutes'].astype(float)
    except ValueError:
        logger.error("Error: Total day minutes must be a float")
        raise ValueError("Total day minutes must be a float")

    try:
        data['total_eve_minutes'] = data['total_eve_minutes'].astype(float)
    except ValueError:
        logger.error("Error: Total evening minutes must be a float")
        raise ValueError("Total evening minutes must be a float")

    try:
        data['total_night_minutes'] = data['total_night_minutes'].astype(float)
    except ValueError:
        logger.error("Error: Total night minutes must be a float")
        raise ValueError("Total night minutes must be a float")

    try:
        data['total_intl_minutes'] = data['total_intl_minutes'].astype(float)
    except ValueError:
        logger.error("Error: Total international minutes must be a float")
        raise ValueError("Total international minutes must be a float")

    try:
        data['total_intl_calls'] = data['total_intl_calls'].astype(int)
    except ValueError:
        logger.error("Error: Total international calls must be an integer")
        raise ValueError("Total international calls must be an integer")

    try:
        data['customer_service_calls'] = data['customer_service_calls'].astype(int)
    except ValueError:
        logger.error("Error: Customer service calls must be an integer")
        raise ValueError("Customer service calls must be an integer")

    return data

