import pytest
import math
from types import FunctionType
from configuration_engine.utils import resolve_function  # Replace with actual module name

class TestResolveFunction:

    def test_valid_function_from_allowed_module(self):
        func = resolve_function("math.sqrt", allowed_modules=["math"])
        assert callable(func)
        assert func(16) == 4.0

    def test_function_not_in_allowed_module(self):
        with pytest.raises(ImportError) as exc:
            resolve_function("math.sqrt", allowed_modules=["random"])
        assert "not in the allowed list" in str(exc.value)

    def test_function_does_not_exist(self):
        with pytest.raises(AttributeError) as exc:
            resolve_function("math.nonexistent", allowed_modules=["math"])
        assert "not found in module" in str(exc.value)

    def test_non_callable_attribute(self):
        with pytest.raises(TypeError) as exc:
            resolve_function("math.pi", allowed_modules=["math"])
        assert "is not callable" in str(exc.value)

    def test_builtin_function_disallowed(self):
        with pytest.raises(ValueError) as exc:
            resolve_function("len")
        assert "Built-in functions are not supported" in str(exc.value)

    def test_valid_function_without_whitelist(self):
        func = resolve_function("math.ceil")
        assert func(2.3) == 3