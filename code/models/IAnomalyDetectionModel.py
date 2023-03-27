import os
from abc import ABC, abstractmethod
from typing import Optional, Any, Generator, Tuple, Dict

from common.features import IFeature
from dataloaders import IDataLoader


class IAnomalyDetectionModel(ABC):
    def __init__(
        self,
        model_name: str,
        train_new_model: bool = True,
        skip_saving_model: bool = False,
        model_storage_base_path: Optional[str] = None,
        model_relative_path: Optional[str] = None,
        **kwargs,
    ):

        self.model_name = model_name
        self.train_new_model = train_new_model
        self.skip_saving_model = skip_saving_model

        assert model_storage_base_path
        if not model_relative_path:
            model_relative_path = os.path.join(model_name, f"{model_name}.pickle")
        self.store_file = os.path.join(model_storage_base_path, model_relative_path)

        if self.train_new_model and os.path.exists(self.store_file):
            raise RuntimeError(f"Model file already exists: {self.store_file}")
        elif not os.path.exists(os.path.dirname(self.store_file)):
            os.mkdir(os.path.dirname(self.store_file))

        if not self.train_new_model and not os.path.exists(self.store_file):
            # The specified model is not available.
            raise RuntimeError(f"No file found under the path: {self.store_file}")
        elif not self.train_new_model:
            self.load()

    def save_configuration(self, config: str):
        config_file_path = os.path.join(os.path.dirname(self.store_file), "config.json")
        assert not os.path.exists(config_file_path)
        with open(config_file_path, "w") as f:
            f.write(config)

    @abstractmethod
    def train(
        self, data: Generator[Tuple[Dict[IFeature, Any], Any], None, None], **kwargs
    ):
        pass

    @abstractmethod
    def load(self, **kwargs):
        pass

    @abstractmethod
    def predict(self, features: Dict[IFeature, Any], encoded_data: Any, **kwargs):
        """
        Add a prediction entry based on encoded_data directly into
        the feature dictionary.
        """
        pass
