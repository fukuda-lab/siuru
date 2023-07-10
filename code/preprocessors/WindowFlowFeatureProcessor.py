import time
from collections import defaultdict
from typing import Dict

from common.features import (
    flow_identifier,
    PacketFeature as Packet,
    FlowFeature as Flow,
    SampleGenerator,
    FlowIdentifier,
)
from common.functions import report_performance
from common.pipeline_logger import PipelineLogger

from preprocessors.IPreprocessor import IPreprocessor


class WindowFlowFeatureProcessor(IPreprocessor):
    """
    Stores flow statistics during a time window every time a packet is processed.
    Yields if the last yield for the flow identifier was more than <window> ago.
    After yield, the values for the flow identifier are reset.

    Note that the processor does not implement a sliding window: after a sample is
    yielded, all statistics for the flow are reset.
    """

    def __init__(self, window_size_ms: int = 1000, **kwargs):
        self.overall_packet_counter = 0
        self.valid_packet_counter = 0
        # Save window sizes in microseconds as these are the timestamps
        # returned from C++ packet processor.
        self.window_size_micros = window_size_ms * 1000
        self.window_packet_count: Dict[FlowIdentifier, int] = defaultdict(lambda: 0)
        self.window_packet_size_sum: Dict[FlowIdentifier, int] = defaultdict(lambda: 0)

        self.first_timestamp_after_yield: Dict[FlowIdentifier, int] = {}
        self.last_timestamp: Dict[FlowIdentifier, int] = defaultdict(lambda: 0)
        self.window_sum_inter_arrival_times: Dict[FlowIdentifier, int] = defaultdict(
            lambda: 0
        )

    def process(self, samples: SampleGenerator) -> SampleGenerator:
        sum_processing_time = 0
        packet_count = 0

        for s in samples:
            start_time_ref = time.process_time_ns()

            flow_id: FlowIdentifier = flow_identifier(s)
            timestamp = s[Packet.TIMESTAMP]

            if flow_id not in self.first_timestamp_after_yield:
                self.first_timestamp_after_yield[flow_id] = timestamp

            if timestamp - self.first_timestamp_after_yield[flow_id] > self.window_size_micros:

                # Set new features for this sample based on packets in the window
                # so far, excluding the current received one.
                s[Flow.WINDOW_AVG_PACKET_SIZE] = (
                    self.window_packet_size_sum[flow_id]
                    / self.window_packet_count[flow_id]
                )
                s[Flow.WINDOW_AVG_INTER_ARRIVAL_TIME] = (
                    self.window_sum_inter_arrival_times[flow_id]
                    / self.window_packet_count[flow_id]
                )
                s[Flow.WINDOW_RECEIVED_PACKET_COUNT] = self.window_packet_count[flow_id]
                s[Flow.WINDOW_SUM_PACKET_SIZE] = self.window_packet_size_sum[flow_id]

                # Reset counters for this flow.
                self.window_packet_count[flow_id] = 1
                self.window_packet_size_sum[flow_id] = s[Packet.IP_PACKET_SIZE]
                self.window_sum_inter_arrival_times[flow_id] = timestamp - self.last_timestamp[flow_id]
                self.last_timestamp[flow_id] = timestamp
                self.first_timestamp_after_yield[flow_id] = timestamp

                sum_processing_time += time.process_time_ns() - start_time_ref
                packet_count += 1
                yield s

            else:
                # Process the packet, but yield nothing.
                self.window_packet_count[flow_id] += 1
                self.window_packet_size_sum[flow_id] += s[Packet.IP_PACKET_SIZE]
                if self.last_timestamp[flow_id] != 0:
                    self.window_sum_inter_arrival_times[flow_id] += timestamp - self.last_timestamp[flow_id]
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
