import subprocess
import time
import xarray
from typing import List, Generator, Dict, Any

from common.functions import report_performance
from dataloaders.IDataLoader import IDataLoader
from common.features import IFeature, PacketFeature

from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class XarrayPcapFileLoader(IDataLoader):
    def __init__(self, filepath: str, preprocessor_path: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self.preprocessor_path = preprocessor_path
        log.info(f"[{ type(self).__name__ }] Reading from file: {self.filepath}")

    def get_features(
        self,
    ) -> Generator[Dict[IFeature, Any], None, None]:
        pcap_call = [self.preprocessor_path, "stream-file", self.filepath]

        log.info(f"[PcapFileLoader] Processing file: {self.filepath}")
        sum_processing_time = 0
        packet_count = 0
        process = subprocess.Popen(
            pcap_call, stdout=subprocess.PIPE, universal_newlines=True
        )

        while True:
            start_time_ref = time.process_time_ns()
            line = process.stdout.readline()
            if line:
                packet_features = xarray.DataArray(
                    [line], dims=[PacketFeature.CPP_FEATURE_STRING]
                )
                sum_processing_time += time.process_time_ns() - start_time_ref
                yield packet_features
                packet_count += 1
            else:
                break

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)

    @staticmethod
    def feature_signature() -> List[IFeature]:
        return [PacketFeature.CPP_FEATURE_STRING]
