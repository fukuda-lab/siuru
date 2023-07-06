import csv
import time
from typing import List

from common.features import FeatureGenerator, IFeature, PredictionField
from common.functions import report_performance
from common.pipeline_logger import PipelineLogger
from preprocessors import IPreprocessor

log = PipelineLogger.get_logger()


class KitsuneLabelProcessor(IPreprocessor):

    @staticmethod
    def input_signature() -> List[IFeature]:
        return []

    @staticmethod
    def output_signature() -> List[IFeature]:
        return [PredictionField.GROUND_TRUTH]

    def __init__(self, label_file: str):
        self.csv_reader = csv.reader(label_file)

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        # According to Kitsune dataset creators,
        # column 0 is the index, column 1 is the label.

        for f in features:
            start_time_ref = time.process_time_ns()

            f[PredictionField.GROUND_TRUTH] = int(self.csv_reader.__next__())

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1

            yield f

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
