import time
from typing import Dict, List, Optional, Any

from common.features import IFeature, PredictionField, PacketFeature, FeatureGenerator
from common.functions import report_performance
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
            # TODO Allow loading files with labels if some dataset requires it.
            raise NotImplementedError
        if source_file and source_file in FileLabelProcessor.DEFAULT_LABELS:
            self.value = FileLabelProcessor.DEFAULT_LABELS[source_file]
        else:
            self.value = label_value
        log.info(f"Label for data: {self.value}")

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()
            if self.value is not None:
                f[PredictionField.GROUND_TRUTH] = self.value

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1
            yield f

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
