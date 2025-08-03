from typing import List, Any, Dict, Optional, Tuple
from configuration_engine.datasets import PandasDataset
from configuration_engine.parameter import Parameter, NontunableParameter
from configuration_engine.processing_action import TabularProcessingAction
from configuration_engine.configuration.metadata import Metadata
import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from dataclasses import dataclass


@dataclass
class ProcessedPandasDataset:
    data: pd.DataFrame
    weight: List[float]
    folds: List[Tuple[np.ndarray, np.ndarray]]
    dataset_parameters: List[Dict[str, Any]]


class TabularConfiguration:

    def __init__(
        self,
        metadata: Metadata,
        additional_parameters: List[NontunableParameter[Any]],
        tuner_parameters: List[NontunableParameter[Any]],
        training_datasets: List[PandasDataset],
        training_parameters: List[Parameter[Any]],
        model_parameters: List[Parameter[Any]],
        processing: List[TabularProcessingAction],
    ):
        self.additional_parameters = additional_parameters
        self.tuner_parameters = tuner_parameters
        self.metadata = metadata
        self.training_datasets = training_datasets
        self.training_parameters = training_parameters
        self.model_parameters = model_parameters
        self.processing = processing

    def construct_dataset(
        self, target_column: str, trial: optuna.Trial = None, k_folds: Optional[int] = 5
    ) -> ProcessedPandasDataset:
        """
        First it constructs dataset, than processing is applied
        """
        dataset_parameters: List[Dict[str, Any]] = []
        training_datasets: List[pd.DataFrame] = []
        aditional_datasets: List[pd.DataFrame] = []
        training_weight: List[float] = []
        additional_weight: List[float] = []
        for dataset in self.training_datasets:
            if dataset.cv:
                training_datasets.append(dataset.data)
                if trial is not None:
                    curr_weight = dataset.weight.suggest(trial)
                else:
                    curr_weight = dataset.weight.first()
                for i in range(dataset.data.shape[0]):
                    training_weight.append(curr_weight)
            else:
                aditional_datasets.append(dataset.data)
                if trial is not None:
                    curr_weight = dataset.weight.suggest(trial)
                else:
                    curr_weight = dataset.weight.first()
                for i in range(dataset.data.shape[0]):
                    additional_weight.append(curr_weight)
            dataset_parameters.append(
                {
                    "path": dataset.path,
                    "weight": curr_weight,
                    "cv": dataset.cv,
                    "name": dataset.name,
                }
            )

        training_dataset = pd.concat(training_datasets, axis=0)
        if aditional_datasets:
            additional_dataset = pd.concat(aditional_datasets, axis=0)
            total_dataset = pd.concat([training_dataset, additional_dataset], axis=0)
        else:
            total_dataset = training_dataset.copy()

        for processor in self.processing:
            processor.fit_transform(total_dataset, True)
            processor.transform(training_dataset, True)
            if aditional_datasets:
                processor.transform(additional_dataset, True)

        kf = StratifiedKFold(
            n_splits=k_folds, shuffle=True, random_state=self.metadata.seed
        )
        folds = [
            (train_idx, val_idx)
            for train_idx, val_idx in kf.split(
                X=training_dataset, y=training_dataset[target_column]
            )
        ]
        if aditional_datasets:
            for i in range(len(folds)):
                folds[i] = (
                    np.concat(
                        [
                            folds[i][0],
                            np.arange(additional_dataset.shape[0])
                            + training_dataset.shape[0],
                        ],
                        axis=0,
                    ),
                    folds[i][1],
                )

        return ProcessedPandasDataset(
            data=total_dataset,
            weight=training_weight + additional_weight,
            folds=folds,
            dataset_parameters=dataset_parameters,
        )

    def suggest_model_params(
        self, trial: optuna.Trial
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Mělby vrátit dvojici, parametry pro program a parametry vhodné pro uložení do yamlu
        """
        params: Dict[str, Any] = {}
        for param in self.model_parameters:
            params[param.name] = param.suggest(trial)
        return params, params

    def suggest_training_params(
        self, trial: optuna.Trial
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        params: Dict[str, Any] = {}
        for param in self.training_parameters:
            params[param.name] = param.suggest(trial)
        return params, params

    def construct_additional_params(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        params: Dict[str, Any] = {}
        for param in self.additional_parameters:
            params[param.name()] = param.value()
        return params, params

    def construct_tuner_parameters(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        params: Dict[str, Any] = {}
        for param in self.tuner_parameters:
            params[param.name()] = param.value()
        return params, params

    def first_model_params(self) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        for param in self.model_parameters:
            params[param.name] = param.first()
        return params
