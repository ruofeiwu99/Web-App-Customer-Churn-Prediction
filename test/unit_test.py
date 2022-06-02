import pytest

import pandas as pd




"""
Test select_target function
"""
def test_select_target_valid_input():
    """
    Test select_target function with valid input
    """
    data = pd.DataFrame({'id': [1, 2, 3], 'target': [1, 0, 1]})
    target = 'target'
    assert select_target(data, target) is not None
    Returns:

    """