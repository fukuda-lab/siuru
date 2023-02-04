from typing import Generator
import numpy as np

from sklearn.ensemble import RandomForestClassifier


def train(features: Generator[np.array, None, None], y, path_to_store: str):
    rfc = RandomForestClassifier()
    rfc.fit(features, y)
