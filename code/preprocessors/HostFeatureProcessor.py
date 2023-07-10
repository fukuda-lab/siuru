import time
from collections import defaultdict
from typing import Dict

from common.features import (
    PacketFeature as Packet,
    HostFeature as Host,
    SampleGenerator,
)
from common.functions import report_performance
from common.pipeline_logger import PipelineLogger

from preprocessors.IPreprocessor import IPreprocessor


class HostFeatureProcessor(IPreprocessor):
    def __init__(self):
        self.overall_packet_counter = 0

        self.packet_count_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_count_to_host: Dict[str, int] = defaultdict(lambda: 0)

        self.packet_size_sum_from_host: Dict[str, int] = defaultdict(lambda: 0)
        self.packet_size_sum_to_host: Dict[str, int] = defaultdict(lambda: 0)

        self.first_timestamp_from_host: Dict[str, int] = {}
        self.last_timestamp_from_host: Dict[str, int] = {}

        self.sum_inter_arrival_times_from_host: Dict[str, int] = defaultdict(lambda: 0)

    def process(self, samples: SampleGenerator) -> SampleGenerator:
        sum_processing_time = 0
        packet_count = 0

        for s in samples:
            start_time_ref = time.process_time_ns()
            self.overall_packet_counter += 1

            src_ip = s[Packet.IP_SOURCE_ADDRESS]
            dst_ip = s[Packet.IP_DESTINATION_ADDRESS]

            self.packet_count_from_host[src_ip] += 1
            self.packet_count_to_host[dst_ip] += 1

            self.packet_size_sum_from_host[src_ip] += s[Packet.IP_PACKET_SIZE]
            self.packet_size_sum_to_host[dst_ip] += s[Packet.IP_PACKET_SIZE]

            if src_ip not in self.first_timestamp_from_host:
                # TODO switch to NaN? Needs special handling in decision trees.
                host_last_inter_arrival_time = 0
                host_avg_inter_arrival_time = 0
                self.first_timestamp_from_host[src_ip] = s[Packet.TIMESTAMP]
            else:
                host_last_inter_arrival_time = (
                    s[Packet.TIMESTAMP] - self.last_timestamp_from_host[src_ip]
                )

                self.sum_inter_arrival_times_from_host[
                    src_ip
                ] += host_last_inter_arrival_time

                host_avg_inter_arrival_time = self.sum_inter_arrival_times_from_host[
                    src_ip
                ] / (self.packet_count_from_host[src_ip] - 1)

            self.last_timestamp_from_host[src_ip] = s[Packet.TIMESTAMP]

            host_connection_duration = (
                self.last_timestamp_from_host[src_ip]
                - self.first_timestamp_from_host[src_ip]
            )

            s[Host.RECEIVED_PACKET_COUNT] = self.packet_count_from_host[src_ip]
            s[Host.SUM_RECEIVED_PACKET_SIZE] = self.packet_size_sum_from_host[src_ip]

            s[Host.AVG_RECEIVED_PACKET_SIZE] = (
                self.packet_size_sum_from_host[src_ip]
                / self.packet_count_from_host[src_ip]
            )

            s[Host.SENT_PACKET_COUNT] = self.packet_count_to_host[dst_ip]
            s[Host.SUM_SENT_PACKET_SIZE] = self.packet_size_sum_to_host[dst_ip]
            s[Host.AVG_SENT_PACKET_SIZE] = (
                self.packet_size_sum_from_host[src_ip]
                / self.packet_count_to_host[dst_ip]
            )

            s[Host.LAST_INTER_ARRIVAL_TIME] = host_last_inter_arrival_time
            s[Host.AVG_INTER_ARRIVAL_TIME] = host_avg_inter_arrival_time
            s[Host.CONNECTION_DURATION] = host_connection_duration

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1

            yield s

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
