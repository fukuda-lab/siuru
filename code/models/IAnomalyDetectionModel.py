import os
from abc import ABC


class IAnomalyDetectionModel(ABC):
    def __init__(self, model_storage_base_path, **kwargs):
        assert kwargs["MODEL_NAME"]
        self.store_file = IAnomalyDetectionModel.model_path(
            model_storage_base_path,
            kwargs["MODEL_NAME"],
            model_path=kwargs["PATH"] if kwargs["PATH"] else None)

    @staticmethod
    def model_path(model_storage_base_path,
                   model_name,
                   model_path=None):
        # TODO specify model path rules in the README.
        if model_path:
            return os.path.join(
                model_storage_base_path,
                model_path)
        else:
            return os.path.join(
                model_storage_base_path,
                model_name,
                f"{model_name}.pickle")
