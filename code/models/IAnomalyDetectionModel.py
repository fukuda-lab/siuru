import os
from abc import ABC, abstractmethod
from typing import Optional

from common.features import EncodedSampleGenerator, SampleGenerator


class IAnomalyDetectionModel(ABC):
    """
    Generic interface for anomaly detection model classes to implement.
    """

    def __init__(
        self,
        model_name: str,
        train_new_model: bool = True,
        skip_saving_model: bool = False,
        model_storage_base_path: Optional[str] = None,
        model_relative_path: Optional[str] = None,
        full_config_json: Optional[str] = None,
        **kwargs,
    ):
        """
        Generic interface for anomaly detection models with storage and loading logic.

        :param model_name: Name of the model. Will be used as the name of the storage
            file (must exist in prediction mode) and for tagging the prediction.
        :param train_new_model: If true, data will be passed to the train() function
            and a new model is created. Otherwise, the model must exist under the
            provided path and data will be passed to the predict() function.
        :param skip_saving_model: Train a model, but do not store it. Can be used to
            test the training pipeline. train_new_model must be set to true for this
            parameter to take effect.
        :param model_storage_base_path: The base path in the project where models
            will be stored or searched for.
        :param model_relative_path: Path relative to model_storage_base path where the
            trained model is stored or loaded.
        :param full_config_json: Configuration file for the pipeline, used to provide
            parameters to models. The config will be stored along with any newly trained
            model if skip_saving_model is not set.
        :param kwargs: Optional arguments that can be used to pass additional parameters
            to the model implementation.
        """
        self.model_name = model_name
        self.train_new_model = train_new_model
        self.skip_saving_model = skip_saving_model

        assert model_storage_base_path
        if not model_relative_path:
            model_relative_path = os.path.join(model_name, f"{model_name}.pickle")
        self.store_file = os.path.abspath(
            os.path.join(model_storage_base_path, model_relative_path)
        )

        if self.train_new_model and not self.skip_saving_model:
            if os.path.exists(self.store_file):
                raise RuntimeError(f"Model file already exists: {self.store_file}")
            elif not os.path.exists(os.path.dirname(self.store_file)):
                # Create the directory to store the new model.
                os.makedirs(os.path.dirname(self.store_file))
            if full_config_json:
                self.save_configuration(full_config_json)

        if not self.train_new_model and not os.path.exists(self.store_file):
            # The specified model is not available.
            raise RuntimeError(f"No file found under the path: {self.store_file}")
        elif not self.train_new_model:
            self.load()

    def save_configuration(self, config: str):
        config_file_path = os.path.join(os.path.dirname(self.store_file), "config.json")
        assert not os.path.exists(config_file_path), (
            f"Configuration path already exists: {config_file_path}"
            + "\nForgot to remove build artifacts from past run?"
        )
        with open(config_file_path, "w") as f:
            f.write(config)

    @abstractmethod
    def train(self, data: EncodedSampleGenerator, **kwargs):
        """
        Trains the anomaly detection model on provided data.
        If skip_saving_model == false, the model will be stored after training.
        """
        pass

    @abstractmethod
    def load(self, **kwargs):
        """
        Load a previously stored model for prediction.
        """
        pass

    @abstractmethod
    def predict(self, data: EncodedSampleGenerator, **kwargs) -> SampleGenerator:
        """
        Adds a prediction entry based on encoded data directly into
        the feature dictionary of the provided sample, then return the sample.
        """
        pass
