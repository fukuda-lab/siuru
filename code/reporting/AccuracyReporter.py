from typing import Dict, Any, List

from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, \
    recall_score

from common.features import IFeature, PredictionField
from common.pipeline_logger import PipelineLogger
from reporting.IReporter import IReporter


class AccuracyReporter(IReporter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ground_truths = []
        self.predicted_labels = []

    def report(self, features: Dict[IFeature, Any]):
        self.ground_truths.append(features[PredictionField.GROUND_TRUTH])
        self.predicted_labels.append(features[PredictionField.OUTPUT_BINARY])

    def end_processing(self):
        log = PipelineLogger.get_logger()
        labels = sorted(set(self.ground_truths + self.predicted_labels))

        cnf_matrix = confusion_matrix(self.ground_truths, self.predicted_labels, labels=labels)
        log.info(f"\n---\nReport\n"
                 f"\nConfusion matrix:\n\n{cnf_matrix}\n\n"
                 f"Labels: {labels}\n"
                 f"(i-th row, j-th column: samples with true label i and predicted label j)\n\n"
                 f"Accuracy:"
                 f"{accuracy_score(self.ground_truths, self.predicted_labels)}\n"
                 f"Precision:"
                 f"{precision_score(self.ground_truths, self.predicted_labels, average='macro')}\n"
                 f"Recall:"
                 f"{recall_score(self.ground_truths, self.predicted_labels, average='macro')}\n"
                 f"F1 score: "
                 f"{f1_score(self.ground_truths, self.predicted_labels, average='macro')}\n---"
                 )

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
