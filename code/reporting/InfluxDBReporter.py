import time
from typing import Dict, Any, Optional

import influxdb_client
from influxdb_client import Point
from influxdb_client.client.exceptions import InfluxDBError

from common.features import PacketFeature, IFeature, PredictionField

from common import pipeline_logger
from common.functions import report_performance
from reporting.IReporter import IReporter

log = pipeline_logger.PipelineLogger.get_logger()


class InfluxDBReporter(IReporter):
    def __init__(
        self,
        influx_url,
        influx_org,
        influx_token,
        influx_bucket,
        measurement_name: Optional[str] = "anomaly_detection",
        **kwargs,
    ):
        if not influx_token:
            log.error("[InfluxDBReporter] Initialized without a token!")
            exit(1)

        self.url = influx_url
        self.org = influx_org
        self.token = influx_token
        self.bucket = influx_bucket
        self.measurement_name = measurement_name

        self.client = influxdb_client.InfluxDBClient(
            url=self.url,
            org=self.org,
            token=self.token,
        )
        self.logger = pipeline_logger.PipelineLogger.get_logger()
        self.write_api = self.client.write_api(
            success_callback=self.success,
            error_callback=self.error,
            retry_callback=self.retry,
        )
        self.logger.info(
            f"Initialized InfluxDB writer to {self.url} " f"[{self.org}/{self.bucket}]."
        )
        self.sum_processing_time = 0
        self.sample_count = 0

    def success(self, conf: (str, str, str), data: str):
        pass

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.error(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.info(
            f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}"
        )

    def report(self, features: Dict[IFeature, Any]):
        start_time_ref = time.process_time_ns()

        p = Point(self.measurement_name)
        p.tag(PredictionField.MODEL_NAME.value, features[PredictionField.MODEL_NAME])

        is_binary_classification = (
            PredictionField.OUTPUT_BINARY in features
            and PredictionField.GROUND_TRUTH in features
        )
        is_autoencoder_distance = PredictionField.OUTPUT_DISTANCE in features

        if is_binary_classification:
            p.field(
                PredictionField.OUTPUT_BINARY.value,
                features[PredictionField.OUTPUT_BINARY],
            )
            p.field(
                PredictionField.GROUND_TRUTH.value,
                features[PredictionField.GROUND_TRUTH],
            )
        elif is_autoencoder_distance:
            p.field(
                PredictionField.OUTPUT_DISTANCE.value,
                sum(abs(features[PredictionField.OUTPUT_DISTANCE])),
            )
        else:
            raise NotImplementedError(
                "Either binary output and ground truth, or "
                "output distance field must be set by the model!"
            )

        # Save packet timestamp as a field -- InfluxDB timestamp will be creation time.
        p.field("packet_timestamp", features[PacketFeature.TIMESTAMP])

        # TODO Decide on relevant tags, or leave them configurable.
        # p.time(features[PacketFeature.TIMESTAMP].isoformat(timespec="nanoseconds"))
        # p.tag(PacketFeature.IP_SOURCE_ADDRESS.value, features[PacketFeature.IP_SOURCE_ADDRESS])
        # p.tag(PacketFeature.IP_SOURCE_PORT.value, features[PacketFeature.IP_SOURCE_PORT])
        # p.tag(PacketFeature.IP_DESTINATION_ADDRESS.value, features[PacketFeature.IP_DESTINATION_ADDRESS])
        # p.tag(PacketFeature.IP_DESTINATION_PORT.value, features[PacketFeature.IP_DESTINATION_PORT])
        # p.tag(PacketFeature.PROTOCOL.value, features[PacketFeature.PROTOCOL])

        self.write_api.write(bucket=self.bucket, org=self.org, record=p)
        self.sum_processing_time += time.process_time_ns() - start_time_ref
        self.sample_count += 1

    def end_processing(self):
        self.write_api.flush()
        self.write_api.close()

        report_performance(
            type(self).__name__, log, self.sample_count, self.sum_processing_time
        )

    @staticmethod
    def input_signature():
        return [
            PacketFeature.TIMESTAMP,
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
