from typing import List, Union, Literal, Dict
from pydantic import BaseModel
from configuration_engine.processing_action.pandas import (
    DropColumn,
    ChangeCategory,
    CategoryToCodes,
    TabularProcessingAction,
)
from pydantic import BaseModel
from abc import ABC, abstractmethod
import pandas as pd


class BaseColumnActionSchema[T](BaseModel, ABC):

    @abstractmethod
    def build(self, column: str) -> T:
        pass


class DropColumnSchema(BaseColumnActionSchema[DropColumn]):
    name: Literal["drop"]

    def build(self, column: str) -> DropColumn:
        return DropColumn(column=column)


class CategoryToCodesSchema(BaseColumnActionSchema[CategoryToCodes]):
    name: Literal["codes"]

    def build(self, column: str) -> CategoryToCodes:
        return CategoryToCodes(column=column)


class ChangeCategorySchema(BaseModel):
    name: Literal["category_change"]
    category: str

    def build(self, column, categories: Dict[str, pd.CategoricalDtype]):
        return ChangeCategory(column, categories[self.category])


class TabularColumnActionSchema(BaseModel):
    column: str
    actions: List[Union[DropColumnSchema, CategoryToCodesSchema, ChangeCategorySchema]]

    def build(
        self, categories: Dict[str, pd.CategoricalDtype]
    ) -> List[TabularProcessingAction]:
        converted: List[TabularProcessingAction] = []
        for action in self.actions:
            if isinstance(action, BaseColumnActionSchema):
                converted.append(action.build(self.column))
            elif isinstance(action, ChangeCategorySchema):
                converted.append(action.build(self.column, categories))
        return converted


class TabularActionSchema(BaseModel):
    pass
