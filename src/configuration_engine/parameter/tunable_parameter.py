from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from optuna import Trial
import math


class Parameter[T](ABC):
    """
    Třída reprezentující tunable parametr
    """

    def __init__(self, name: str, alias: Optional[str] = None):
        self.name = name
        self.alias = name if not alias else alias

    @abstractmethod
    def suggest(self, trial: Trial) -> T:
        """
        Value suggested by optuna
        """
        pass

    @abstractmethod
    def first(self) -> T:
        """
        Returns first possible value
        """
        pass

    @abstractmethod
    def __eq__(self, other: Any):
        pass


class ConstantParameter[T](Parameter[T]):

    def __init__(self, name: str, value: T, alias: Optional[str] = None):
        super().__init__(name, alias)
        self.value = value

    def suggest(self, trial: Trial) -> T:
        return self.value

    def first(self) -> T:
        return self.value

    def __eq__(self, other: Any):
        if not isinstance(other, ConstantParameter):
            return False
        if type(self.value) != type(other.value):
            return False
        if isinstance(self.value, float):
            value_condition = math.isclose(self.value, other.value)
        else:
            value_condition = self.value == other.value
        base_condition = self.name == other.name and self.alias == other.alias
        return base_condition and value_condition


class CallableParameter(Parameter[Callable]):

    def __init__(
        self, name: str, callables: list[Callable], alias: Optional[str] = None
    ):
        super().__init__(name, alias)
        self.callables = callables

    def suggest(self, trial: Trial):
        index = trial.suggest_int(
            name=self.alias,
            low=0,
            high=len(self.callables) - 1,
        )
        return self.callables[index]

    def first(self):
        return self.callables[0]

    def __eq__(self, other: Any):
        if not isinstance(other, CallableParameter):
            return False
        return (
            self.name == other.name
            and self.alias == other.alias
            and self.callables == other.callables
        )


class LiteralParameter[T: (int | float | str | bool)](Parameter[T]):

    def __init__(self, name: str, values: list[T], alias: Optional[str] = None):
        super().__init__(name, alias)
        self.values = values

    def suggest(self, trial: Trial):
        index = trial.suggest_int(
            name=self.alias,
            low=0,
            high=len(self.values) - 1,
        )
        return self.values[index]

    def first(self):
        return self.values[0]

    def __eq__(self, other: Any):
        """
        Probably wont work well for literal, that is of type float
        """
        if not isinstance(other, LiteralParameter):
            return False
        for curr_el, other_el in zip(self.values, other.values):
            if type(curr_el) != type(other_el):
                return False
            if isinstance(curr_el, float) and not math.isclose(curr_el, other_el):
                return False
            if curr_el != other_el:
                return False
        return self.name == other.name and self.alias == other.alias


class RangeParameter[T: (int, float)](Parameter[T]):

    def __init__(
        self,
        name: str,
        min: T,
        max: T,
        log: bool,
        step: Optional[T],
        alias: Optional[str] = None,
    ):
        super().__init__(name, alias)
        self.min = min
        self.max = max
        self.log = log
        self.step = step

    def suggest(self, trial: Trial) -> T:
        if isinstance(self.min, int):
            return trial.suggest_int(
                self.alias,
                low=self.min,
                high=self.max,
                log=self.log,
                step=self.step if self.step is not None else 1,
            )
        return trial.suggest_float(
            self.alias, low=self.min, high=self.max, step=self.step, log=self.log
        )

    def first(self):
        return self.min

    def __eq__(self, other: Any):
        if not isinstance(other, RangeParameter):
            return False
        return (
            self.name == other.name
            and self.alias == other.alias
            and math.isclose(self.min, other.min)
            and math.isclose(self.max, other.max)
            and (
                (self.step is None and other.step is None)
                or (
                    self.step is not None
                    and other.step is not None
                    and math.isclose(self.step, other.step)
                )
            )
            and self.log == other.log
        )


class MultiParameter[T](Parameter[T]):

    def __init__(
        self,
        name: str,
        parameters: list[Parameter[T]],
        alias: Optional[str] = None,
    ):
        super().__init__(name, alias)
        self.parameters = parameters

    def suggest(self, trial: Trial) -> T:
        index = trial.suggest_int(
            name=self.alias,
            low=0,
            high=len(self.parameters) - 1,
        )
        return self.parameters[index].suggest(trial)

    def __eq__(self, other: Any):
        if not isinstance(other, MultiParameter):
            return False
        return (
            self.name == other.name
            and self.alias == other.alias
            and self.parameters == other.parameters
        )
