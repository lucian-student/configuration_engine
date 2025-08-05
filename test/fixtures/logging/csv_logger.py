import pytest


@pytest.fixture
def basic_data():
    return [
        {
            "iter": 1,
            "trial_number": 1,
            "train_loss": 1.4,
            "gradient_norm": 0.9,
            "batch_perplexity": 1.2,
        },
        {
            "iter": 2,
            "trial_number": 1,
            "train_loss": 1.5,
            "gradient_norm": 0.9,
            "batch_perplexity": 1.7,
        },
    ]