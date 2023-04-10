from abc import ABC, abstractmethod
from typing import Generator, Dict, Any, Tuple

from common.features import IFeature, FeatureGenerator, LabeledFeatureGenerator


class IDataEncoder(ABC):
    """
    Generic interface for data encoder modules to implement.
    """

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> LabeledFeatureGenerator:
        """
        For each feature, return both the original feature and its encoded version.
        """
        yield None
