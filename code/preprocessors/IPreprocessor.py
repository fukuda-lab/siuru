from abc import ABC, abstractmethod
from typing import List

from common.features import IFeature, FeatureGenerator


class IPreprocessor(ABC):
    """
    Generic interface for data preprocessor classes to implement.
    """

    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        """
        Returns a list of features that the preprocessor requires
        in each input sample for internal processing.
        """
        pass

    @staticmethod
    @abstractmethod
    def output_signature() -> List[IFeature]:
        """
        Returns a list of features that the preprocessor promises
        to deliver (in addition to the existing features) in each
         sample when the generator is called.
        """
        pass

    @abstractmethod
    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        """
        Applies preprocessing steps to samples in the input
        feature generator, then yields the processed samples.
        The number of yielded samples need not correspond
        to the input sample count.
        """
        pass
