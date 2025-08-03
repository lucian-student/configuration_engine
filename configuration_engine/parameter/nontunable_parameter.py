from abc import ABC, abstractmethod


class NontunableParameter[T](ABC):

    @abstractmethod
    def value(self) -> T:
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class ConstantNontunableParameter[T](NontunableParameter[T]):

    def __init__(self, name: str, value: T):
        self._name = name
        self._value = value

    def name(self):
        return self._name

    def value(self):
        return self._value
