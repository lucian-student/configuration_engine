from abc import ABC, abstractmethod
from typing import Any
import math


class NontunableParameter[T](ABC):

    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def value(self) -> T:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def __eq__(self, other: Any):
        pass


class ConstantNontunableParameter[T](NontunableParameter[T]):

    def __init__(self, name: str, value: T):
        super().__init__(name)
        self._value = value

    def name(self):
        return self._name

    def value(self):
        return self._value

    def __eq__(self, other: Any):
        if not isinstance(other, ConstantNontunableParameter):
            return False
        if type(self.value()) != type(other.value()):
            return False
        if isinstance(self.value(), float):
            value_condition = math.isclose(self.value(), other.value())
        else:
            value_condition = self.value() == other.value()
        base_condition = self.name() == other.name()
        return base_condition and value_condition
