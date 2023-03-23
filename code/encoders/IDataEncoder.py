from abc import ABC, abstractmethod
from typing import Generator, Dict, Union, Any

from prediction_output import PredictionField
from common.features import IFeature, FeatureGenerator


class IDataEncoder(ABC):
    """
    Generic interface for data encoder modules to implement.
    """
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def encode(self, features: FeatureGenerator, **kwargs) -> Any:
        yield None
