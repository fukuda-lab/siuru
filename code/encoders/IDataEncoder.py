from abc import ABC, abstractmethod

from common.features import FeatureGenerator, EncodedFeatureGenerator


class IDataEncoder(ABC):
    """
    Generic interface for data encoder classes to implement.
    """

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def encode(self, features: FeatureGenerator, **kwargs) -> EncodedFeatureGenerator:
        """
        For each feature, yields both the original feature and its encoded version.
        """
        pass
