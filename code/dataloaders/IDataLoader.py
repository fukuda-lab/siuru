import os
import subprocess
from abc import ABC, abstractmethod
from typing import List, Union, Generator, Dict, Any, Tuple

from preprocess_features import PacketFeature, HostFeature, FlowFeature


class IDataLoader(ABC):
    """
    Generic interface for DataLoader classes to implement.
    """
    @staticmethod
    @abstractmethod
    def can_load(filepath: str) -> bool:
        return False

    @staticmethod
    @abstractmethod
    def feature_signature() -> List[Union[PacketFeature, HostFeature, FlowFeature]]:
        return []

    @abstractmethod
    def get_features(self, **kwargs) -> Generator[Dict[Union[PacketFeature, HostFeature, FlowFeature], Any], None, None]:
        """
        Yields a dictionary of preprocessed features per sample.
        """
        yield {}

    @abstractmethod
    def get_metadata(self, **kwargs) -> Generator[Dict[Union[PacketFeature, HostFeature, FlowFeature], Any], None, None]:
        """
        Yields a dictionary of metadata per sample.
        """
        yield {}

    @abstractmethod
    def get_labels(self, **kwargs) -> Generator[Any, None, None]:
        yield []

    @staticmethod
    def _get_path_relative_to_data_dir(filepath: str) -> Union[str, None]:
        path_elements = filepath.split(os.path.sep)
        try:
            data_dir_idx = len(path_elements) - path_elements[::-1].index("data") - 1
        except ValueError:
            return None
        return os.path.join(*path_elements[data_dir_idx + 1:])
