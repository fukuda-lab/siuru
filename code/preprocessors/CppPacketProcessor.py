import json
import re
from typing import List, Any, Dict

import pandas

from common.features import IFeature, PacketFeature
from preprocessors.IPreprocessor import IPreprocessor


class CppPacketData(IPreprocessor):
    """
    Helper class to map C++ feature extractor output to features.
    """

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

    input_pattern = re.compile(
        r"(?P<srcip>\S+)\s"
        r"(?P<dstip>\S+)\s"
        r"(?P<srcport>\S+)\s"
        r"(?P<dstport>\S+)\s"
        r"(?P<proto>\S+)\s"
        r"(?P<features>{.+})"
    )

    def process(self, input_data: Dict[IFeature, Any]):
        matched_input = CppPacketData.input_pattern.match(
            input_data[PacketFeature.CPP_FEATURE_STRING]
        )

        if matched_input:
            features = json.loads(matched_input.group("features"))
            return {
                PacketFeature.IP_SOURCE_ADDRESS: matched_input.group("srcip"),
                PacketFeature.IP_DESTINATION_ADDRESS: matched_input.group("dstip"),
                PacketFeature.IP_SOURCE_PORT: matched_input.group("srcport"),
                PacketFeature.IP_DESTINATION_PORT: matched_input.group("dstport"),
                PacketFeature.PROTOCOL: matched_input.group("proto"),
                PacketFeature.TIMESTAMP: pandas.to_datetime(features["ts"], unit="us"),
                PacketFeature.IP_PACKET_SIZE: features["ip_len"],
                PacketFeature.TCP_CWR_FLAG: features["tcp_flags"][0],
                PacketFeature.TCP_ECE_FLAG: features["tcp_flags"][1],
                PacketFeature.TCP_URG_FLAG: features["tcp_flags"][2],
                PacketFeature.TCP_ACK_FLAG: features["tcp_flags"][3],
                PacketFeature.TCP_PSH_FLAG: features["tcp_flags"][4],
                PacketFeature.TCP_RST_FLAG: features["tcp_flags"][5],
                PacketFeature.TCP_SYN_FLAG: features["tcp_flags"][6],
                PacketFeature.TCP_FIN_FLAG: features["tcp_flags"][7],
            }
