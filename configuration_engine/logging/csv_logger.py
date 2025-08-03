import csv
import io
from configuration_engine.logging.logger import Logger
from typing import Dict, Set, Protocol, Iterable, Any
import os
from abc import abstractmethod
from configuration_engine.error import error_message
from configuration_engine.constants import *


class CSVWriter(Protocol):
    def writerow(self, row: Iterable[Any]) -> Any: ...
    def writerows(self, rows: Iterable[Iterable[Any]]) -> None: ...


class CSVLogger(Logger):

    def __init__(self):
        self.headers: Set[str] = set()

    def log(self, data: Dict):
        """
        throws ValueError
        """
        if self.first_row():
            self.headers = set(data.keys())
            self.writer().writerow(data.keys())
            self.set_first_row(False)

        keys = set(data.keys())
        if keys != self.headers:
            raise ValueError(
                error_message(
                    MODULE_NAME,
                    "csv log",
                    f"Headers don't match {self.headers} != {keys}  !",
                )
            )
        self.writer().writerow([data[key] for key in self.headers])
        self.stream().flush()

    @abstractmethod
    def writer(self) -> CSVWriter:
        pass

    @abstractmethod
    def first_row(self) -> bool:
        pass

    @abstractmethod
    def set_first_row(self, val: bool):
        pass


class CSVFileLogger(CSVLogger):

    def __init__(self, path: str):
        super().__init__()
        """
        Raises:
            OSError
        """
        self._first_row = True
        if os.path.exists(path):
            self._first_row = False
        self._stream = open(path, "a", newline="")
        self._writer = csv.writer(self._stream)

    def stream(self):
        return self._stream

    def first_row(self):
        return self._first_row

    def set_first_row(self, val):
        self._first_row = val

    def writer(self) -> CSVWriter:
        return self._writer


class CSVStringLogger(CSVLogger):

    def __init__(self):
        super().__init__()
        self._stream = io.StringIO()
        self._first_row = True
        self._writer = csv.writer(self._stream)

    def stream(self):
        return self._stream

    def first_row(self):
        return self._first_row

    def set_first_row(self, val):
        self._first_row = val

    def writer(self) -> CSVWriter:
        return self._writer


"""
class CSVLogger(Logger):

    def __init__(
        self,
        path: str,
        headers: List[str],
        defaults: Optional[Dict[str, Union[str, int, float]]],
        flush_each_row: bool = False,
    ):
        super().__init__()
        self.path = path
        self.headers = headers
        self.defaults = defaults
        self.flush_each_row = flush_each_row

        try:
            # jestli soubor existuje, tak vytvořit a zapsat headery jinak pouze otveřít
            if not os.path.isfile(path):
                createHeader = True
            else:
                createHeader = False

            self.file = open(self.path, "a", newline="")
            self.writer = csv.writer(self.file)

            if createHeader:
                self.writer.writerow(headers)
                if self.flush_each_row:
                    self.file.flush()
        except OSError:
            raise LoggerFailure(f"{__name__}: Failed to open file {self.path}!")

    def __del__(self):
        self.file.close()

    def log(self, data: Dict[str, Union[str, int, float]]):
        try:
            row = []
            for header in self.headers:
                if header in data:
                    row.append(data[header])
                else:
                    if self.defaults and header in self.defaults:
                        row.append(self.defaults[header])
                    else:
                        row.append("")
            self.writer.writerow(row)
            if self.flush_each_row:
                self.file.flush()
        except OSError:
            raise LoggerFailure(f"{__name__}: Failed to write to file {self.path}!")
"""
