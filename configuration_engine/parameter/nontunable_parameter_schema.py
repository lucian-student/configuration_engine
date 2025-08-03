from pydantic import BaseModel
from abc import ABC,abstractmethod

class BaseNontunableParameter[T](BaseModel,ABC):

    @abstractmethod
    def build(self, name: str) -> T:
        pass

