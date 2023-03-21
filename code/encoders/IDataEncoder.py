from abc import ABC, abstractmethod
from typing import Generator, Dict, Union, Any

from prediction_output import PredictionField
from common.features import IFeature


class IDataEncoder(ABC):
    """
    Generic interface for data encoder modules to implement.
    """

    @abstractmethod
    def encode(
        self,
        data: Generator[
            Dict[IFeature, Any],
            None,
            None,
        ],
    ) -> Generator[Any, None, None]:
        yield None
