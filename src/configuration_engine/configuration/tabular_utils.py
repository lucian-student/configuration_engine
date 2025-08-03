from configuration_engine.configuration.training_schema import TrainingSchema
from configuration_engine.configuration.tabular_schema import TabularSchema
import pandas as pd
import yaml


def get_best_tabular_config(config: TrainingSchema, categories):
    with open(config.config_path) as configurationsStream:
        configurations = yaml.safe_load_all(configurationsStream)
        configs = list(configurations)
    metrics = pd.read_csv(config.metric_path)
    first_config = configs[0]

    if first_config["additional_parameters"]["direction"] == "maximize":
        index = metrics["best_score"].idxmax()
        best_config = configs[index]
    else:
        index = metrics["best_score"].idxmin()
        best_config = configs[index]

    validatedConfig = TabularSchema(**best_config)
    tabularConfig = validatedConfig.build(categories=categories)
    return tabularConfig
