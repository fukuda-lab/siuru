import logging
from typing import Generator
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

log = logging.getLogger()

def train(features: Generator[np.array, None, None], y, path_to_store: str = None):
    log.info("Training a random forest classifier.")
    X_train, X_test, y_train, y_test = train_test_split(
        list(features), y, test_size=0.2, random_state=8)
    rfc = RandomForestClassifier()
    rfc.fit(X_train, y_train)

    accuracy = rfc.score(X_test, y_test)
    log.info(f"Accuracy: {accuracy}")
