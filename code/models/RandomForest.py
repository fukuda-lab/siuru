import logging
from typing import Generator, Any, Dict, Tuple
import numpy as np
from joblib import dump, load

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    accuracy_score,
)
from sklearn.model_selection import train_test_split

from common.features import IFeature, PredictionField
from models.IAnomalyDetectionModel import IAnomalyDetectionModel

log = logging.getLogger()


class RandomForestModel(IAnomalyDetectionModel):
    def __init__(
        self,
        model_name,
        use_existing_model=False,
        skip_saving_model=False,
        model_storage_base_path=None,
        model_relative_path=None,
        **kwargs,
    ):
        self.model_instance = None
        super().__init__(
            model_name,
            use_existing_model=use_existing_model,
            skip_saving_model=skip_saving_model,
            model_storage_base_path=model_storage_base_path,
            model_relative_path=model_relative_path,
        )

    def train(
        self,
        data: Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None],
        **kwargs,
    ):
        log.info("Training a random forest classifier.")

        labels = []
        encoded_features = []

        for features, encoding in data:
            labels.append(features[PredictionField.GROUND_TRUTH])
            encoded_features.append(encoding)

        self.model_instance = RandomForestClassifier()
        self.model_instance.fit(encoded_features, labels)

        # TODO Move evaluation functionality into a separate reporter class.
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

        if not self.skip_saving_model:
            dump(self.model_instance, self.store_file)

    def load(self):
        self.model_instance = load(self.store_file)

    def predict_array(self, X):
        return self.model_instance.predict(X)

    def predict(self, features, encoded_data, **kwargs):
        features[PredictionField.MODEL_NAME] = self.model_name
        features[PredictionField.OUTPUT_BINARY] = int(
            self.model_instance.predict(encoded_data)[0]
        )
