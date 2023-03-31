import time
from collections import defaultdict
from typing import Dict, Tuple

from common.features import (
    flow_identifier,
    PacketFeature as Packet,
    FlowFeature as Flow,
    FeatureGenerator,
)
from common.functions import report_performance
from pipeline_logger import PipelineLogger

from preprocessors.IPreprocessor import IPreprocessor


class FlowFeatureProcessor(IPreprocessor):
    def __init__(self):
        self.overall_packet_counter = 0
        self.valid_packet_counter = 0

        self.packet_count_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

        self.packet_size_sum_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

        self.first_timestamp_by_flow: Dict[Tuple[str, str, int, int, str], int] = {}

        self.last_timestamp_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.last_timestamp_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

        self.sum_inter_arrival_times_by_flow: Dict[
            Tuple[str, str, int, int, str], int
        ] = defaultdict(lambda: 0)

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()

            flow_id: Tuple[str, str, int, int, str] = flow_identifier(f)

            self.packet_count_by_flow[flow_id] += 1
            self.packet_size_sum_by_flow[flow_id] += f[Packet.IP_PACKET_SIZE]

            if flow_id not in self.first_timestamp_by_flow:
                # TODO switch to NaN? Needs special handling in decision trees.
                flow_last_inter_arrival_time = 0
                flow_avg_inter_arrival_time = 0
                flow_connection_duration = 0
                self.first_timestamp_by_flow[flow_id] = f[Packet.TIMESTAMP]
            else:
                flow_last_inter_arrival_time = (
                    f[Packet.TIMESTAMP] - self.last_timestamp_by_flow[flow_id]
                )
                self.sum_inter_arrival_times_by_flow[
                    flow_id
                ] += flow_last_inter_arrival_time
                flow_avg_inter_arrival_time = self.sum_inter_arrival_times_by_flow[
                    flow_id
                ] / (self.packet_count_by_flow[flow_id] - 1)
                self.last_timestamp_by_flow[flow_id] = f[Packet.TIMESTAMP]
                flow_connection_duration = (
                    self.last_timestamp_by_flow[flow_id]
                    - self.first_timestamp_by_flow[flow_id]
                )

            f[Flow.RECEIVED_PACKET_COUNT] = self.packet_count_by_flow[flow_id]
            f[Flow.SUM_PACKET_SIZE] = self.packet_size_sum_by_flow[flow_id]
            f[Flow.AVG_PACKET_SIZE] = (
                self.packet_size_sum_by_flow[flow_id]
                / self.packet_count_by_flow[flow_id]
            )
            f[Flow.LAST_INTER_ARRIVAL_TIME] = flow_last_inter_arrival_time
            f[Flow.AVG_INTER_ARRIVAL_TIME] = flow_avg_inter_arrival_time
            f[Flow.CONNECTION_DURATION] = flow_connection_duration

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1
            yield f

        log = PipelineLogger.get_logger()
        report_performance(type(self).__name__, log, packet_count, sum_processing_time)

    @staticmethod
    def input_signature():
        return [
            Packet.IP_PACKET_SIZE,
            Packet.TCP_CWR_FLAG,
            Packet.TCP_ECE_FLAG,
            Packet.TCP_URG_FLAG,
            Packet.TCP_ACK_FLAG,
            Packet.TCP_PSH_FLAG,
            Packet.TCP_RST_FLAG,
            Packet.TCP_SYN_FLAG,
            Packet.TCP_FIN_FLAG,
        ]

    @staticmethod
    def output_signature():
        return [
            Flow.RECEIVED_PACKET_COUNT,
            Flow.SUM_PACKET_SIZE,
            Flow.AVG_PACKET_SIZE,
            Flow.LAST_INTER_ARRIVAL_TIME,
            Flow.AVG_INTER_ARRIVAL_TIME,
            Flow.CONNECTION_DURATION,
        ]
