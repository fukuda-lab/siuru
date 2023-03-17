import subprocess
from typing import List, Union, Generator, Dict, Any, Tuple

from dataloaders.IDataLoader import IDataLoader
from prediction_output import PredictionField
from preprocessors.PacketProcessor import PacketProcessor
from preprocessors.common import (
    PacketFeature,
    HostFeature,
    FlowFeature,
    PacketData,
)

from pipeline_logger import PipelineLogger


class MQTTsetLoader(IDataLoader):
    SUPPORTED_FILES = [
        "MQTTset/Data/PCAP/capture_flood.pcap",
        "MQTTset/Data/PCAP/capture_1w.pcap",
        "MQTTset/Data/PCAP/capture_custom_1h.pcap",
        "MQTTset/Data/PCAP/slowite.pcap",
        "MQTTset/Data/PCAP/capture_malariaDoS.pcap",
        "kaiyodai-ship/tcpdump/mqtt-perftool.cap",
        "kaiyodai-ship/tcpdump/mqtt-sensor.cap",
    ]

    LABELS = {
        "MQTTset/Data/PCAP/capture_flood.pcap": [1 for _ in range(613)],
        "MQTTset/Data/PCAP/capture_1w.pcap": [0 for _ in range(11916329)],
        "MQTTset/Data/PCAP/capture_custom_1h.pcap": [0 for _ in range(70983)],
        "MQTTset/Data/PCAP/slowite.pcap": [1 for _ in range(9202)],
        "MQTTset/Data/PCAP/capture_malariaDoS.pcap": [1 for _ in range(130223)],
        "kaiyodai-ship/tcpdump/mqtt-perftool.cap": [0 for _ in range(1)],
        "kaiyodai-ship/tcpdump/mqtt-sensor.cap": [0 for _ in range(1)],
    }

    def __init__(self, filepath, preprocessor_path):
        self.filepath = filepath
        self.preprocessor_path = preprocessor_path

    @staticmethod
    def can_load(filepath: str) -> bool:
        return (
            IDataLoader._get_path_relative_to_data_dir(filepath)
            in MQTTsetLoader.SUPPORTED_FILES
        )

    def get_features(self) -> Generator[
        Dict[Union[PacketFeature, HostFeature, FlowFeature, PredictionField], Any],
        None,
        None,
    ]:

        log = PipelineLogger.get_logger()

        log.info(f"[MQTTsetLoader] Processing file: {self.filepath}")

        pcap_call = [self.preprocessor_path, "stream-file", self.filepath]
        process = subprocess.Popen(
            pcap_call, stdout=subprocess.PIPE, universal_newlines=True
        )

        preprocessor = PacketProcessor()
        for packet_features in process.stdout.readlines():
            yield preprocessor.process(PacketData(packet_features))

    def get_metadata(
        self, **kwargs
    ) -> Generator[
        Dict[Union[PacketFeature, HostFeature, FlowFeature, PredictionField], Any],
        None,
        None,
    ]:

        log = PipelineLogger.get_logger()

        assert kwargs["preprocessor_path"], kwargs["filepath"]
        preprocessor_path = kwargs["preprocessor_path"]
        filepath = kwargs["filepath"]

        log.info(f"[MQTTsetLoader] Processing file: {filepath} for metadata.")

        pcap_call = [preprocessor_path, "stream-file", filepath]
        process = subprocess.Popen(
            pcap_call, stdout=subprocess.PIPE, universal_newlines=True
        )

        overall_packet_counter = 0

        for packet_features in process.stdout.readlines():
            p = PacketData(packet_features)
            if not p.is_valid:
                continue
            overall_packet_counter += 1
            yield {
                PacketFeature.TIMESTAMP: p.timestamp,
                PacketFeature.IP_SOURCE_ADDRESS: p.source_ip,
                PacketFeature.IP_DESTINATION_ADDRESS: p.destination_ip,
                PacketFeature.IP_SOURCE_PORT: p.source_port,
                PacketFeature.IP_DESTINATION_PORT: p.destination_port,
                PacketFeature.PROTOCOL: p.protocol,
            }

        log.info(
            f"[MQTTsetLoader] Extracted and processed {overall_packet_counter} packets."
        )

    @staticmethod
    def feature_signature() -> List[
        Union[PacketFeature, HostFeature, FlowFeature, PredictionField]
    ]:
        return PacketProcessor.signature()

    def get_labels(self, **kwargs) -> Generator[Any, None, None]:
        assert kwargs["filepath"]
        yield from MQTTsetLoader.LABELS[
            IDataLoader._get_path_relative_to_data_dir(kwargs["filepath"])
        ]
