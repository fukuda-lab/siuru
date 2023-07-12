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

    def __init__(self, feature_list=None, **kwargs):
        """
        Initialize the distance reporter. If feature_list is set,
        the distance is stored and reporter per feature.

        :param feature_list: List of feature type strings, analogous to
            encoders. Must be in the same order as the features in the
            sample encoder of the pipeline!
        """
        super().__init__(**kwargs)
        self.feature_list = feature_list
        self.distance_sum_per_model_label_feature = defaultdict(lambda: 0)
        self.samples_per_model_and_label = defaultdict(lambda: 0)

    def report(self, features: Dict[IFeature, Any]):
        if self.feature_list:
            # Sum distance results by model, label and feature.
            for i, f in enumerate(features[PredictionField.OUTPUT_DISTANCE]):
                key = (
                    features[PredictionField.MODEL_NAME],
                    features[PredictionField.GROUND_TRUTH],
                    self.feature_list[i]
                )
                self.distance_sum_per_model_label_feature[key] += abs(f)

            sample_count_key = (
                    features[PredictionField.MODEL_NAME],
                    features[PredictionField.GROUND_TRUTH]
            )
            self.samples_per_model_and_label[sample_count_key] += 1
        else:
            # Sum distance results only by model and label.
            key = (
                features[PredictionField.MODEL_NAME],
                features[PredictionField.GROUND_TRUTH],
                None
            )
            self.distance_sum_per_model_label_feature[key] += \
                sum(abs(features[PredictionField.OUTPUT_DISTANCE]))
            self.samples_per_model_and_label[key] += 1

    def end_processing(self):
        log = PipelineLogger.get_logger()
        report = "\n---\nDistance report\n"
        reported_keys = []
        for key, distance_sum in self.distance_sum_per_model_label_feature.items():
            model, label, feature_name = key
            sample_count = self.samples_per_model_and_label[(model, label)]
            # Python dictionaries are ordered by insertion, so we can output the model
            # and label info during iteration and expect the immediately following
            # entries to all be related to the same model-label pair, until none left.
            if (model, label) not in reported_keys:
                report += (
                    f"Model: {model}\n"
                    f"Label: {label}\n"
                    f"Total samples: {sample_count}\n\n")
                reported_keys.append((model, label))
            avg = (
                self.distance_sum_per_model_label_feature[key] / sample_count
            )
            if feature_name:
                report += (
                    f"Feature: {feature_name}\n"
                    f"AvgDistance: {round(avg, 2)}\n\n"
                )
            else:
                report += f"AvgDistance: {round(avg, 2)}\n\n"

        log.info(report)

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
