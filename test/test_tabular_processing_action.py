from test.fixtures.dataframes import test_dataframe, state_category, categorical_dataframe
from configuration_engine.processing_action.pandas.tabular_processing_action import (
    DropColumn,
    ChangeCategory,
    CategoryToCodes,
)
import pandas as pd
import numpy.testing as npt
import numpy as np
import pytest
from configuration_engine.error import NotFittedError


class TestDropColumn:

    def test_drop_column_inplace(self, test_dataframe: pd.DataFrame):
        action = DropColumn("price")
        action.fit_transform(test_dataframe, True)
        assert npt.assert_array_equal(test_dataframe.columns, ["state"]) == None

    def test_drop_column(self, test_dataframe: pd.DataFrame):
        action = DropColumn("price")
        modified = action.fit_transform(test_dataframe)
        assert (
            npt.assert_array_equal(test_dataframe.columns, ["state", "price"]) == None
        )
        assert npt.assert_array_equal(modified.columns, ["state"]) == None

    def test_transform_before_fit_should_fail(self, test_dataframe: pd.DataFrame):
        action = DropColumn("price")
        with pytest.raises(NotFittedError):
            action.transform(test_dataframe)


class TestChangeCategory:

    def test_change_catgory_inplace(
        self, test_dataframe: pd.DataFrame, state_category: pd.CategoricalDtype
    ):
        action = ChangeCategory("state", state_category)
        action.fit_transform(test_dataframe, True)
        assert test_dataframe["state"].dtype == state_category

    def test_change_category(
        self, test_dataframe: pd.DataFrame, state_category: pd.CategoricalDtype
    ):
        action = ChangeCategory("state", state_category)
        modified = action.fit_transform(test_dataframe, False)
        assert test_dataframe["state"].dtype != state_category
        assert modified["state"].dtype == state_category

    def test_transform_before_fit_should_fail(
        self, test_dataframe: pd.DataFrame, state_category: pd.CategoricalDtype
    ):
        action = ChangeCategory("state", state_category)
        with pytest.raises(NotFittedError):
            action.transform(test_dataframe)


class TestCategoryToCodes:

    def test_category_to_codes_inplace(self, categorical_dataframe: pd.DataFrame):
        action = CategoryToCodes("state")
        action.fit_transform(categorical_dataframe, inplace=True)
        state = np.array(categorical_dataframe["state"])
        assert npt.assert_array_equal(state, np.array([0, 1, 2, 1])) == None

    def test_category_to_codes(self, categorical_dataframe: pd.DataFrame):
        action = CategoryToCodes("state")
        modified = action.fit_transform(categorical_dataframe)
        state = np.array(modified["state"])
        assert npt.assert_array_equal(state, np.array([0, 1, 2, 1])) == None


    def test_transform_noncategorical_column(self, test_dataframe: pd.DataFrame):
        action = CategoryToCodes("state")
        with pytest.raises(ValueError):
            action.fit_transform(test_dataframe)

    def test_transform_before_fit_should_fail(self, test_dataframe: pd.DataFrame):
        action = CategoryToCodes("state")
        with pytest.raises(NotFittedError):
            action.transform(test_dataframe)
