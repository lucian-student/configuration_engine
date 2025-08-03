import pandas as pd
from configuration_engine.parameter import Parameter
from abc import ABC
from typing import Optional
import pathlib
from configuration_engine.error import error_message
from configuration_engine.constants import *


class BaseDataset(ABC):
    pass


class PandasDataset(BaseDataset):

    @staticmethod
    def from_file(path: str, name: str, weight: Parameter[float], cv: bool):
        """
        Raise:
            OSError
            ValueError
        """
        suffix = pathlib.Path(path).suffix
        match suffix:
            case ".csv":
                data = pd.read_csv(path)
            case ".parquet":
                data = pd.read_csv(path)
            case _:
                raise ValueError(
                    error_message(
                        MODULE_NAME,
                        "from_file",
                        f"Couln't determine extension of file {path}!",
                    )
                )
        return PandasDataset(data=data, name=name, weight=weight, cv=cv, path=path)

    def __init__(
        self,
        data: pd.DataFrame,
        name: str,
        weight: Parameter[float],
        cv: bool,
        path: Optional[str] = None,
    ):
        """
        cv: říká jestli data z datasetu můžou patříti mezi validační data v rámci cross validace
        """
        self.data = data
        self.name = name
        self.weight = weight
        self.cv = cv
        self.path = path
