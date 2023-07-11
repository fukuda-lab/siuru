from abc import ABC, abstractmethod

from common.features import SampleGenerator, EncodedSampleGenerator


class IDataEncoder(ABC):
    """
    Generic interface for data encoder classes to implement.
    """

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def encode(self, samples: SampleGenerator, **kwargs) -> EncodedSampleGenerator:
        """
        For each feature, yields both the original feature and its encoded version.
        """
        pass
