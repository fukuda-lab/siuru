from abc import ABC, abstractmethod
from typing import List

from common.features import IFeature, FeatureGenerator


class IDataLoader(ABC):
    """
    Generic interface for data loading classes to implement.
    """

    def __init__(self, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def feature_signature() -> List[IFeature]:
        """
        Returns a list of features that the data loader promises
        to deliver in each sample when the generator is called.
        """
        pass

    @abstractmethod
    def get_features(self) -> FeatureGenerator:
        """
        Yields a dictionary of preprocessed features per sample.
        """
        pass
