from pydantic import Field
from configuration_engine.processing_action import (
    TabularColumnActionSchema,
    TabularProcessingAction,
)
from typing import List, Dict, Union, Any
from configuration_engine.parameter import (
    RangeParameterSchema,
    Parameter,
    BaseParameter,
    ConstantParameter,
    NontunableParameter,
    ConstantNontunableParameter,
)
from configuration_engine.datasets import DatasetSchema
from pydantic import BaseModel
from configuration_engine.configuration import (
    TabularConfiguration,
)
from configuration_engine.datasets import PandasDataset
from configuration_engine.configuration.metadata import Metadata
import pandas as pd


ParameterType = Union[
    RangeParameterSchema[int],
    RangeParameterSchema[float],
    int,
    float,
    str,
    bool,
    List[str],
]


class TabularSchema(BaseModel):
    metadata: Metadata
    tuner_parameters: Dict[str, Union[int, float, str, bool]]
    additional_parameters: Dict[str, Union[int, float, str, bool]]
    training_datasets: List[DatasetSchema]
    training_parameters: Dict[str, ParameterType]
    model_parameters: Dict[str, ParameterType]
    preprocessing: List[TabularColumnActionSchema] = Field(default_factory=list)

    def convert_paramaeters(
        self,
        parameters: Dict[str, ParameterType],
    ) -> List[Parameter]:
        converted: List[Parameter] = []
        for key, val in parameters.items():
            if isinstance(val, BaseParameter):
                converted.append(val.build(key))
            else:
                converted.append(ConstantParameter(name=key, value=val))
        return converted

    def build(self, categories: Dict[str, pd.CategoricalDtype]) -> TabularConfiguration:
        converted_training_datasets: List[PandasDataset] = []

        for dataset in self.training_datasets:
            converted_training_datasets.append(dataset.build())
        converted_training_parameters: List[Parameter[Any]] = self.convert_paramaeters(
            self.training_parameters
        )
        converted_model_parameters: List[Parameter[Any]] = self.convert_paramaeters(
            self.model_parameters
        )
        converted_preprocessing: List[TabularProcessingAction] = []
        for action in self.preprocessing:
            for converted_action in action.build(categories):
                converted_preprocessing.append(converted_action)

        converted_tuner_parameters: List[NontunableParameter[Any]] = []
        for key, val in self.tuner_parameters.items():
            converted_tuner_parameters.append(
                ConstantNontunableParameter(name=key, value=val)
            )
        converted_additional_parameters: List[NontunableParameter[Any]] = []
        for key, val in self.additional_parameters.items():
            converted_additional_parameters.append(
                ConstantNontunableParameter(name=key, value=val)
            )

        return TabularConfiguration(
            metadata=self.metadata,
            additional_parameters=converted_additional_parameters,
            tuner_parameters=converted_tuner_parameters,
            training_datasets=converted_training_datasets,
            training_parameters=converted_training_parameters,
            model_parameters=converted_model_parameters,
            processing=converted_preprocessing,
        )
