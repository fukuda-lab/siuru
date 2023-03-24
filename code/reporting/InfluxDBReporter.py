from typing import Dict, Any, Optional

import influxdb_client
from influxdb_client import Point
from influxdb_client.client.exceptions import InfluxDBError

from common.features import PacketFeature, IFeature, PredictionField

import pipeline_logger
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
        # TODO optimize batch reporting (the default).
        # 2023-03-02 Performance with synchronous reporting: 87 packets/s.
        # 2023-03-02 Performance with default batch reporting: 168 packets/s.
        self.write_api = self.client.write_api(
            success_callback=self.success,
            error_callback=self.error,
            retry_callback=self.retry,
        )
        self.logger.info(
            f"Initialized InfluxDB writer to {self.url} " f"[{self.org}/{self.bucket}]."
        )

    def success(self, conf: (str, str, str), data: str):
        pass

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.error(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.info(
            f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}"
        )

    def report(self, features: Dict[IFeature, Any]):
        p = Point(self.measurement_name)
        p.time(features[PacketFeature.TIMESTAMP].isoformat(timespec="nanoseconds"))
        p.tag(PredictionField.MODEL_NAME.value, features[PredictionField.MODEL_NAME])
        p.field(
            PredictionField.OUTPUT_BINARY.value, features[PredictionField.OUTPUT_BINARY]
        )
        p.field(
            PredictionField.GROUND_TRUTH.value, features[PredictionField.GROUND_TRUTH]
        )

        # TODO Decide on relevant tags, or leave them customizable.
        # p.tag(PacketFeature.IP_SOURCE_ADDRESS.value, features[PacketFeature.IP_SOURCE_ADDRESS])
        # p.tag(PacketFeature.IP_SOURCE_PORT.value, features[PacketFeature.IP_SOURCE_PORT])
        # p.tag(PacketFeature.IP_DESTINATION_ADDRESS.value, features[PacketFeature.IP_DESTINATION_ADDRESS])
        # p.tag(PacketFeature.IP_DESTINATION_PORT.value, features[PacketFeature.IP_DESTINATION_PORT])
        # p.tag(PacketFeature.PROTOCOL.value, features[PacketFeature.PROTOCOL])

        self.write_api.write(bucket=self.bucket, org=self.org, record=p)

    @staticmethod
    def input_signature():
        return [
            PacketFeature.TIMESTAMP,
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
