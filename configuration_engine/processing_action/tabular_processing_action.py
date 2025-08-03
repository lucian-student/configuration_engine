from abc import ABC, abstractmethod
import pandas as pd
from configuration_engine import NotFittedError, error_message
from configuration_engine.constants import *
from typing import overload, Literal, Union


class TabularProcessingAction(ABC):

    def __init__(self):
        super().__init__()
        self._is_fitted = False

    @abstractmethod
    def fit(self, X: pd.DataFrame):
        pass

    @overload
    def transform(self, X: pd.DataFrame, inplace: Literal[True]) -> None: ...

    @overload
    def transform(self, X: pd.DataFrame, inplace: Literal[False]) -> pd.DataFrame: ...

    @abstractmethod
    def transform(
        self, X: pd.DataFrame, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        """
        Raises:
            NotFittedError: if method fit wasn't called before.
        """
        if not self.is_fit():
            raise NotFittedError(
                error_message(
                    f"{MODULE_NAME}:{self.__class__}",
                    "fit",
                    "U can't transform data before fitting!",
                )
            )
        return X

    @overload
    def fit_transform(self, X: pd.DataFrame, inplace: Literal[True]) -> None: ...

    @overload
    def fit_transform(
        self, X: pd.DataFrame, inplace: Literal[False]
    ) -> pd.DataFrame: ...

    @abstractmethod
    def fit_transform(
        self, X: pd.DataFrame, inplace: bool = False
    ) -> Union[None, pd.DataFrame]:
        pass

    def is_fit(self) -> bool:
        return self._is_fitted


class DropColumn(TabularProcessingAction):

    def __init__(self, column: str):
        super().__init__()
        self.column = column

    def fit(self, X: pd.DataFrame):
        super().fit(X)
        self._is_fitted = True

    def transform(self, X: pd.DataFrame, inplace: bool = False):
        """
        Raises:
            ValueError: when column doesn't exist!
            NotFittedError: if method fit wasn't called before.
        """
        super().transform(X)
        if self.column not in X.columns:
            raise ValueError(
                error_message(
                    f"{MODULE_NAME}:{self.__class__}",
                    "drop column",
                    f"Pandas dataframe doesn't contain column {self.column}!",
                )
            )
        return X.drop(columns=[self.column], inplace=inplace)

    def fit_transform(self, X, inplace=False):
        """
        ValueError: when column doesn't exist!
        """
        self.fit(X)
        return self.transform(X, inplace)


class ChangeCategory(TabularProcessingAction):

    def __init__(self, column: str, category: pd.CategoricalDtype):
        super().__init__()
        self.column = column
        self.category = category

    def fit(self, X: pd.DataFrame):
        super().fit(X)
        self._is_fitted = True

    def change_category(self, X: pd.DataFrame):
        X[self.column] = X[self.column].astype(self.category)

    def transform(self, X: pd.DataFrame, inplace: bool = False):
        """
        Raises:
            ValueError: when column doesn't exist!
            NotFittedError: if method fit wasn't called before.
        """
        super().transform(X)
        if self.column not in X.columns:
            raise ValueError(
                error_message(
                    f"{MODULE_NAME}:{self.__class__}",
                    "change category",
                    f"Pandas dataframe doesn't contain column {self.column}!",
                )
            )
        if inplace:
            self.change_category(X)
            return

        copy = X.copy()
        self.change_category(copy)
        return copy

    def fit_transform(self, X, inplace=False):
        """
        Raises:
            ValueError: when column doesn't exist!
        """
        self.fit(X)
        return self.transform(X, inplace)


class CategoryToCodes(TabularProcessingAction):

    def __init__(self, column: str):
        super().__init__()
        self.column = column

    def fit(self, X):
        super().fit(X)
        self._is_fitted = True

    def to_codes(self, X: pd.DataFrame):
        X[self.column] = X[self.column].cat.codes

    def transform(self, X: pd.DataFrame, inplace: bool = False):
        """
        Raises:
            ValueError: when column doesn't exist!
            NotFittedError: if method fit wasn't called before.
        """
        super().transform(X)
        if self.column not in X.columns:
            raise ValueError(
                error_message(
                    f"{MODULE_NAME}:{self.__class__}",
                    "category to codes",
                    f"Pandas dataframe doesn't contain column {self.column}!",
                )
            )
        try:
            if inplace:
                self.to_codes(X)
                return
            copy = X.copy()
            self.to_codes(copy)
        except AttributeError:
            raise ValueError(
                error_message(
                    f"{MODULE_NAME}:{self.__class__}",
                    "category to codes",
                    f"Column isn't categorical {self.column}!",
                )
            )
        return copy

    def fit_transform(self, X, inplace=False):
        """
        Raises:
            ValueError: when column doesn't exist!
        """
        self.fit(X)
        return self.transform(X, inplace)
