import time

from typing import Any, Dict, Generator, Tuple, Optional, List

import numpy
import numpy as np
import xarray

from common.functions import report_performance
from encoders.IDataEncoder import IDataEncoder
from common.features import IFeature, FeatureGenerator, resolve_feature

from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class MultiSampleEncoder(IDataEncoder):
    def __init__(
        self,
        feature_filter: Optional[List[str]] = None,
        max_array_size: int = 0,
        max_time_window_ms: int = 0,
        **kwargs,
    ):
        """
        Encode data into xarray.DataArrays with features in the feature_filter as
        first dimension and samples in the second dimension. Without time or array size
        limit, all features will be encoded in the same DataArray.

        :param feature_filter: Feature names to include in the order as the
            features should appear in the DataArray. If empty, all input features
            of the first sample will be included.
        :param max_array_size: Maximal number of samples to include in each yielded
           array, if max_time_window_ms is not reached before.
        :param max_time_window_ms: Maximal time to wait before yielding an array,
            if the max_array_size is not reached before.
        """
        super().__init__(**kwargs)
        self.feature_filter = [resolve_feature(f) for f in feature_filter]
        log.info(f"Applying feature filter: {self.feature_filter}")
        self.max_array_size = max_array_size
        self.max_time_window_ns = max_time_window_ms * 10**6

    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None]:
        """
        Encode input features into xarray.DataArrays. Features in feature_filter become
        the first dimension and samples the second dimension of the DataArray.

        :param features: Generator of feature dictionaries to be encoded.
        :return: Yields tuples with:
            (1) list of input feature dictionaries used to generate the encoding,
            (2) xarray.DataArray of the encoded samples.
        """
        packet_count = 0
        sum_processing_time = 0

        first = True
        feature_dicts = []
        encoding_array = None
        last_published_time = time.process_time_ns()

        for sample in features:
            start_time = time.process_time_ns()

            # Feature dictionaries will be stored in a single list element.
            feature_dicts.append(sample)

            # xarray is built by appending each feature's encoding one by one.
            if first:
                if not self.feature_filter:
                    # All encoded samples will follow the first sample's feature scheme!
                    self.feature_filter = list(sample.keys())

                encoding_array = xarray.DataArray(
                    [
                        [sample[f] for f in self.feature_filter],
                    ],
                    dims=["samples", "features"],
                    coords={"features": self.feature_filter},
                )
                # encoding_array.reshape((1, len(self.feature_filter)))
                first = False

            else:
                encoding_array = numpy.concatenate(
                    (
                        encoding_array,
                        [
                            [sample[f] for f in self.feature_filter],
                        ],
                    ),
                    axis=0,
                )

            current_time = time.process_time_ns()
            sum_processing_time += current_time - start_time
            packet_count += 1

            if (
                self.max_time_window_ns != 0
                and current_time - last_published_time >= self.max_time_window_ns
            ) or (
                self.max_array_size != 0 and len(feature_dicts) >= self.max_array_size
            ):
                yield feature_dicts, encoding_array

        # When the samples run out, still publish the last array!
        yield feature_dicts, encoding_array

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
