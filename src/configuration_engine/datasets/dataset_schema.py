from typing import Union
from configuration_engine.parameter import (
    RangeParameterSchema,
    ConstantParameter,
)
from configuration_engine import Base
from configuration_engine.datasets.training_dataset import PandasDataset


class DatasetSchema(Base[PandasDataset]):
    name: str
    path: str
    weight: Union[float, RangeParameterSchema[float]] = 1.0
    cv: bool = False

    def build(self) -> PandasDataset:
        if isinstance(self.weight, float):
            parameter = ConstantParameter[float](name="weight", value=self.weight)
        else:
            parameter = self.weight.build("weight", f"weight_{self.name}")
        return PandasDataset.from_file(
            path=self.path, name=self.name, weight=parameter, cv=self.cv
        )
