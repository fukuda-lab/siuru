import influxdb_client
from influxdb_client import Point
from influxdb_client.client.exceptions import InfluxDBError

from prediction_output import Prediction, PredictionField
from common.features import PacketFeature

import pipeline_logger


log = pipeline_logger.PipelineLogger.get_logger()


# TODO Create reporter interface.
class InfluxDBReporter:
    def __init__(self, url, org, token, bucket):
        self.url = url
        self.org = org
        self.token = token
        self.bucket = bucket

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

    def report(self, p: Prediction, measurement_name: str = "anomaly_detection"):
        point = Point(measurement_name)
        point.time(p.fields[PacketFeature.TIMESTAMP].isoformat(timespec="nanoseconds"))
        point.tag(
            PredictionField.MODEL_NAME.value, p.fields[PredictionField.MODEL_NAME.value]
        )
        # TODO Decide on relevant tags, or leave them customizable.
        # point.tag(PacketFeature.IP_SOURCE_ADDRESS.value, p.fields[PacketFeature.IP_SOURCE_ADDRESS])
        # point.tag(PacketFeature.IP_SOURCE_PORT.value, p.fields[PacketFeature.IP_SOURCE_PORT])
        # point.tag(PacketFeature.IP_DESTINATION_ADDRESS.value, p.fields[PacketFeature.IP_DESTINATION_ADDRESS])
        # point.tag(PacketFeature.IP_DESTINATION_PORT.value, p.fields[PacketFeature.IP_DESTINATION_PORT])
        # point.tag(PacketFeature.PROTOCOL.value, p.fields[PacketFeature.PROTOCOL])

        if PredictionField.OUTPUT_BINARY in p.fields:
            point.field(
                PredictionField.OUTPUT_BINARY.value,
                p.fields[PredictionField.OUTPUT_BINARY.value],
            )
        else:
            raise NotImplementedError("TODO: Support other prediction outputs!")

        self.write_api.write(bucket=self.bucket, org=self.org, record=point)
