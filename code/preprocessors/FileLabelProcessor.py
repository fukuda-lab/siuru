from typing import Dict, List, Optional, Any

from common.features import IFeature, PredictionField, PacketFeature
from pipeline_logger import PipelineLogger
from preprocessors.IPreprocessor import IPreprocessor


log = PipelineLogger.get_logger()


class FileLabelProcessor(IPreprocessor):
    # 1 stands for anomalous and 0 for non-anomalous data.
    DEFAULT_LABELS = {
        "MQTTset/Data/PCAP/capture_flood.pcap": 1,
        "MQTTset/Data/PCAP/capture_1w.pcap": 0,
        "MQTTset/Data/PCAP/capture_custom_1h.pcap": 0,
        "MQTTset/Data/PCAP/slowite.pcap": 1,
        "MQTTset/Data/PCAP/capture_malariaDoS.pcap": 1,
        "kaiyodai-ship/tcpdump/mqtt-perftool.cap": 0,
        "kaiyodai-ship/tcpdump/mqtt-sensor.cap": 0,
    }

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [PacketFeature.SOURCE_FILE_NAME]

    @staticmethod
    def output_signature() -> List[IFeature]:
        return [PredictionField.GROUND_TRUTH]

    def __init__(
        self,
        source_file: Optional[str] = None,
        label_file: Optional[str] = None,
        label_value: Optional[Any] = None,
    ):
        if label_file:
            raise NotImplementedError
        if source_file and source_file in FileLabelProcessor.DEFAULT_LABELS:
            self.value = FileLabelProcessor.DEFAULT_LABELS[source_file]
        else:
            self.value = label_value if label_value else None
        log.info(f"Label for data: {self.value}")

    def process(self, features: Dict[IFeature, Any]):
        if self.value:
            features[PredictionField.GROUND_TRUTH] = self.value

        return features
