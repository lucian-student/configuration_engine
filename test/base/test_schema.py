from configuration_engine.schema import (
    BaseSchema,
    BasicSchema,
    TunableSchema,
    NonTunableSchema,
    Configuration,
    SmartSchema,
    ConfigurationEntry,
    ConfigurationDict,
    TunableDictSchema,
    NonTunableDictSchema,
)
from configuration_engine.parameter import (
    LiteralParameterSchema,
    LiteralParameter,
    RangeParameterSchema,
    RangeParameter,
    ConstantParameter,
    ConstantNontunableParameter,
    Tunable,
    Nontunable,
)
from typing import Literal, Annotated
from unittest.mock import MagicMock
import pytest


class DummyTunableSchema(TunableSchema):
    weather_type: (
        LiteralParameterSchema[Literal["bad", "good"]] | Literal["bad", "good"]
    )
    temperature: RangeParameterSchema[float] | float


class TestTunableSchema:

    def test_build(self):
        schema = DummyTunableSchema(
            **{"weather_type": {"values": ["good", "bad"]}, "temperature": 10.0}
        )
        parameter_dict = schema.build()
        reference_dict = {
            "weather_type": LiteralParameter(
                name="weather_type", values=["good", "bad"]
            ),
            "temperature": ConstantParameter(name="temperature", value=10.0),
        }
        assert parameter_dict == reference_dict


class DummyNonTunableSchema(NonTunableSchema):
    weather_type: str
    temperature: float


class TestNonTunableSchema:

    def test_build(self):
        schema = DummyNonTunableSchema(**{"weather_type": "good", "temperature": 10.0})
        parameter_dict = schema.build()
        reference_dict = {
            "weather_type": ConstantNontunableParameter(
                name="weather_type",
                value="good",
            ),
            "temperature": ConstantNontunableParameter(name="temperature", value=10.0),
        }
        assert parameter_dict == reference_dict


class DummyBasicSchema(BasicSchema):
    name: str
    surename: str


@pytest.fixture
def basic_configuration():
    return Configuration(
        data={
            "info": DummyBasicSchema(**{"name": "peter", "surename": "karel"}),
            "tunable": {
                "age": RangeParameter(name="age", min=0, max=24, log=False, step=1),
            },
            "nontunable": {
                "skin": ConstantNontunableParameter(name="skin", value="bad")
            },
        }
    )


@pytest.fixture
def trial_mock():
    mock = MagicMock()
    mock.suggest_int.return_value = 5
    return mock


class TestConfiguration:

    def test_construct_missing_key(self, basic_configuration: Configuration):
        with pytest.raises(ValueError):
            basic_configuration.construct("hello")

    def test_construct_basic_schema(self, basic_configuration: Configuration):
        data = basic_configuration.construct("info")
        expected = {"name": "peter", "surename": "karel"}
        assert data == expected

    def test_construct_tunable_dict(self, basic_configuration: Configuration):
        data = basic_configuration.construct("tunable")
        expected = {"age": 0}
        assert data == expected

    def test_construct_nontunable_dict(self, basic_configuration: Configuration):
        data = basic_configuration.construct("nontunable")
        expected = {"skin": "bad"}
        assert data == expected

    def test_suggest_tunable_dict(
        self, basic_configuration: Configuration, trial_mock: MagicMock
    ):
        data = basic_configuration.suggest("tunable", trial_mock)
        excepted = {"age": 5}
        assert data == excepted

    def test_suggest_nontunable_dict(
        self, basic_configuration: Configuration, trial_mock: MagicMock
    ):
        with pytest.raises(ValueError):
            basic_configuration.suggest("nontunable", trial_mock)

    def test_suggest_basic_schema(
        self, basic_configuration: Configuration, trial_mock: MagicMock
    ):
        with pytest.raises(ValueError):
            basic_configuration.suggest("info", trial_mock)

    def test_suggest_missing_key(
        self, basic_configuration: Configuration, trial_mock: MagicMock
    ):
        with pytest.raises(ValueError):
            basic_configuration.suggest("missing", trial_mock)


class DummySmartSchema(SmartSchema):
    tunable_dict: Annotated[TunableDictSchema, Tunable()]
    nontunable_dict: Annotated[NonTunableDictSchema, Nontunable()]
    basic: DummyBasicSchema
    tunable: DummyTunableSchema
    nontunable: DummyNonTunableSchema


@pytest.fixture
def smart_schema_data():
    return {
        "tunable_dict": {
            "age": {
                "min": 0,
                "max": 24,
            }
        },
        "nontunable_dict": {"age": 24},
        "basic": {"name": "peter", "surename": "karel"},
        "tunable": {"weather_type": {"values": ["good", "bad"]}, "temperature": 10.0},
        "nontunable": {"weather_type": "good", "temperature": 10.0},
    }


class TestSmartSchema:

    def test_build_configuration(self, smart_schema_data: dict):
        schema = DummySmartSchema(**smart_schema_data)
        config = schema.build_configuration()
        return config == Configuration(
            {
                "tunable_dict": {
                    "age": RangeParameter(
                        name="age", min=0, max=24, log=False, step=None
                    )
                },
                "nontunable_dict": {
                    "age": ConstantNontunableParameter(name="age", value=24)
                },
                "basic": BasicSchema(**{"name": "peter", "surename": "karel"}),
                "tunable": DummyTunableSchema(
                    **{
                        "weather_type": {"values": ["good", "bad"]},
                        "temperature": 10.0,
                    }
                ),
                "nontunable": DummyNonTunableSchema(
                    **{"weather_type": "good", "temperature": 10.0}
                ),
            }
        )
