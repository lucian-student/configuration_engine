from pydantic import BaseModel
from abc import ABC, abstractmethod
from configuration_engine.parameter.tunable_parameter import (
    Parameter,
    ConstantParameter,
)
from configuration_engine.parameter.parameter_schema import Tunable, BaseParameter
from configuration_engine.parameter.nontunable_parameter import (
    NontunableParameter,
    ConstantNontunableParameter,
)
from configuration_engine.parameter.nontunable_parameter_schema import (
    Nontunable,
    BaseNontunableParameter,
)
from typing import Any
import optuna
from configuration_engine import error_message
from configuration_engine.constants import *


class BaseSchema(BaseModel, ABC):

    @abstractmethod
    def build(self) -> Any:
        pass


class BasicSchema(BaseSchema):

    def build(self):
        return self


class TunableSchema(BaseSchema):

    def build(self):
        transformed_data: dict[str, Parameter[Any]] = {}
        for param_name in self.__pydantic_fields__:
            param_schema = getattr(self, param_name)
            if isinstance(param_schema, BaseParameter):
                transformed_data[param_name] = param_schema.build(name=param_name)
            else:
                transformed_data[param_name] = ConstantParameter(
                    name=param_name, value=param_schema
                )
        return transformed_data


class NonTunableSchema(BaseSchema):
    def build(self):
        transformed_data: list[str, NontunableParameter[Any]] = {}
        for param_name in self.__pydantic_fields__:
            param_schema = getattr(self, param_name)
            if isinstance(param_schema, BaseNontunableParameter):
                transformed_data[param_name] = param_schema.build(name=param_name)
            else:
                transformed_data[param_name] = ConstantNontunableParameter(
                    name=param_name, value=param_schema
                )
        return transformed_data


ConfigurationEntry = (
    BasicSchema | dict[str, Parameter[Any]] | dict[str, NontunableParameter[Any]]
)
ConfigurationDict = dict[str, ConfigurationEntry]


class Configuration:
    """
    Flexible Configuration, class that is automatically constructed by SmartSchema
    """

    def __init__(self, data: ConfigurationDict):
        self.data = data

    def __getitem__(self, key: str) -> Any:
        if key not in self.data:
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "__getitem__",
                f"Key {key} isn't present!",
            )
        return self.data[key]

    def construct(self, key: str) -> dict[str, Any]:
        """
        This value contructs parameter dict:
        * for BasicSchema it model_dumps()
        * For tunable parameters it gets value returned by method first
        * For nontunable parameter it calls value method
        Raises:
            ValueError
        """
        if key not in self.data:
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "suggest",
                f"Key {key} isn't present!",
            )
        values = self.data[key]
        if isinstance(values, BasicSchema):
            return values.model_dump()
        if not isinstance(values, dict):
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "suggest",
                f"Key {key} type isn't supported key should be parameter dict or basic schema!",
            )
        constructed_values: dict[str, Any] = {}
        for parameter_name, parameter in values.items():
            if isinstance(parameter, NontunableParameter):
                constructed_values[parameter_name] = parameter.value()
            elif isinstance(parameter, Parameter):
                constructed_values[parameter_name] = parameter.first()
            else:
                raise ValueError(
                    f"{MODULE_NAME}:{self.__class__}",
                    "suggest",
                    f"Dict should only contain {Parameter} or {NontunableParameter}!",
                )
        return constructed_values

    def suggest(self, key: str, trial: optuna.Trial) -> dict[Any]:
        """
        This method suggest parameters, if the value is dict of tunable parameters.
        Raises:
            ValueError
        """
        if key not in self.data:
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "suggest",
                f"Key {key} isn't present!",
            )
        values = self.data[key]
        if not isinstance(values, dict):
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "suggest",
                f"Key {key} value should be a dict!",
            )
        if not values:
            return {}
        first_value = next(iter(values.values()))
        if not isinstance(first_value, Parameter):
            raise ValueError(
                f"{MODULE_NAME}:{self.__class__}",
                "suggest",
                f"Key {key} should be an instance of the {Parameter} class!",
            )
        # typecasting, since when one value is Parameter i assume, all values are parameter, that is done for better performance
        values: dict[str, Parameter[Any]]
        suggested_values: dict[str, Any] = {}
        for parameter_name, parameter in values.items():
            suggested_values[parameter_name] = parameter.suggest(trial)
        return suggested_values


class SmartSchema(BaseModel, ABC):
    """
    This class alows to automatically convert schema dicts to parameters.
    Or parameters, that are of type TunableSchema or NontunableSchema
    """

    def build_configuration(self) -> Configuration:
        """
        This method uses Field metadata, to build dict of parameters
        Raise:
        """
        cls = self.__class__
        data = self.model_dump()
        transformed_data: ConfigurationDict = {}
        for name, field in cls.__pydantic_fields__.items():
            metadata = field.metadata
            current_value = data[name]
            contains_tunable = any(isinstance(item, Tunable) for item in metadata)
            contains_nontunable = any(isinstance(item, Nontunable) for item in metadata)
            if isinstance(current_value, dict):
                transformed_value = {}
                if contains_tunable:
                    for param_name, param_schema in current_value.items():
                        if isinstance(param_schema, BaseParameter):
                            transformed_value[param_name] = param_schema.build(
                                name=param_name
                            )
                        else:
                            transformed_value[param_name] = ConstantParameter(
                                name=param_name, value=param_schema
                            )
                    transformed_data[name] = transformed_value
                elif contains_nontunable:
                    for param_name, param_schema in current_value.items():
                        if isinstance(param_schema, BaseNontunableParameter):
                            transformed_value[param_name] = param_schema.build(
                                name=param_name
                            )
                        else:
                            transformed_value[param_name] = ConstantNontunableParameter(
                                name=param_name, value=param_schema
                            )
                    transformed_data[name] = transformed_value
                else:
                    transformed_data[name] = current_value
            elif isinstance(current_value, BaseSchema):
                transformed_data[name] = current_value.build()
            else:
                transformed_data[name] = current_value
        return Configuration(transformed_data)
