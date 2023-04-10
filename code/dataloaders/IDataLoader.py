import os
from abc import ABC, abstractmethod
from typing import List, Union, Generator, Dict, Any

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
