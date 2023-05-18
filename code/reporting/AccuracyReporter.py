from collections import defaultdict
from typing import Dict, Any, List

from common.features import IFeature, PredictionField
from reporting.IReporter import IReporter


class AccuracyReporter(IReporter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.correct_classifications_per_model = defaultdict(lambda: 0)
        self.false_classifications_per_model = defaultdict(lambda: 0)

    def report(self, features: Dict[IFeature, Any]):
        name = features[PredictionField.MODEL_NAME]
        if (
            features[PredictionField.OUTPUT_BINARY]
            == features[PredictionField.GROUND_TRUTH]
        ):
            self.correct_classifications_per_model[name] += 1
        else:
            self.false_classifications_per_model[name] += 1

    def end_processing(self):
        # y_pred = self.model_instance.predict(X_test)
        #
        # cnf_matrix = confusion_matrix(y_test, y_pred)
        # log.debug(f"\nConfusion matrix:\n\n{cnf_matrix}\n")
        #
        # log.info(f"Accuracy: {accuracy_score(y_test, y_pred)}")
        # log.info(f"Precision: {precision_score(y_test, y_pred, average='macro')}")
        # log.info(f"Recall: {recall_score(y_test, y_pred, average='macro')}")
        # log.info(f"F1 score: {f1_score(y_test, y_pred, average='macro')}")
        #
        # if feature_names:
        #     log.debug("Feature importances:")
        #     for idx, name in enumerate(feature_names):
        #         log.debug(
        #             f"{name : <40} "
        #             f"{self.model_instance.feature_importances_[idx]:6.4f}"
        #         )

        print()
        print("Accuracy report:")
        print("---")
        for model in self.correct_classifications_per_model.keys():
            print(model)
            acc = self.correct_classifications_per_model[model] / (
                self.correct_classifications_per_model[model]
                + self.false_classifications_per_model[model]
            )
            print(f"Correct: {self.correct_classifications_per_model[model]}")
            print(f"False: {self.false_classifications_per_model[model]}")
            print(f"Accuracy: {acc}")
            print("---")
            print()

    @staticmethod
    def input_signature() -> List[IFeature]:
        return [
            PredictionField.MODEL_NAME,
            PredictionField.OUTPUT_BINARY,
            PredictionField.GROUND_TRUTH,
        ]
