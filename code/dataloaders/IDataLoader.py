import os
from abc import ABC, abstractmethod
from typing import List, Union, Generator, Dict, Any

from prediction_output import PredictionField
from common.features import IFeature, FeatureGenerator


class IDataLoader(ABC):
    """
    Generic interface for data loading modules to implement.
    """

    def __init__(self, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def feature_signature() -> List[IFeature]:
        return []

    @abstractmethod
    def get_features(self) -> FeatureGenerator:
        """
        Yields a dictionary of preprocessed features per sample.
        """
        yield {}

    @staticmethod
    def _get_path_relative_to_data_dir(filepath: str) -> Union[str, None]:
        path_elements = filepath.split(os.path.sep)
        try:
            data_dir_idx = len(path_elements) - path_elements[::-1].index("data") - 1
        except ValueError:
            return None
        return os.path.join(*path_elements[data_dir_idx + 1 :])
