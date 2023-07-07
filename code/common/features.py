import enum
import itertools
from typing import NewType, Union, Dict, Any, Generator, Tuple


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
    TCP_SEGMENT_SIZE = "tcp_size"
    CPP_FEATURE_STRING = "cpp_feature_string"
    SOURCE_FILE_NAME = "source_file_name"


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
    """

    RECEIVED_PACKET_COUNT = "flow_pkt_count"
    SUM_PACKET_SIZE = "flow_sum_pkt_size"
    AVG_PACKET_SIZE = "flow_avg_pkt_size"

    WINDOW_RECEIVED_PACKET_COUNT = "window_flow_pkt_count"
    WINDOW_SUM_PACKET_SIZE = "window_flow_sum_pkt_size"
    WINDOW_AVG_PACKET_SIZE = "window_flow_avg_pkt_size"

    LAST_INTER_ARRIVAL_TIME = "flow_inter_arrival_last"
    AVG_INTER_ARRIVAL_TIME = "flow_inter_arrival_avg"
    WINDOW_AVG_INTER_ARRIVAL_TIME = "window_flow_inter_arrival_avg"

    # Relative to first received packet.
    CONNECTION_DURATION = "flow_conn_timedelta"


class PredictionField(str, enum.Enum):
    MODEL_NAME = "model_name"
    OUTPUT_BINARY = "output_binary"
    OUTPUT_CONFIDENCE = "output_confidence"
    OUTPUT_MULTILABEL = "output_multilabel"
    OUTPUT_DISTANCE = "output_distance"
    GROUND_TRUTH = "ground_truth"


# IFeature is one component of a data point throughout the pipeline,
# including processing results and metadata.
IFeature = NewType(
    "IFeature", Union[PacketFeature, HostFeature, FlowFeature, PredictionField]
)


def resolve_feature(feature_tag: str) -> IFeature:
    feature_enums = [PacketFeature, HostFeature, FlowFeature, PredictionField]
    f: IFeature
    for f in itertools.chain(*feature_enums):
        if feature_tag == f.value:
            return f
    return None


# TODO can these be specified further? Otherwise, might just as well use 'Any'.
DataType = NewType("DataType", Any)
EncodedData = NewType("EncodedData", Any)

FeatureGenerator = NewType(
    "FeatureGenerator", Generator[Dict[IFeature, DataType], None, None]
)

LabeledFeatureGenerator = NewType(
    "LabeledFeatureGenerator",
    Generator[Tuple[Dict[IFeature, DataType], EncodedData], None, None],
)

FlowIdentifier = NewType("FlowIdentifier", Tuple[str, str, int, int, str])


def flow_identifier(input_data: (Dict[IFeature, Any])) -> FlowIdentifier:
    return (
        input_data[PacketFeature.IP_SOURCE_ADDRESS],
        input_data[PacketFeature.IP_DESTINATION_ADDRESS],
        input_data[PacketFeature.IP_SOURCE_PORT],
        input_data[PacketFeature.IP_DESTINATION_PORT],
        input_data[PacketFeature.PROTOCOL],
    )
