from abc import ABC, abstractmethod
from typing import Generator, Dict, Union, Any

from prediction_output import PredictionField
from preprocessors.common import PacketFeature, HostFeature, FlowFeature


class IDataEncoder(ABC):
    """
    Generic interface for data encoder modules to implement.
    """

    @abstractmethod
    def encode(
        self,
        data: Generator[
            Dict[Union[PacketFeature, HostFeature, FlowFeature, PredictionField], Any],
            None,
            None,
        ],
    ) -> Generator[Any, None, None]:
        yield None
