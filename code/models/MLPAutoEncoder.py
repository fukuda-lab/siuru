from typing import Any, Dict, Generator, Optional, List, Tuple, Union

import numpy
import numpy as np
from sklearn.neural_network import MLPRegressor
from joblib import dump, load

from common.features import EncodedSampleGenerator, IFeature, PredictionField, SampleGenerator
from models.IAnomalyDetectionModel import IAnomalyDetectionModel
from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class MLPAutoEncoderModel(IAnomalyDetectionModel):
    """
    Multi-layer perceptron (MLP) based autoencoder.
    """

    def __init__(
        self,
        filter_label: Optional[int] = None,
        **kwargs,
    ):
        """
        TODO: multi-AE setup where PredictionField.GROUND_TRUTH label of the data
         will be used to split the data into multiple training sets, then training
         multiple AEs to each predict their own class only.

        :param filter_label:
        :param kwargs: Arguments for the superclass constructor.
        """
        self.model_instance = None
        self.filter_label = filter_label
        super().__init__(**kwargs)

    def train(
        self,
        data: Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None],
        **kwargs,
    ):
        log.info("Training an MLP autoencoder.")

        single_array_processing = False
        concatenated_data_array = None
        encoded_features = []

        for features, encoding in data:
            if isinstance(features, list):
                if self.filter_label:
                    # TODO filter xarray by GROUND_TRUTH filter.
                    pass
                elif not concatenated_data_array:
                    concatenated_data_array = encoding
                else:
                    concatenated_data_array = numpy.concatenate(
                        (concatenated_data_array, encoding),
                        axis=0,
                    )
            else:
                single_array_processing = True
                encoded_features.append(encoding[0])

        # TODO make model parameters configurable.
        self.model_instance = MLPRegressor(
            alpha=1e-15,
            hidden_layer_sizes=[
                25,
                50,
                25,
                2,
                25,
                50,
                25,
            ],
            random_state=1,
            max_iter=10000,
        )

        if not single_array_processing:
            self.model_instance.fit(concatenated_data_array, concatenated_data_array)
        else:
            self.model_instance.fit(encoded_features, encoded_features)

        if not self.skip_saving_model:
            dump(self.model_instance, self.store_file)

    def load(self):
        self.model_instance = load(self.store_file)
        if not self.model_instance:
            log.error(f"Failed to load model from: {self.store_file}")

    def predict(self, data: EncodedSampleGenerator, **kwargs) -> SampleGenerator:
        for sample, encoded_sample in data:
            prediction = self.model_instance.predict(encoded_sample)

            if isinstance(sample, list):
                # Handle the prediction for multi-sample encoding.
                for i, sample in enumerate(sample):
                    sample[PredictionField.MODEL_NAME] = self.model_name
                    sample[PredictionField.OUTPUT_DISTANCE] = sum(abs(prediction[i]))
                    yield sample

            else:
                sample[PredictionField.MODEL_NAME] = self.model_name
                sample[PredictionField.OUTPUT_DISTANCE] = sum(prediction[0])
                yield sample
