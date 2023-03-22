import os
from abc import ABC, abstractmethod
from typing import Optional

from dataloaders import IDataLoader


class IAnomalyDetectionModel(ABC):
    def __init__(
        self,
        model_name: str,
        use_existing_model: bool = False,
        skip_saving_model: bool = False,
        model_storage_base_path: Optional[str] = None,
        model_relative_path: Optional[str] = None,
        **kwargs,
    ):

        self.model_name = model_name
        self.use_existing_model = use_existing_model
        self.skip_saving_model = skip_saving_model

        if not self.skip_saving_model:
            assert model_storage_base_path
            self.model_relative_path = model_relative_path
            if not self.model_relative_path:
                self.model_relative_path = os.path.join(
                    model_name, f"{model_name}.pickle"
                )
            self.store_file = os.path.join(model_storage_base_path, model_relative_path)

        if self.use_existing_model and not os.path.exists(self.store_file):
            # The specified model is not available.
            raise RuntimeError(f"No file found under the path: {self.store_file}")
        elif os.path.exists(self.store_file):
            raise RuntimeError(f"Model file already exists: {self.store_file}")
        elif not os.path.exists(os.path.join(self.store_file, "..")):
            os.mkdir(os.path.join(self.store_file, ".."))

    @abstractmethod
    def train_with_source(self, data_source: IDataLoader, **kwargs):
        pass

    @abstractmethod
    def predict_from_source(self, data_source: IDataLoader, **kwargs):
        pass
