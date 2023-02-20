import subprocess
from collections import defaultdict
from typing import List, Union, Generator, Dict, Any, Tuple

import pandas as pd

from dataloaders.IDataLoader import IDataLoader
from preprocess_features import PacketFeature, HostFeature, FlowFeature, PacketData

from pipeline_logger import PipelineLogger


class MawiLoaderDummy(IDataLoader):
    SUPPORTED_FILES = [
        "2006-08-24-14:00:00-WIDE/200608241400.dump"
    ]

    LABELS = {
        "2006-08-24-14:00:00-WIDE/200608241400.dump": [0 for _ in range(0)]  # TODO
    }

    @staticmethod
    def can_load(filepath: str) -> bool:
        return IDataLoader._get_path_relative_to_data_dir(filepath) in MawiLoaderDummy.SUPPORTED_FILES

    def preprocess(self, **kwargs) -> Generator[
            Dict[Union[PacketFeature, HostFeature, HostFeature], Any], None, None]:

        log = PipelineLogger.get_logger()

        assert kwargs["preprocessor_path"], kwargs["filepath"]
        preprocessor_path = kwargs["preprocessor_path"]
        filepath = kwargs["filepath"]

        log.info(f"[MawiLoader] Processing file: {filepath}")

        pcap_call = [preprocessor_path, "stream-file", filepath]
        process = subprocess.Popen(pcap_call, stdout=subprocess.PIPE, universal_newlines=True)

        packet_counter = 0

        for packet_features in process.stdout.readlines():
            packet_counter += 1
            yield {}

        log.info(f"[MQTTsetLoader] Extracted and processed {packet_counter} packets.")

    @staticmethod
    def feature_signature() -> List[Union[PacketFeature, HostFeature, FlowFeature]]:
        return []

    def get_labels(self, **kwargs) -> Generator[Any, None, None]:
        assert kwargs["filepath"]
        yield from MawiLoaderDummy.LABELS[IDataLoader._get_path_relative_to_data_dir(kwargs["filepath"])]
