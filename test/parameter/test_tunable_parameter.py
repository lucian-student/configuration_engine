import pytest
from unittest.mock import MagicMock
from configuration_engine.parameter import LiteralParameter  # Replace with actual import

class TestLiteralParameter:
    
    def setup_method(self):
        self.trial = MagicMock()

    def test_suggest_returns_correct_value(self):
        param = LiteralParameter(name="color", values=["red", "green", "blue"])
        self.trial.suggest_int.return_value = 1

        result = param.suggest(self.trial)
        assert result == "green"
        self.trial.suggest_int.assert_called_once_with(name=param.alias, low=0, high=2)

    def test_alias_usage(self):
        param = LiteralParameter(name="size", values=[10, 20, 30], alias="custom_alias")
        self.trial.suggest_int.return_value = 2

        result = param.suggest(self.trial)
        assert result == 30
        self.trial.suggest_int.assert_called_once_with(name="custom_alias", low=0, high=2)

    def test_out_of_bounds_index_raises(self):
        param = LiteralParameter(name="level", values=["low", "medium", "high"])
        self.trial.suggest_int.return_value = 5  # Invalid index

        with pytest.raises(IndexError):
            _ = param.suggest(self.trial)
