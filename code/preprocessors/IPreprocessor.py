from abc import ABC, abstractmethod
from typing import List, Dict, Any

from common.features import IFeature


class IPreprocessor(ABC):
    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        pass

    @staticmethod
    @abstractmethod
    def output_signature() -> List[IFeature]:
        pass

    @abstractmethod
    def process(self, features: Dict[IFeature, Any]) -> Dict[IFeature, Any]:
        pass
