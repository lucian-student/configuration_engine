from configuration_engine.parameter import LiteralParameterSchema, LiteralParameter


class TestLiteralParameterSchema:
    def test_build_creates_literal_parameter(self):
        schema = LiteralParameterSchema(values=["red", "green", "blue"])
        param = schema.build(name="color")

        assert isinstance(param, LiteralParameter)
        assert param.values == ["red", "green", "blue"]
        assert param.name == "color"
        assert param.alias == "color"

    def test_build_with_alias(self):
        schema = LiteralParameterSchema(values=["small", "medium", "large"])
        param = schema.build(name="size", alias="custom_size")

        assert param.name == "size"
        assert param.alias == "custom_size"
        assert param.values == ["small", "medium", "large"]
