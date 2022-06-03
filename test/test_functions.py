import pytest
import pandas as pd

from src.process_data import clean_data
from src.modeling import select_target, select_features

# pylint: disable=locally-disabled, invalid-name


def test_select_target_valid_input():
    """
    Test select_target function with valid input
    """
    # load file for testing
    data = pd.read_csv("test/unit_test_data/final_data_test.csv")
    output_true = data['churn']
    output_test = select_target(data, 'churn')
    assert output_test.equals(output_true)


def test_select_target_invalid_input():
    """
    Test select_target function with invalid input
    """
    # load file for testing
    data = pd.read_csv("test/unit_test_data/final_data_test.csv")
    with pytest.raises(KeyError):
        select_target(data, 'invalid_churn')


def test_select_features_valid_input():
    """
    Test select_features function with valid input
    """
    # load file for testing
    data = pd.read_csv("test/unit_test_data/final_data_test.csv")
    output_true = data[['churn', 'account_length']]
    output_test = select_features(data, ['churn', 'account_length'])
    # Test that the true and test are the same
    pd.testing.assert_frame_equal(output_true, output_test)


def test_select_features_empty_input():
    """
    Test select_features function with empty input
    """
    # load file for testing
    data = pd.read_csv("test/unit_test_data/final_data_test.csv")
    output_true = pd.DataFrame()
    output_test = select_features(data, [])
    # Test that the true and test are the same
    assert output_test.equals(output_true)


def test_select_features_invalid_input():
    """
    Test select_features function with invalid input
    """
    # load file for testing
    data = pd.read_csv("test/unit_test_data/final_data_test.csv")
    output_true = pd.DataFrame()
    output_test = select_features(data, ['invalid_churn', 'invalid_account_length'])
    # Test that the true and test are the same
    assert output_test.equals(output_true)


def test_clean_data_valid_input():
    """
    Test clean_data function with valid input
    """
    # load file for testing
    raw_data = pd.read_csv("test/unit_test_data/raw_data_test.csv")
    output_true = pd.read_csv("test/unit_test_data/final_data_test.csv")
    output_test = clean_data(raw_data, 'churn')
    # Test that the true and test are the same
    assert output_test.equals(output_true)


def test_clean_data_invalid_input():
    """
    Test clean_data function with invalid column name
    """
    # load file for testing
    raw_data = pd.read_csv("test/unit_test_data/raw_data_test.csv")
    with pytest.raises(KeyError):
        clean_data(raw_data, 'invalid_churn')
