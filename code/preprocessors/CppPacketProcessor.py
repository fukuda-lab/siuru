import re
import time
from typing import List

import common.global_variables as global_variables
from common.features import IFeature, PacketFeature, SampleGenerator
from common.functions import report_performance
from preprocessors.IPreprocessor import IPreprocessor

from common.pipeline_logger import PipelineLogger


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
            PacketFeature.IP_HEADER_SIZE,
            PacketFeature.IP_DATA_SIZE,
            PacketFeature.TCP_CWR_FLAG,
            PacketFeature.TCP_ECE_FLAG,
            PacketFeature.TCP_URG_FLAG,
            PacketFeature.TCP_ACK_FLAG,
            PacketFeature.TCP_PSH_FLAG,
            PacketFeature.TCP_RST_FLAG,
            PacketFeature.TCP_SYN_FLAG,
            PacketFeature.TCP_FIN_FLAG,
            PacketFeature.TCP_HEADER_SIZE,
            PacketFeature.TCP_DATA_SIZE,
        ]

    def process(self, samples: SampleGenerator) -> SampleGenerator:
        sum_processing_time = 0
        valid_packet_count = 0
        invalid_packet_count = 0

        for s in samples:
            start_time_ref = time.process_time_ns()
            parts = s[PacketFeature.CPP_FEATURE_STRING].rstrip().split(",")
            if len(parts) != len(self.output_signature()) - 1:  # Deduct for TCP_DATA_SIZE.
                invalid_packet_count += 1
                continue

            s[PacketFeature.IP_SOURCE_ADDRESS] = parts[0]
            s[PacketFeature.IP_DESTINATION_ADDRESS] = parts[1]
            s[PacketFeature.IP_SOURCE_PORT] = parts[2]
            s[PacketFeature.IP_DESTINATION_PORT] = parts[3]
            s[PacketFeature.PROTOCOL] = parts[4]
            s[PacketFeature.TIMESTAMP] = int(parts[5])
            s[PacketFeature.IP_HEADER_SIZE] = int(parts[6])
            s[PacketFeature.IP_DATA_SIZE] = int(parts[7])
            s[PacketFeature.TCP_CWR_FLAG] = int(parts[8])
            s[PacketFeature.TCP_ECE_FLAG] = int(parts[9])
            s[PacketFeature.TCP_URG_FLAG] = int(parts[10])
            s[PacketFeature.TCP_ACK_FLAG] = int(parts[11])
            s[PacketFeature.TCP_PSH_FLAG] = int(parts[12])
            s[PacketFeature.TCP_RST_FLAG] = int(parts[13])
            s[PacketFeature.TCP_SYN_FLAG] = int(parts[14])
            s[PacketFeature.TCP_FIN_FLAG] = int(parts[15])
            s[PacketFeature.TCP_HEADER_SIZE] = int(parts[16])
            s[PacketFeature.TCP_DATA_SIZE] = s[PacketFeature.IP_DATA_SIZE] - s[PacketFeature.TCP_HEADER_SIZE]

            sum_processing_time += time.process_time_ns() - start_time_ref
            valid_packet_count += 1
            global_variables.global_sum_ip_packet_sizes += s[PacketFeature.IP_HEADER_SIZE]
            global_variables.global_sum_ip_packet_sizes += s[PacketFeature.IP_DATA_SIZE]
            yield s

        log = PipelineLogger.get_logger()
        log.info(
            f"[{type(self).__name__}] {invalid_packet_count} invalid packets dropped."
        )
        report_performance(
            type(self).__name__, log, valid_packet_count, sum_processing_time
        )
