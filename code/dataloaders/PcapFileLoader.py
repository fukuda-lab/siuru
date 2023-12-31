import subprocess
import time
from typing import List, Generator, Dict, Any

import common.global_variables as global_variables
from common.functions import report_performance
from dataloaders.IDataLoader import IDataLoader
from common.features import IFeature, PacketFeature

from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class PcapFileLoader(IDataLoader):
    def __init__(self, filepath: str, packet_processor_path: str, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self.preprocessor_path = packet_processor_path
        log.info(f"[{ type(self).__name__ }] Reading from file: {self.filepath}")

    def get_samples(
        self,
    ) -> Generator[Dict[IFeature, Any], None, None]:
        pcap_call = [self.preprocessor_path, "stream-file", self.filepath]

        log.info(f"[PcapFileLoader] Processing file: {self.filepath}")
        sum_processing_time = 0
        packet_count = 0
        process = subprocess.Popen(
            pcap_call, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
        )

        while True:
            start_time_ref = time.process_time_ns()
            if process.poll() and process.returncode:
                log.error(process.stdout.readlines())
                raise RuntimeError(f"PCAP feature extractor exited with error code {process.returncode}!")
            packet_features = {
                PacketFeature.CPP_FEATURE_STRING: process.stdout.readline()
            }
            sum_processing_time += time.process_time_ns() - start_time_ref
            if packet_features[PacketFeature.CPP_FEATURE_STRING]:
                yield packet_features
                packet_count += 1
            else:
                break

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)

        # Data loaders only exists once per data source, therefore they are
        # suitable for tracking the overall number of packets processed. This
        # value will be reported by the main pipeline in the end.
        global_variables.global_pipeline_packet_count += packet_count

    @staticmethod
    def feature_signature() -> List[IFeature]:
        return [PacketFeature.CPP_FEATURE_STRING]
