import time
from typing import Any, Dict, Generator, Optional, List, Tuple, Union

import numpy
import numpy as np
from sklearn.neural_network import MLPRegressor
from joblib import dump, load

from common.features import EncodedSampleGenerator, IFeature, PredictionField, SampleGenerator
from common.functions import report_performance
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
        data_prep_time = 0

        single_array_processing = False
        concatenated_data_array = None
        encoded_features = []

        for samples, encoding in data:
            start = time.process_time_ns()
            if isinstance(samples, list):
                if self.filter_label:
                    # TODO filter xarray by GROUND_TRUTH filter.
                    pass
                elif concatenated_data_array is None:
                    concatenated_data_array = encoding
                else:
                    concatenated_data_array = numpy.concatenate(
                        (concatenated_data_array, encoding),
                        axis=0,
                    )
            else:
                single_array_processing = True
                encoded_features.append(encoding[0])
            data_prep_time += time.process_time_ns() - start

        training_start = time.process_time_ns()
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
        training_time = time.process_time_ns() - training_start

        sample_count = len(encoded_features) if encoded_features else len(concatenated_data_array)

        report_performance(type(self).__name__ + "-preparation", log, sample_count,
                           data_prep_time)
        report_performance(type(self).__name__ + "-training", log, sample_count,
                           training_time)

        if not self.skip_saving_model:
            dump(self.model_instance, self.store_file)

    def load(self):
        self.model_instance = load(self.store_file)
        if not self.model_instance:
            log.error(f"Failed to load model from: {self.store_file}")

    def predict(self, data: EncodedSampleGenerator, **kwargs) -> SampleGenerator:
        sum_processing_time = 0
        sum_samples = 0
        for sample, encoded_sample in data:
            start_time_ref = time.process_time_ns()
            prediction = self.model_instance.predict(encoded_sample)

            if isinstance(sample, list):
                # Handle the prediction for multi-sample encoding.
                for i, sample in enumerate(sample):
                    sample[PredictionField.MODEL_NAME] = self.model_name
                    sample[PredictionField.OUTPUT_DISTANCE] = sum(abs(prediction[i]))
                    sum_processing_time += time.process_time_ns() - start_time_ref
                    sum_samples += 1
                    yield sample

            else:
                sample[PredictionField.MODEL_NAME] = self.model_name
                sample[PredictionField.OUTPUT_DISTANCE] = sum(prediction[0])
                sum_processing_time += time.process_time_ns() - start_time_ref
                sum_samples += 1
                yield sample

        report_performance(type(self).__name__ + "-testing", log, sum_samples, sum_processing_time)
