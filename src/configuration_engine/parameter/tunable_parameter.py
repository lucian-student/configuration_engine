from abc import ABC, abstractmethod
from typing import Optional, Literal
from optuna import Trial


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


class ConstantParameter[T](Parameter[T]):

    def __init__(self, name: str, value: T, alias: Optional[str] = None):
        super().__init__(name, alias)
        self.value = value

    def suggest(self, trial: Trial) -> T:
        return self.value

    def first(self) -> T:
        return self.value


class LiteralParameter[T: (int, float, str, bool)](Parameter[T]):

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
