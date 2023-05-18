import time

from typing import Any, Dict, Union, Generator, Tuple, Optional, List

import numpy
import numpy as np
import xarray

from common.functions import report_performance
from encoders.IDataEncoder import IDataEncoder
from common.features import IFeature, FeatureGenerator

from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class MultiSampleEncoder(IDataEncoder):
    def __init__(
        self,
        feature_filter: Optional[List[str]] = None,
        max_array_size: int = 1000,
        max_time_window_ms: int = 1000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.feature_filter = feature_filter
        log.info(f"Applying feature filter: {self.feature_filter}")
        self.max_array_size = max_array_size
        self.max_time_window_ms = max_time_window_ms

    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None]:
        packet_count = 0
        sum_processing_time = 0

        first = True
        # TODO reflect in signature that the sample data is just packed into a list.
        multi_sample_data = []
        multi_sample_encoding_array = None

        for sample in features:
            start_time_ref = time.process_time_ns()

            # Feature dictionaries will be stored in a single list element.
            multi_sample_data.append(sample)

            # xarray is built by appending each feature's encoding one by one.
            if first:
                first = False
                if not self.feature_filter:
                    # All encoded features follow the first sample's scheme!
                    self.feature_filter = list(sample.keys())

                multi_sample_encoding_array = xarray.DataArray(
                    [
                        [sample[f] for f in self.feature_filter],
                    ],
                    dims=["samples", "features"],
                    coords={"features": self.feature_filter},
                )
                # multi_sample_encoding_array.reshape((1, len(self.feature_filter)))
            else:
                multi_sample_encoding_array = numpy.concatenate(
                    (
                        multi_sample_encoding_array,
                        [
                            [sample[f] for f in self.feature_filter],
                        ],
                    ),
                    axis=0,
                )

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1
            # TODO publish array when max time window has elapsed.

        yield multi_sample_data, multi_sample_encoding_array

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
