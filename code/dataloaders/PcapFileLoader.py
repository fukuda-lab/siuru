import subprocess
from typing import List, Generator, Dict, Any

from dataloaders.IDataLoader import IDataLoader
from common.features import IFeature, PacketFeature

from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class PcapFileLoader(IDataLoader):
    def __init__(self, filepath, preprocessor_path, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self.preprocessor_path = preprocessor_path
        log.info(f"[PcapFileLoader] Reading from file: {self.filepath}")

    def get_features(
        self,
    ) -> Generator[Dict[IFeature, Any], None, None]:

        log.info(f"[PcapFileLoader] Processing file: {self.filepath}")

        pcap_call = [self.preprocessor_path, "stream-file", self.filepath]
        process = subprocess.Popen(
            pcap_call, stdout=subprocess.PIPE, universal_newlines=True
        )

        for packet_features in process.stdout.readlines():
            yield {
                PacketFeature.CPP_FEATURE_STRING: packet_features
            }

    @staticmethod
    def feature_signature() -> List[IFeature]:
        return [PacketFeature.CPP_FEATURE_STRING]
