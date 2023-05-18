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
            PacketFeature.TCP_SEGMENT_SIZE,
        ]

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        valid_packet_count = 0
        invalid_packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()
            parts = f[PacketFeature.CPP_FEATURE_STRING].rstrip().split(",")
            if len(parts) != 16:
                invalid_packet_count += 1
                continue

            f[PacketFeature.IP_SOURCE_ADDRESS] = parts[0]
            f[PacketFeature.IP_DESTINATION_ADDRESS] = parts[1]
            f[PacketFeature.IP_SOURCE_PORT] = parts[2]
            f[PacketFeature.IP_DESTINATION_PORT] = parts[3]
            f[PacketFeature.PROTOCOL] = parts[4]
            f[PacketFeature.TIMESTAMP] = int(parts[5])
            f[PacketFeature.IP_PACKET_SIZE] = int(parts[6])
            f[PacketFeature.TCP_CWR_FLAG] = int(parts[7])
            f[PacketFeature.TCP_ECE_FLAG] = int(parts[8])
            f[PacketFeature.TCP_URG_FLAG] = int(parts[9])
            f[PacketFeature.TCP_ACK_FLAG] = int(parts[10])
            f[PacketFeature.TCP_PSH_FLAG] = int(parts[11])
            f[PacketFeature.TCP_RST_FLAG] = int(parts[12])
            f[PacketFeature.TCP_SYN_FLAG] = int(parts[13])
            f[PacketFeature.TCP_FIN_FLAG] = int(parts[14])
            f[PacketFeature.TCP_SEGMENT_SIZE] = int(parts[15])

            sum_processing_time += time.process_time_ns() - start_time_ref
            valid_packet_count += 1
            yield f

        log = PipelineLogger.get_logger()
        log.info(
            f"[{type(self).__name__}] {invalid_packet_count} invalid packets dropped."
        )
        report_performance(
            type(self).__name__, log, valid_packet_count, sum_processing_time
        )
