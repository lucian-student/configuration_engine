import pandas as pd
import pytest


@pytest.fixture
def state_category():
    return pd.CategoricalDtype(categories=["used", "new", "worn out"])


@pytest.fixture
def test_dataframe():
    return pd.DataFrame(
        data=[
            {"state": "used", "price": 1},
            {"state": "new", "price": 10},
            {"state": "worn out", "price": 5},
            {"state": "new", "price": 5},
        ]
    )

@pytest.fixture
def categorical_dataframe(test_dataframe:pd.DataFrame,state_category:pd.CategoricalDtype)->pd.DataFrame:
    test_dataframe['state'] = test_dataframe['state'].astype(state_category)
    return test_dataframe
