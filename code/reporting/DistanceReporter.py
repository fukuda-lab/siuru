from collections import defaultdict
from typing import Dict, Any, List

from common.features import IFeature, PredictionField
from common.pipeline_logger import PipelineLogger
from reporting.IReporter import IReporter


class DistanceReporter(IReporter):
    """
    Tracks the distance stored under PredictionField.OUTPUT_DISTANCE
    by an unsupervised model such as an AutoEncoder.

    Can only be used when PredictionField.GROUND_TRUTH is known!
    Distances are split into groups by the labels, allowing comparisons
    of the average encoding deviation between different classes.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.distance_sum_per_model_and_label = defaultdict(lambda: 0)
        self.samples_per_model_and_label = defaultdict(lambda: 0)

    def report(self, features: Dict[IFeature, Any]):
        key = (features[PredictionField.MODEL_NAME], features[PredictionField.GROUND_TRUTH])
        self.distance_sum_per_model_and_label[key] += \
            features[PredictionField.OUTPUT_DISTANCE]
        self.samples_per_model_and_label[key] += 1

    def end_processing(self):
        log = PipelineLogger.get_logger()
        report = "\n---\nDistance report\n"
        for key, distance_sum in self.distance_sum_per_model_and_label.items():
            model, label = key
            avg = self.distance_sum_per_model_and_label[key] / self.samples_per_model_and_label[key]
            report += \
                f"Model: {model}\n" \
                f"Label: {label}\n" \
                f"Total samples: {self.samples_per_model_and_label[key]}\n" \
                f"Average distance: {avg:.5E}\n\n"
        log.info(report)

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
