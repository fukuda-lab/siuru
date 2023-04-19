from typing import Generator, Any, Optional, List

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split

from models.IAnomalyDetectionModel import IAnomalyDetectionModel
from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class MLPAutoEncoderModel(IAnomalyDetectionModel):
    """
    Multi-layer perceptron (MLP) based autoencoder.
    """

    def __init__(
        self,
        model_name,
        train_new_model=True,
        skip_saving_model=False,
        model_storage_base_path=None,
        model_relative_path=None,
        **kwargs,
    ):

        super().__init__(
            model_name,
            train_new_model,
            skip_saving_model,
            model_storage_base_path,
            model_relative_path,
            **kwargs,
        )
        self.model_instance = None


    # TODO Doesn't work - update to use the new interface!
    def train(
        self,
        true_features: Generator[np.array, None, None],
        false_features: Generator[np.array, None, None],
        feature_names: Optional[List[str]] = None,
        **kwargs,
    ):
        log.info("Training an MLP autoencoder.")
        # TODO Find ways to work with the generators to save memory.
        true_feat_list = list(true_features)
        false_feat_list = list(false_features)
        log.info(f"Number of true (target) samples: {len(true_feat_list)}")
        log.info(
            f"Number of false (anomalous) samples for testing: {len(false_feat_list)}"
        )

        X_train, X_test = train_test_split(
            true_feat_list, test_size=0.1, random_state=8
        )
        ae = MLPRegressor(
            alpha=1e-15,
            hidden_layer_sizes=[25, 50, 25, 2, 25, 50,# p.time(features[PacketFeature.TIMESTAMP].isoformat(timespec="nanoseconds"))
         25],
            random_state=1,
            max_iter=10000,
        )
        ae.fit(X_train, X_train)
        true_vs_pred = map(lambda x, y: abs(x - y), X_test, ae.predict(X_test))
        log.info(f"True feature avg diff: {sum(sum(true_vs_pred)) / len(X_test)}")
        false_vs_pred = map(
            lambda x, y: abs(x - y), false_feat_list, ae.predict(false_feat_list)
        )
        log.info(
            f"False feature avg diff: {sum(sum(false_vs_pred)) / len(false_feat_list)}"
        )
