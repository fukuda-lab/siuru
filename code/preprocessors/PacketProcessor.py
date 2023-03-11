from collections import defaultdict
from typing import Dict, Any, Union
from typing import Tuple

from pandas import Timestamp, Timedelta

from prediction_output import PredictionField
from preprocessors.common import (
    PacketData,
    PacketFeature,
    HostFeature,
    FlowFeature,
)


class PacketProcessor:
    def __init__(self):
        self.overall_packet_counter = 0
        self.valid_packet_counter = 0

        self.packet_count_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_count_to_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_count_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

        self.packet_size_sum_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_size_sum_to_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_size_sum_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

        self.first_timestamp_from_host: Dict[str, Timestamp] = {}
        self.first_timestamp_by_flow: Dict[
            Tuple[str, str, int, int, str], Timestamp
        ] = {}

        self.last_timestamp_from_host: Dict[str, Timestamp] = defaultdict(
            lambda: Timestamp(0)
        )
        self.last_timestamp_by_flow: Dict[
            Tuple[str, str, int, int, str], Timestamp
        ] = defaultdict(lambda: Timestamp(0))

        self.sum_inter_arrival_times_from_host: Dict[str, Timedelta] = defaultdict(
            lambda: Timedelta(0)
        )
        self.sum_inter_arrival_times_by_flow: Dict[
            Tuple[str, str, int, int, str], Timedelta
        ] = defaultdict(lambda: Timedelta(0))

    def process(
        self, p: PacketData
    ) -> Dict[Union[PacketFeature, HostFeature, FlowFeature, PredictionField], float]:
        self.overall_packet_counter += 1
        if not p.is_valid:
            return None
        self.valid_packet_counter += 1

        self.packet_count_from_host[p.source_ip] += 1
        self.packet_count_to_host[p.destination_ip] += 1
        self.packet_count_by_flow[p.flow_identifier] += 1

        self.packet_size_sum_from_host[p.source_ip] += p.ip_size
        self.packet_size_sum_to_host[p.destination_ip] += p.ip_size
        self.packet_size_sum_by_flow[p.flow_identifier] += p.ip_size

        if p.source_ip not in self.first_timestamp_from_host:
            # TODO switch to NaN? Needs special handling in decision trees.
            host_last_inter_arrival_time = Timedelta(0)
            host_avg_inter_arrival_time = Timedelta(0)
            host_connection_duration = Timedelta(0)
            self.first_timestamp_from_host[p.source_ip] = p.timestamp
        else:
            host_last_inter_arrival_time = (
                p.timestamp - self.last_timestamp_from_host[p.source_ip]
            )
            self.sum_inter_arrival_times_from_host[
                p.source_ip
            ] += host_last_inter_arrival_time
            host_avg_inter_arrival_time = self.sum_inter_arrival_times_from_host[
                p.source_ip
            ] / (self.packet_count_from_host[p.source_ip] - 1)
            self.last_timestamp_from_host[p.source_ip] = p.timestamp
            host_connection_duration = (
                self.last_timestamp_from_host[p.source_ip]
                - self.first_timestamp_from_host[p.source_ip]
            )

        if p.flow_identifier not in self.first_timestamp_by_flow:
            # TODO switch to NaN? Needs special handling in decision trees.
            flow_last_inter_arrival_time = Timedelta(0)
            flow_avg_inter_arrival_time = Timedelta(0)
            flow_connection_duration = Timedelta(0)
            self.first_timestamp_by_flow[p.flow_identifier] = p.timestamp
        else:
            flow_last_inter_arrival_time = (
                p.timestamp - self.last_timestamp_by_flow[p.flow_identifier]
            )
            self.sum_inter_arrival_times_by_flow[
                p.flow_identifier
            ] += flow_last_inter_arrival_time
            flow_avg_inter_arrival_time = self.sum_inter_arrival_times_by_flow[
                p.flow_identifier
            ] / (self.packet_count_by_flow[p.flow_identifier] - 1)
            self.last_timestamp_by_flow[p.flow_identifier] = p.timestamp
            flow_connection_duration = (
                self.last_timestamp_by_flow[p.flow_identifier]
                - self.first_timestamp_by_flow[p.flow_identifier]
            )

        return {
            PacketFeature.IP_PACKET_SIZE: p.ip_size,
            PacketFeature.TCP_CWR_FLAG: p.flag_cwr,
            PacketFeature.TCP_ECE_FLAG: p.flag_ece,
            PacketFeature.TCP_URG_FLAG: p.flag_urg,
            PacketFeature.TCP_ACK_FLAG: p.flag_ack,
            PacketFeature.TCP_PSH_FLAG: p.flag_psh,
            PacketFeature.TCP_RST_FLAG: p.flag_rst,
            PacketFeature.TCP_SYN_FLAG: p.flag_syn,
            PacketFeature.TCP_FIN_FLAG: p.flag_fin,
            HostFeature.RECEIVED_PACKET_COUNT: self.packet_count_from_host[p.source_ip],
            HostFeature.SUM_RECEIVED_PACKET_SIZE: self.packet_size_sum_from_host[
                p.source_ip
            ],
            HostFeature.AVG_RECEIVED_PACKET_SIZE: self.packet_size_sum_from_host[
                p.source_ip
            ]
            / self.packet_count_from_host[p.source_ip],
            HostFeature.SENT_PACKET_COUNT: self.packet_count_to_host[p.destination_ip],
            HostFeature.SUM_SENT_PACKET_SIZE: self.packet_size_sum_to_host[
                p.destination_ip
            ],
            HostFeature.AVG_SENT_PACKET_SIZE: self.packet_size_sum_from_host[
                p.source_ip
            ]
            / self.packet_count_to_host[p.destination_ip],
            HostFeature.LAST_INTER_ARRIVAL_TIME: host_last_inter_arrival_time.value,
            HostFeature.AVG_INTER_ARRIVAL_TIME: host_avg_inter_arrival_time.value,
            HostFeature.CONNECTION_DURATION: host_connection_duration.value,
            FlowFeature.RECEIVED_PACKET_COUNT: self.packet_count_by_flow[
                p.flow_identifier
            ],
            FlowFeature.SUM_PACKET_SIZE: self.packet_size_sum_by_flow[
                p.flow_identifier
            ],
            FlowFeature.AVG_PACKET_SIZE: self.packet_size_sum_by_flow[p.flow_identifier]
            / self.packet_count_by_flow[p.flow_identifier],
            FlowFeature.LAST_INTER_ARRIVAL_TIME: flow_last_inter_arrival_time.value,
            FlowFeature.AVG_INTER_ARRIVAL_TIME: flow_avg_inter_arrival_time.value,
            FlowFeature.CONNECTION_DURATION: flow_connection_duration.value,
        }

    @staticmethod
    def signature():
        return [
            PacketFeature.IP_PACKET_SIZE,
            PacketFeature.TCP_CWR_FLAG,
            PacketFeature.TCP_ECE_FLAG,
            PacketFeature.TCP_URG_FLAG,
            PacketFeature.TCP_ACK_FLAG,
            PacketFeature.TCP_PSH_FLAG,
            PacketFeature.TCP_RST_FLAG,
            PacketFeature.TCP_SYN_FLAG,
            PacketFeature.TCP_FIN_FLAG,
            HostFeature.RECEIVED_PACKET_COUNT,
            HostFeature.SUM_RECEIVED_PACKET_SIZE,
            HostFeature.AVG_RECEIVED_PACKET_SIZE,
            HostFeature.SENT_PACKET_COUNT,
            HostFeature.SUM_SENT_PACKET_SIZE,
            HostFeature.AVG_SENT_PACKET_SIZE,
            HostFeature.LAST_INTER_ARRIVAL_TIME,
            HostFeature.AVG_INTER_ARRIVAL_TIME,
            HostFeature.CONNECTION_DURATION,
            FlowFeature.RECEIVED_PACKET_COUNT,
            FlowFeature.SUM_PACKET_SIZE,
            FlowFeature.AVG_PACKET_SIZE,
            FlowFeature.LAST_INTER_ARRIVAL_TIME,
            FlowFeature.AVG_INTER_ARRIVAL_TIME,
            FlowFeature.CONNECTION_DURATION,
        ]
