from abc import ABC, abstractmethod
from typing import Dict, Any, List

from common.features import IFeature


class IReporter(ABC):
    """
    Generic interface for reporter classes to implement.
    """

    @abstractmethod
    def report(self, features: Dict[IFeature, Any]):
        """
        Performs the reporting task based on the sample's feature dictionary,
        which should contain prediction information from an anomaly detection
        component.
        """
        pass

    @abstractmethod
    def end_processing(self):
        """
        Callback triggered by the main pipeline at the end of
        processing for eventual teardown tasks.
        """
        pass

    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        """
        Returns a list of features that the reporter requires
        in each input sample for internal processing.
        """
        pass
