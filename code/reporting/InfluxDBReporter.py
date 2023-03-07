import influxdb_client
from influxdb_client import Point
from influxdb_client.client.exceptions import InfluxDBError

from prediction_output import Prediction, PredictionField
from preprocessors.common import PacketFeature

import pipeline_logger

stop = 100000

# TODO Create reporter interface.
class InfluxDBReporter:
    def __init__(self, url, org, token, bucket):
        # TODO Do not hardcode the bucket or the token...
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
        self.write_api = self.client.write_api(success_callback=self.success,
                                               error_callback=self.error,
                                               retry_callback=self.retry
                                               )
        self.logger.info(f"Initialized InfluxDB writer to {self.url} "
                 f"[{self.org}/{self.bucket}].")

    def success(self, conf: (str, str, str), data: str):
        pass

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.error(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        self.logger.info(f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}")

    def report(self, p: Prediction, measurement_name: str = "anomaly_detection"):
        global stop

        t = p.fields[PacketFeature.TIMESTAMP].isoformat()
        for k, v in p.fields.items():
            if k == PacketFeature.TIMESTAMP or \
                    k == PacketFeature.IP_SOURCE_ADDRESS or \
                    k == PacketFeature.IP_SOURCE_PORT or \
                    k == PacketFeature.IP_DESTINATION_ADDRESS or \
                    k == PacketFeature.IP_DESTINATION_PORT or \
                    k == PacketFeature.PROTOCOL:
                continue

            point = Point(f"{measurement_name}.{k.value}")
            point.time(t)
            point.field(k.value, v)
            point.tag(PacketFeature.IP_SOURCE_ADDRESS.value, p.fields[PacketFeature.IP_SOURCE_ADDRESS])
            point.tag(PacketFeature.IP_SOURCE_PORT.value, p.fields[PacketFeature.IP_SOURCE_PORT])
            point.tag(PacketFeature.IP_DESTINATION_ADDRESS.value, p.fields[PacketFeature.IP_DESTINATION_ADDRESS])
            point.tag(PacketFeature.IP_DESTINATION_PORT.value, p.fields[PacketFeature.IP_DESTINATION_PORT])
            point.tag(PacketFeature.PROTOCOL.value, p.fields[PacketFeature.PROTOCOL])

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            stop -= 1
            if stop <= 0:
                print("Stopped after 100000 data points.")
                exit(0)
