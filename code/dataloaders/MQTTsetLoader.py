import subprocess
from collections import defaultdict
from typing import List, Union, Generator, Dict, Any, Tuple

import pandas as pd

from dataloaders.IDataLoader import IDataLoader
from preprocess_features import PacketFeature, HostFeature, OpenFlowFeature, PacketData

from pipeline_logger import PipelineLogger


class MQTTsetLoader(IDataLoader):
    SUPPORTED_FILES = [
        "MQTTset/Data/PCAP/capture_flood.pcap",
        "MQTTset/Data/PCAP/capture_1w.pcap",
        "MQTTset/Data/PCAP/capture_custom_1h.pcap",
        "MQTTset/Data/PCAP/slowite.pcap",
        "MQTTset/Data/PCAP/capture_malariaDoS.pcap",
    ]

    LABELS = {
        "MQTTset/Data/PCAP/capture_flood.pcap": [1 for _ in range(613)],
        "MQTTset/Data/PCAP/capture_1w.pcap": [0 for _ in range(11916329)],
        "MQTTset/Data/PCAP/capture_custom_1h.pcap": [0 for _ in range(70983)],
        "MQTTset/Data/PCAP/slowite.pcap": [1 for _ in range(9202)],
        "MQTTset/Data/PCAP/capture_malariaDoS.pcap": [1 for _ in range(130223)],
    }

    @staticmethod
    def can_load(filepath: str) -> bool:
        return IDataLoader._get_path_relative_to_data_dir(filepath) in MQTTsetLoader.SUPPORTED_FILES

    def preprocess(self, **kwargs) -> Generator[
            Dict[Union[PacketFeature, HostFeature, HostFeature], Any], None, None]:

        log = PipelineLogger.get_logger()

        assert kwargs["preprocessor_path"], kwargs["filepath"]
        preprocessor_path = kwargs["preprocessor_path"]
        filepath = kwargs["filepath"]

        log.info(f"[MQTTsetLoader] Processing file: {filepath}")

        pcap_call = [preprocessor_path, "stream-file", filepath]
        process = subprocess.Popen(pcap_call, stdout=subprocess.PIPE, universal_newlines=True)

        overall_packet_counter = 0
        packet_count_from_host: Dict[str, int] = defaultdict(lambda: 0)
        packet_count_by_flow: Dict[Tuple[str, str, int, int], int] = defaultdict(lambda: 0)

        packet_size_sum_from_host: Dict[str, int] = defaultdict(lambda: 0)
        packet_size_sum_by_flow: Dict[Tuple[str, str, int, int], int] = defaultdict(lambda: 0)

        first_timestamp_from_host: Dict[str, pd.Timestamp] = {}
        first_timestamp_by_flow: Dict[Tuple[str, str, int, int], pd.Timestamp] = {}

        last_timestamp_from_host: Dict[str, pd.Timestamp] = defaultdict(lambda: pd.Timestamp(0))
        last_timestamp_by_flow: Dict[Tuple[str, str, int, int], pd.Timestamp] = defaultdict(lambda: pd.Timestamp(0))

        sum_inter_arrival_times_from_host: Dict[str, pd.Timedelta] = defaultdict(lambda: pd.Timedelta(0))
        sum_inter_arrival_times_by_flow: Dict[Tuple[str, str, int, int], pd.Timedelta] = defaultdict(lambda: pd.Timedelta(0))

        for packet_features in process.stdout.readlines():
            p = PacketData(packet_features)

            if not p.is_valid:
                continue

            overall_packet_counter += 1
            packet_count_from_host[p.source_ip] += 1
            packet_count_by_flow[p.flow_identifier] += 1

            packet_size_sum_from_host[p.source_ip] += p.ip_size
            packet_size_sum_by_flow[p.flow_identifier] += p.ip_size

            if p.source_ip not in first_timestamp_from_host:
                host_last_inter_arrival_time = None
                host_avg_inter_arrival_time = None
                host_connection_duration = None
                first_timestamp_from_host[p.source_ip] = p.timestamp
            else:
                host_last_inter_arrival_time = p.timestamp - last_timestamp_from_host[p.source_ip]
                sum_inter_arrival_times_from_host[p.source_ip] += host_last_inter_arrival_time
                host_avg_inter_arrival_time = sum_inter_arrival_times_from_host[p.source_ip] / (
                            packet_count_from_host[p.source_ip] - 1)
                last_timestamp_from_host[p.source_ip] = p.timestamp
                host_connection_duration = last_timestamp_from_host[p.source_ip] - first_timestamp_from_host[
                    p.source_ip]

            if p.flow_identifier not in first_timestamp_by_flow:
                flow_last_inter_arrival_time = None
                flow_avg_inter_arrival_time = None
                flow_connection_duration = None
                first_timestamp_by_flow[p.flow_identifier] = p.timestamp
            else:
                flow_last_inter_arrival_time = p.timestamp - last_timestamp_by_flow[p.flow_identifier]
                sum_inter_arrival_times_by_flow[p.flow_identifier] += flow_last_inter_arrival_time
                flow_avg_inter_arrival_time = sum_inter_arrival_times_by_flow[p.flow_identifier] / (
                            packet_count_by_flow[p.flow_identifier] - 1)
                last_timestamp_by_flow[p.flow_identifier] = p.timestamp
                flow_connection_duration = last_timestamp_by_flow[p.flow_identifier] - first_timestamp_by_flow[
                    p.flow_identifier]

            # TODO Add stats on packets sent to host.
            yield {
                # PacketFeature.TIMESTAMP: p.timestamp,
                # PacketFeature.IP_SOURCE_ADDRESS: None,
                # PacketFeature.IP_DESTINATION_ADDRESS: None,
                PacketFeature.IP_PACKET_SIZE: p.ip_size,
                PacketFeature.TCP_CWR_FLAG: p.flag_cwr,
                PacketFeature.TCP_ECE_FLAG: p.flag_ece,
                PacketFeature.TCP_URG_FLAG: p.flag_urg,
                PacketFeature.TCP_ACK_FLAG: p.flag_ack,
                PacketFeature.TCP_PSH_FLAG: p.flag_psh,
                PacketFeature.TCP_RST_FLAG: p.flag_rst,
                PacketFeature.TCP_SYN_FLAG: p.flag_syn,
                PacketFeature.TCP_FIN_FLAG: p.flag_fin,

                HostFeature.RECEIVED_PACKET_COUNT: packet_count_from_host[p.source_ip],
                HostFeature.SUM_RECEIVED_PACKET_SIZE: packet_size_sum_from_host[p.source_ip],
                HostFeature.AVG_RECEIVED_PACKET_SIZE: packet_size_sum_from_host[p.source_ip] / packet_count_from_host[
                    p.source_ip],
                # HostFeature.SENT_PACKET_COUNT: None,
                # HostFeature.SUM_SENT_PACKET_SIZE: None,
                # HostFeature.AVG_SENT_PACKET_SIZE: None,
                # HostFeature.LAST_INTER_ARRIVAL_TIME: host_last_inter_arrival_time,
                # HostFeature.AVG_INTER_ARRIVAL_TIME: host_avg_inter_arrival_time,
                # HostFeature.CONNECTION_DURATION: host_connection_duration,

                OpenFlowFeature.RECEIVED_PACKET_COUNT: packet_count_by_flow[p.flow_identifier],
                OpenFlowFeature.SUM_PACKET_SIZE: packet_size_sum_by_flow[p.flow_identifier],
                OpenFlowFeature.AVG_PACKET_SIZE: packet_size_sum_by_flow[p.flow_identifier] / packet_count_by_flow[
                    p.flow_identifier],
                # OpenFlowFeature.LAST_INTER_ARRIVAL_TIME: flow_last_inter_arrival_time,
                # OpenFlowFeature.AVG_INTER_ARRIVAL_TIME: flow_avg_inter_arrival_time,
                # OpenFlowFeature.CONNECTION_DURATION: flow_connection_duration,
            }

        log.info(f"[MQTTsetLoader] Extracted and processed {overall_packet_counter} packets.")

    @staticmethod
    def feature_signature() -> List[Union[PacketFeature, HostFeature, OpenFlowFeature]]:
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

            OpenFlowFeature.RECEIVED_PACKET_COUNT,
            OpenFlowFeature.SUM_PACKET_SIZE,
            OpenFlowFeature.AVG_PACKET_SIZE
        ]

    def get_labels(self, **kwargs) -> Generator[Any, None, None]:
        assert kwargs["filepath"]
        yield from MQTTsetLoader.LABELS[IDataLoader._get_path_relative_to_data_dir(kwargs["filepath"])]
