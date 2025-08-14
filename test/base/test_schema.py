from configuration_engine.schema import (
    BaseSchema,
    BasicSchema,
    TunableSchema,
    NonTunableSchema,
    Configuration,
    SmartSchema,
    ConfigurationEntry,
    ConfigurationDict,
)
from configuration_engine.parameter import (
    LiteralParameterSchema,
    LiteralParameter,
    RangeParameterSchema,
    RangeParameter,
    ConstantParameter,
    ConstantNontunableParameter,
)
from typing import Literal


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


class TestConfiguration:
    pass


class TestSmartSchema:
    pass
