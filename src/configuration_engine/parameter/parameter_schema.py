from typing import Optional
from configuration_engine.parameter.tunable_parameter import RangeParameter
from pydantic import BaseModel
from abc import ABC, abstractmethod


class BaseParameter[T](BaseModel, ABC):

    @abstractmethod
    def build(self, name: str, alias: Optional[str] = None) -> T:
        pass


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
