import enum
import json
import re
import pandas

from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class PacketFeature(str, enum.Enum):
    """
    Features describing a single packet.
    """

    TIMESTAMP = "timestamp"
    IP_SOURCE_ADDRESS = "ip_src_addr"
    IP_DESTINATION_ADDRESS = "ip_dst_addr"
    IP_SOURCE_PORT = "ip_src_port"
    IP_DESTINATION_PORT = "ip_dst_port"
    PROTOCOL = "proto"
    IP_PACKET_SIZE = "ip_size"
    TCP_CWR_FLAG = "tcp_cwr"
    TCP_ECE_FLAG = "tcp_ece"
    TCP_URG_FLAG = "tcp_urg"
    TCP_ACK_FLAG = "tcp_ack"
    TCP_PSH_FLAG = "tcp_psh"
    TCP_RST_FLAG = "tcp_rst"
    TCP_SYN_FLAG = "tcp_syn"
    TCP_FIN_FLAG = "tcp_fin"


class HostFeature(str, enum.Enum):
    """
    Features related to a specific host (unique IP address).
    TODO Add features based on time windows, see Kitsune paper for sensible defaults.
    """

    RECEIVED_PACKET_COUNT = "host_rcv_pkt_count"
    SUM_RECEIVED_PACKET_SIZE = "host_sum_rcv_pkt_size"
    AVG_RECEIVED_PACKET_SIZE = "host_avg_rcv_pkt_size"

    SENT_PACKET_COUNT = "host_sent_pkt_count"
    SUM_SENT_PACKET_SIZE = "host_sum_sent_pkt_size"
    AVG_SENT_PACKET_SIZE = "host_avg_sent_pkt_size"

    LAST_INTER_ARRIVAL_TIME = "host_inter_arrival_last"
    AVG_INTER_ARRIVAL_TIME = "host_inter_arrival_avg"

    # Relative to first received packet.
    CONNECTION_DURATION = "host_conn_timedelta"


class FlowFeature(str, enum.Enum):
    """
    Features related to a flow (src_ip + src_port + dst_ip + dst_port).
    Unlike standard flow-based features, open flow features are generated
    on-the-fly as packets arrive, so the communication between hosts might
    have not ended yet.
    TODO Also add features based on time windows here.
    """

    RECEIVED_PACKET_COUNT = "flow_pkt_count"
    SUM_PACKET_SIZE = "flow_sum_pkt_size"
    AVG_PACKET_SIZE = "flow_avg_pkt_size"

    LAST_INTER_ARRIVAL_TIME = "flow_inter_arrival_last"
    AVG_INTER_ARRIVAL_TIME = "flow_inter_arrival_avg"

    # Relative to first received packet.
    CONNECTION_DURATION = "flow_conn_timedelta"


class PacketData:
    input_pattern = re.compile(
        r"(?P<srcip>\S+)\s"
        r"(?P<dstip>\S+)\s"
        r"(?P<srcport>\S+)\s"
        r"(?P<dstport>\S+)\s"
        r"(?P<proto>\S+)\s"
        r"(?P<features>{.+})"
    )

    def __init__(self, feature_data: str, check: bool = False):
        matched_input = PacketData.input_pattern.match(feature_data)
        if matched_input:
            self.is_valid = True
            self.source_ip = matched_input.group("srcip")
            self.destination_ip = matched_input.group("dstip")
            self.source_port = matched_input.group("srcport")
            self.destination_port = matched_input.group("dstport")
            self.protocol = matched_input.group("proto")
            self.flow_identifier = (
                self.source_ip,
                self.destination_ip,
                self.source_port,
                self.destination_port,
                self.protocol,
            )
            self.features = json.loads(matched_input.group("features"))

            self.timestamp = pandas.to_datetime(self.features["ts"], unit="us")
            self.ip_size = self.features["ip_len"]

            self.flag_cwr = self.features["tcp_flags"][0]
            self.flag_ece = self.features["tcp_flags"][1]
            self.flag_urg = self.features["tcp_flags"][2]
            self.flag_ack = self.features["tcp_flags"][3]
            self.flag_psh = self.features["tcp_flags"][4]
            self.flag_rst = self.features["tcp_flags"][5]
            self.flag_syn = self.features["tcp_flags"][6]
            self.flag_fin = self.features["tcp_flags"][7]
        else:
            self.is_valid = False
