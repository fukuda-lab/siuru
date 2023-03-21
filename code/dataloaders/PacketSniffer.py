from typing import List, Union, Generator, Any, Dict

from dataloaders.IDataLoader import IDataLoader
from prediction_output import PredictionField
from common.features import IFeature


class PacketSniffer(IDataLoader):

    def get_features(self, **kwargs) -> Generator[
        Dict[IFeature, Any],
        None,
        None,
    ]:
        pass

    def get_metadata(self, **kwargs) -> Generator[
        Dict[IFeature, Any],
        None,
        None,
    ]:
        pass

    def get_labels(self, **kwargs) -> Generator[Any, None, None]:
        pass

    @staticmethod
    def feature_signature() -> List[
        IFeature
    ]:
        pass

    @staticmethod
    def can_load(filepath: str) -> bool:
        pass