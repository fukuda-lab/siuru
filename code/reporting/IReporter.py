from abc import ABC, abstractmethod
from typing import Dict, Any, List

from common.features import IFeature


class IReporter(ABC):
    @abstractmethod
    def report(self, features: Dict[IFeature, Any]):
        pass

    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        pass
