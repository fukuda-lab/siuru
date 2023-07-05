import logging
from typing import Generator, Any, Dict, Tuple

import numpy
import numpy as np
from joblib import dump, load

from sklearn.ensemble import RandomForestClassifier

from common.features import IFeature, PredictionField
from models.IAnomalyDetectionModel import IAnomalyDetectionModel

log = logging.getLogger()


class RandomForestModel(IAnomalyDetectionModel):
    def __init__(
        self,
        model_name,
        train_new_model=True,
        skip_saving_model=False,
        model_storage_base_path=None,
        model_relative_path=None,
        **kwargs,
    ):
        self.model_instance = None
        super().__init__(
            model_name,
            train_new_model=train_new_model,
            skip_saving_model=skip_saving_model,
            model_storage_base_path=model_storage_base_path,
            model_relative_path=model_relative_path,
            **kwargs,
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
            if isinstance(features, list):
                # Handle the list with multiple features used together with
                # xarray DataArray encodings.
                for f in features:
                    labels.append(f[PredictionField.GROUND_TRUTH])
                if not encoded_features:
                    encoded_features = encoding
                else:
                    encoded_features = numpy.concatenate(
                        (encoded_features, encoding), axis=0
                    )
            else:
                labels.append(features[PredictionField.GROUND_TRUTH])
                encoded_features.append(encoding[0])

        self.model_instance = RandomForestClassifier()
        self.model_instance.fit(encoded_features, labels)

        if not self.skip_saving_model:
            dump(self.model_instance, self.store_file)

    def load(self):
        self.model_instance = load(self.store_file)

    def predict(self, features, encoded_data, **kwargs):
        # Requirements for encoded data:
        #
        # X : {array-like, sparse matrix} of shape (n_samples, n_features)
        #     The input samples. Internally, its dtype will be converted to
        #     ``dtype=np.float32``. If a sparse matrix is provided, it will be
        #     converted into a sparse ``csr_matrix``.
        #
        # Source: https://github.com/scikit-learn/scikit-learn/blob/72a604975102b2d93082385d7a5a7033886cc825/sklearn/ensemble/_forest.py

        prediction = self.model_instance.predict(encoded_data)
        if isinstance(features, list):
            for i, sample in enumerate(features):
                sample[PredictionField.MODEL_NAME] = self.model_name
                sample[PredictionField.OUTPUT_BINARY] = prediction[i]
                yield sample
        else:
            features[PredictionField.MODEL_NAME] = self.model_name
            features[PredictionField.OUTPUT_BINARY] = prediction[0]
            yield features
