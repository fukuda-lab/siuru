import json
import re
from typing import List, Any, Dict

import pandas

from common.features import IFeature, PacketFeature
from preprocessors.IPreprocessor import IPreprocessor


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

    def process(self, features: Dict[IFeature, Any]):
        matched_input = CppPacketProcessor.input_pattern.match(
            features[PacketFeature.CPP_FEATURE_STRING]
        )
        if not matched_input:
            return

        cpp_features = json.loads(matched_input.group("features"))
        features[PacketFeature.IP_SOURCE_ADDRESS] = matched_input.group("srcip")
        features[PacketFeature.IP_DESTINATION_ADDRESS] = matched_input.group("dstip")
        features[PacketFeature.IP_SOURCE_PORT] = matched_input.group("srcport")
        features[PacketFeature.IP_DESTINATION_PORT] = matched_input.group("dstport")
        features[PacketFeature.PROTOCOL] = matched_input.group("proto")
        features[PacketFeature.TIMESTAMP] = pandas.to_datetime(
            cpp_features["ts"], unit="us"
        )
        features[PacketFeature.IP_PACKET_SIZE] = cpp_features["ip_len"]
        features[PacketFeature.TCP_CWR_FLAG] = cpp_features["tcp_flags"][0]
        features[PacketFeature.TCP_ECE_FLAG] = cpp_features["tcp_flags"][1]
        features[PacketFeature.TCP_URG_FLAG] = cpp_features["tcp_flags"][2]
        features[PacketFeature.TCP_ACK_FLAG] = cpp_features["tcp_flags"][3]
        features[PacketFeature.TCP_PSH_FLAG] = cpp_features["tcp_flags"][4]
        features[PacketFeature.TCP_RST_FLAG] = cpp_features["tcp_flags"][5]
        features[PacketFeature.TCP_SYN_FLAG] = cpp_features["tcp_flags"][6]
        features[PacketFeature.TCP_FIN_FLAG] = cpp_features["tcp_flags"][7]

        return features
