import enum
from typing import NewType, Union, Dict, Any


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
    CPP_FEATURE_STRING = "cpp_feature_string"


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
    Features related to a flow (src_ip + src_port + dst_ip + dst_port + protocol).
    Generated on-the-fly as packets arrive, so the communication between hosts might
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


class PredictionField(str, enum.Enum):
    MODEL_NAME = "model_name"
    OUTPUT_BINARY = "output_binary"
    OUTPUT_CONFIDENCE = "output_confidence"
    OUTPUT_MULTILABEL = "output_multilabel"
    GROUND_TRUTH = "ground_truth"


# IFeature is one component of a data point throughout the pipeline,
# including processing results and metadata.
IFeature = NewType("IFeature", Union[PacketFeature, HostFeature, FlowFeature, PredictionField])


def flow_identifier(input_data: (Dict[IFeature, Any])):
    return (
        input_data[PacketFeature.IP_SOURCE_ADDRESS],
        input_data[PacketFeature.IP_DESTINATION_ADDRESS],
        input_data[PacketFeature.IP_SOURCE_PORT],
        input_data[PacketFeature.IP_DESTINATION_PORT],
        input_data[PacketFeature.PROTOCOL]
    )
