from abc import ABC, abstractmethod
from typing import List

from common.features import IFeature, SampleGenerator


class IPreprocessor(ABC):
    """
    Generic interface for data preprocessor classes to implement.
    """

    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        """
        Returns a list of features that the preprocessor requires in each input sample
        for internal processing.
        """
        pass

    @staticmethod
    @abstractmethod
    def output_signature() -> List[IFeature]:
        """
        Returns a list of features that the preprocessor promises to deliver
        (in addition to the existing features) in each sample when the generator
        is called.
        """
        pass

    @abstractmethod
    def process(self, samples: SampleGenerator) -> SampleGenerator:
        """
        Applies preprocessing steps to samples in the input generator, then yields the
        modified samples. The number of yielded samples can be different from the input
        sample count!
        """
        pass
