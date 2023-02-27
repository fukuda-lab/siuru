import logging
import os.path
from typing import Generator, Any, Optional, List, Dict
import numpy as np
from joblib import dump, load

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

from prediction_output import Prediction, PredictionField

log = logging.getLogger()


def train(features: Generator[np.array, None, None],
          y: Generator[Any, None, None],
          path_to_store: str = None,
          feature_names: Optional[List[str]] = None):

    log.info("Training a random forest classifier.")
    X_train, X_test, y_train, y_test = train_test_split(
        list(features), list(y), test_size=0.33, random_state=8)
    rfc = RandomForestClassifier()
    rfc.fit(X_train, y_train)

    y_pred = rfc.predict(X_test)

    cnf_matrix = confusion_matrix(y_test, y_pred)
    log.debug(f"\nConfusion matrix:\n\n{cnf_matrix}\n")

    log.info(f"Accuracy: {accuracy_score(y_test, y_pred)}")
    log.info(f"Precision: {precision_score(y_test, y_pred, average='macro')}")
    log.info(f"Recall: {recall_score(y_test, y_pred, average='macro')}")
    log.info(f"F1 score: {f1_score(y_test, y_pred, average='macro')}")

    if feature_names:
        log.debug("Feature importances:")
        for idx, name in enumerate(feature_names):
            log.debug(f"{name : <40} {rfc.feature_importances_[idx]:6.4f}")

    if path_to_store:
        dump(rfc, path_to_store)


class RF:
    def __init__(self, path_to_model: str):
        self.model = load(path_to_model)
        self.name = os.path.splitext(os.path.basename(path_to_model))[0]

    def predict_array(self, X):
        return self.model.predict(X)

    def predict_packet(self, x):
        return self.model.predict(x)
