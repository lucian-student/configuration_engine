from typing import Optional
from configuration_engine.parameter.tunable_parameter import (
    RangeParameter,
    LiteralParameter,
    CallableParameter,
)
from pydantic import BaseModel
from abc import ABC, abstractmethod
from configuration_engine.utils import resolve_function


class BaseParameter[T](BaseModel, ABC):

    @abstractmethod
    def build(self, name: str, alias: Optional[str] = None) -> T:
        pass


class LiteralParameterSchema[T: (int, float, str, bool)](BaseParameter[T]):
    values: list[T]

    def build(self, name: str, alias: Optional[str] = None) -> LiteralParameter[T]:
        return LiteralParameter(name=name, alias=alias, values=self.values)


class CallableParameterSchema[T](BaseParameter[T]):
    callable: str | list[str]

    def build(self, name: str, alias: Optional[str] = None):
        if isinstance(self.callable, str):
            converted_callables = [resolve_function(self.callable)]
        elif isinstance(self.callable, list) and all(
            isinstance(item, str) for item in self.callable
        ):
            converted_callables = [resolve_function(fn) for fn in self.callable]
        return CallableParameter(name=name, callables=converted_callables, alias=alias)


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
