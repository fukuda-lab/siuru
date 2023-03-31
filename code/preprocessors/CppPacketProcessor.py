import json
import re
import time
from typing import List, Any, Dict

import pandas

from common.features import IFeature, PacketFeature, FeatureGenerator
from common.functions import report_performance
from preprocessors.IPreprocessor import IPreprocessor

from pipeline_logger import PipelineLogger


class CppPacketProcessor(IPreprocessor):
    """
    Helper class to map C++ feature extractor output to features.
    """

    input_pattern = re.compile(
        r"(?P<srcip>\S+)\s"
        r"(?P<dstip>\S+)\s"
        r"(?P<srcport>\S+)\s"
        r"(?P<dstport>\S+)\s"
        r"(?P<proto>\S+)\s"
        r"(?P<features>{.+})"
    )

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [PacketFeature.CPP_FEATURE_STRING]

    @staticmethod
    def output_signature() -> List[IFeature]:
        return [
            PacketFeature.IP_SOURCE_ADDRESS,
            PacketFeature.IP_DESTINATION_ADDRESS,
            PacketFeature.IP_SOURCE_PORT,
            PacketFeature.IP_DESTINATION_PORT,
            PacketFeature.PROTOCOL,
            PacketFeature.TIMESTAMP,
            PacketFeature.IP_PACKET_SIZE,
            PacketFeature.TCP_CWR_FLAG,
            PacketFeature.TCP_ECE_FLAG,
            PacketFeature.TCP_URG_FLAG,
            PacketFeature.TCP_ACK_FLAG,
            PacketFeature.TCP_PSH_FLAG,
            PacketFeature.TCP_RST_FLAG,
            PacketFeature.TCP_SYN_FLAG,
            PacketFeature.TCP_FIN_FLAG,
        ]

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()
            matched_input = CppPacketProcessor.input_pattern.match(
                f[PacketFeature.CPP_FEATURE_STRING]
            )
            if not matched_input:
                continue

            cpp_features = json.loads(matched_input.group("features"))
            f[PacketFeature.IP_SOURCE_ADDRESS] = matched_input.group("srcip")
            f[PacketFeature.IP_DESTINATION_ADDRESS] = matched_input.group("dstip")
            f[PacketFeature.IP_SOURCE_PORT] = matched_input.group("srcport")
            f[PacketFeature.IP_DESTINATION_PORT] = matched_input.group("dstport")
            f[PacketFeature.PROTOCOL] = matched_input.group("proto")
            f[PacketFeature.TIMESTAMP] = pandas.to_datetime(
                cpp_features["ts"], unit="us"
            )
            f[PacketFeature.IP_PACKET_SIZE] = cpp_features["ip_len"]
            f[PacketFeature.TCP_CWR_FLAG] = cpp_features["tcp_flags"][0]
            f[PacketFeature.TCP_ECE_FLAG] = cpp_features["tcp_flags"][1]
            f[PacketFeature.TCP_URG_FLAG] = cpp_features["tcp_flags"][2]
            f[PacketFeature.TCP_ACK_FLAG] = cpp_features["tcp_flags"][3]
            f[PacketFeature.TCP_PSH_FLAG] = cpp_features["tcp_flags"][4]
            f[PacketFeature.TCP_RST_FLAG] = cpp_features["tcp_flags"][5]
            f[PacketFeature.TCP_SYN_FLAG] = cpp_features["tcp_flags"][6]
            f[PacketFeature.TCP_FIN_FLAG] = cpp_features["tcp_flags"][7]

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1
            yield f

        log = PipelineLogger.get_logger()
        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
