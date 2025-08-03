from pydantic import BaseModel
from abc import ABC,abstractmethod

class Base[T](BaseModel,ABC):

    @abstractmethod
    def build(self)->T:
        pass