from abc import ABC,abstractmethod
from  typing import Dict
import io

class Logger(ABC):

    @abstractmethod
    def stream(self) -> io.TextIOBase:
        pass

    @abstractmethod
    def log(self,data:Dict):
        pass

    def close(self):
        self.stream().close()