from typing import Optional, Callable
from configuration_engine.parameter.tunable_parameter import (
    RangeParameter,
    LiteralParameter,
    ClassCallableParameter,
    MultiParameter,
    Parameter,
)
from pydantic import BaseModel
from abc import ABC, abstractmethod
from configuration_engine.utils import resolve_function


class Tunable:
    pass


class BaseParameter[T](BaseModel, ABC):

    @abstractmethod
    def build(self, name: str, alias: Optional[str] = None) -> T:
        pass


class LiteralParameterSchema[T: (int | float | str | bool)](
    BaseParameter[LiteralParameter[T]]
):
    values: list[T]

    def build(self, name: str, alias: Optional[str] = None) -> LiteralParameter[T]:
        return LiteralParameter(name=name, alias=alias, values=self.values)


class ClassCallableSchema(BaseParameter[ClassCallableParameter]):
    callable_class: str | list[str]

    def build(self, name: str, alias: Optional[str] = None) -> ClassCallableParameter:
        if isinstance(self.callable_class, str):
            converted_callables = [resolve_function(self.callable_class)()]
        elif isinstance(self.callable_class, list) and all(
            isinstance(item, str) for item in self.callable_class
        ):
            converted_callables = [
                resolve_function(fn)() for fn in self.callable_class
            ]
        return ClassCallableParameter(
            name=name, callables=converted_callables, alias=alias
        )


class RangeParameterSchema[RangeType: (int, float)](
    BaseParameter[RangeParameter[RangeType]]
):
    min: RangeType
    max: RangeType
    step: Optional[RangeType] = None
    log: bool = False

    def build(
        self, name: str, alias: Optional[str] = None
    ) -> RangeParameter[RangeType]:
        return RangeParameter[RangeType](
            name=name,
            alias=alias,
            min=self.min,
            max=self.max,
            step=self.step,
            log=self.log,
        )


class MultiParameterSchema[SCHEMA: (BaseParameter), PARAM: (Parameter)](
    BaseParameter[MultiParameter[PARAM]]
):
    parameters: list[SCHEMA]

    def build(self, name: str, alias: Optional[str] = None):
        alias = alias or name
        return MultiParameter(
            name=name,
            parameters=[
                s.build(name=f"{name}_{i}", alias=f"{alias}_{i}")
                for i, s in enumerate(self.parameters)
            ],
            alias=alias,
        )


MultiFloatRangeSchema = MultiParameterSchema[
    RangeParameterSchema[float], RangeParameter[float]
]
MultiIntRangeSchema = MultiParameterSchema[
    RangeParameterSchema[int], RangeParameter[int]
]
