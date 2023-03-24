from typing import List, Union, Generator, Any, Dict

from dataloaders.IDataLoader import IDataLoader
from common.features import IFeature


class PacketSniffer(IDataLoader):
    @staticmethod
    def feature_signature() -> List[IFeature]:
        pass

    def get_features(
        self,
    ) -> Generator[Dict[IFeature, Any], None, None,]:
        pass
