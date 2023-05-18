import time
from collections import defaultdict
from typing import Dict, Any

from pandas import Timestamp, Timedelta

from common.features import (
    IFeature,
    PacketFeature as Packet,
    HostFeature as Host,
    FeatureGenerator,
)
from common.functions import report_performance
from pipeline_logger import PipelineLogger

from preprocessors.IPreprocessor import IPreprocessor


class HostFeatureProcessor(IPreprocessor):
    def __init__(self):
        self.overall_packet_counter = 0

        self.packet_count_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_count_to_host: Dict[str, int] = defaultdict(lambda: 0)

        self.packet_size_sum_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_size_sum_to_host: Dict[str, int] = defaultdict(lambda: 0)

        self.first_timestamp_from_host: Dict[str, Timestamp] = {}
        self.last_timestamp_from_host: Dict[str, Timestamp] = {}

        self.sum_inter_arrival_times_from_host: Dict[str, int] = defaultdict(lambda: 0)

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()
            self.overall_packet_counter += 1

            src_ip = f[Packet.IP_SOURCE_ADDRESS]
            dst_ip = f[Packet.IP_DESTINATION_ADDRESS]

            self.packet_count_from_host[src_ip] += 1
            self.packet_count_to_host[dst_ip] += 1

            self.packet_size_sum_from_host[src_ip] += f[Packet.IP_PACKET_SIZE]
            self.packet_size_sum_to_host[dst_ip] += f[Packet.IP_PACKET_SIZE]

            if src_ip not in self.first_timestamp_from_host:
                # TODO switch to NaN? Needs special handling in decision trees.
                host_last_inter_arrival_time = 0
                host_avg_inter_arrival_time = 0
                self.first_timestamp_from_host[src_ip] = f[Packet.TIMESTAMP]
            else:
                host_last_inter_arrival_time = (
                    f[Packet.TIMESTAMP] - self.last_timestamp_from_host[src_ip]
                )

                self.sum_inter_arrival_times_from_host[
                    src_ip
                ] += host_last_inter_arrival_time

                host_avg_inter_arrival_time = self.sum_inter_arrival_times_from_host[
                    src_ip
                ] / (self.packet_count_from_host[src_ip] - 1)

            self.last_timestamp_from_host[src_ip] = f[Packet.TIMESTAMP]

            host_connection_duration = (
                self.last_timestamp_from_host[src_ip]
                - self.first_timestamp_from_host[src_ip]
            )

            f[Host.RECEIVED_PACKET_COUNT] = self.packet_count_from_host[src_ip]
            f[Host.SUM_RECEIVED_PACKET_SIZE] = self.packet_size_sum_from_host[src_ip]

            f[Host.AVG_RECEIVED_PACKET_SIZE] = (
                self.packet_size_sum_from_host[src_ip]
                / self.packet_count_from_host[src_ip]
            )

            f[Host.SENT_PACKET_COUNT] = self.packet_count_to_host[dst_ip]
            f[Host.SUM_SENT_PACKET_SIZE] = self.packet_size_sum_to_host[dst_ip]
            f[Host.AVG_SENT_PACKET_SIZE] = (
                self.packet_size_sum_from_host[src_ip]
                / self.packet_count_to_host[dst_ip]
            )

            f[Host.LAST_INTER_ARRIVAL_TIME] = host_last_inter_arrival_time
            f[Host.AVG_INTER_ARRIVAL_TIME] = host_avg_inter_arrival_time
            f[Host.CONNECTION_DURATION] = host_connection_duration

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
            Host.RECEIVED_PACKET_COUNT,
            Host.SUM_RECEIVED_PACKET_SIZE,
            Host.AVG_RECEIVED_PACKET_SIZE,
            Host.SENT_PACKET_COUNT,
            Host.SUM_SENT_PACKET_SIZE,
            Host.AVG_SENT_PACKET_SIZE,
            Host.LAST_INTER_ARRIVAL_TIME,
            Host.AVG_INTER_ARRIVAL_TIME,
            Host.CONNECTION_DURATION,
        ]
