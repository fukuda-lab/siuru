import time
from collections import defaultdict
from typing import Dict, Any, Tuple

from pandas import Timestamp, Timedelta

from common.features import (
    IFeature,
    flow_identifier,
    PacketFeature as Packet,
    FlowFeature as Flow,
    FeatureGenerator,
    FlowIdentifier,
)
from common.functions import report_performance
from pipeline_logger import PipelineLogger

from preprocessors.IPreprocessor import IPreprocessor


class WindowFlowFeatureProcessor(IPreprocessor):
    """
    Stores flow statistics during a time window every time a packet is processed.
    Yields if the last yield for the flow identifier was more than <window> ago.
    After yield, the values for the flow identifier are reset.
    """

    def __init__(self, window_size_ms: int = 1000, **kwargs):
        self.overall_packet_counter = 0
        self.valid_packet_counter = 0
        self.window_size = Timedelta(window_size_ms, unit="milliseconds")

        self.window_packet_count: Dict[FlowIdentifier, int] = defaultdict(lambda: 0)

        self.window_packet_size_sum: Dict[FlowIdentifier, int] = defaultdict(lambda: 0)

        self.first_timestamp_after_yield: Dict[FlowIdentifier, Timestamp] = defaultdict(
            lambda: Timestamp(0)
        )

        self.last_timestamp: Dict[FlowIdentifier, Timestamp] = defaultdict(
            lambda: Timestamp(0)
        )

        self.window_sum_inter_arrival_times: Dict[
            FlowIdentifier, Timedelta
        ] = defaultdict(lambda: Timedelta(0))

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        for f in features:
            start_time_ref = time.process_time_ns()

            flow_id: FlowIdentifier = flow_identifier(f)
            timestamp = f[Packet.TIMESTAMP]

            if flow_id not in self.first_timestamp_after_yield:
                self.first_timestamp_after_yield[flow_id] = timestamp

            if timestamp - self.first_timestamp_after_yield[flow_id] > self.window_size:
                f[Flow.WINDOW_AVG_PACKET_SIZE] = (
                    self.window_packet_size_sum[flow_id]
                    / self.window_packet_count[flow_id]
                )
                f[Flow.WINDOW_AVG_INTER_ARRIVAL_TIME] = (
                    self.window_sum_inter_arrival_times[flow_id]
                    / self.window_packet_count[flow_id]
                ).value
                f[Flow.WINDOW_RECEIVED_PACKET_COUNT] = self.window_packet_count[flow_id]
                f[Flow.WINDOW_SUM_PACKET_SIZE] = self.window_packet_size_sum[flow_id]

                self.window_packet_count[flow_id] = 1
                self.window_packet_size_sum[flow_id] = f[Packet.IP_PACKET_SIZE]
                self.window_sum_inter_arrival_times[flow_id] = (
                    timestamp - self.last_timestamp[flow_id]
                )
                self.last_timestamp[flow_id] = timestamp
                self.first_timestamp_after_yield[flow_id] = timestamp

                sum_processing_time += time.process_time_ns() - start_time_ref
                packet_count += 1
                yield f

            else:
                # Process the packet, but yield nothing.
                self.window_packet_count[flow_id] += 1
                self.window_packet_size_sum[flow_id] += f[Packet.IP_PACKET_SIZE]
                self.window_sum_inter_arrival_times[flow_id] += (
                    timestamp - self.last_timestamp[flow_id]
                )
                self.last_timestamp[flow_id] = timestamp

                sum_processing_time += time.process_time_ns() - start_time_ref
                packet_count += 1

        log = PipelineLogger.get_logger()
        report_performance(type(self).__name__, log, packet_count, sum_processing_time)



    @staticmethod
    def input_signature():
        return [
            Packet.IP_PACKET_SIZE,
            Packet.IP_SOURCE_ADDRESS,
            Packet.IP_DESTINATION_ADDRESS,
            Packet.IP_SOURCE_PORT,
            Packet.IP_DESTINATION_PORT,
            Packet.PROTOCOL,
            Packet.TIMESTAMP,
        ]

    @staticmethod
    def output_signature():
        return [
            Flow.WINDOW_AVG_PACKET_SIZE,
            Flow.WINDOW_AVG_INTER_ARRIVAL_TIME,
            Flow.WINDOW_RECEIVED_PACKET_COUNT,
            Flow.WINDOW_SUM_PACKET_SIZE,
        ]
