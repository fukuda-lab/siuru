import time

from typing import Any, Dict, Generator, Tuple, Optional, List

import numpy as np

from common.functions import report_performance
from encoders.IDataEncoder import IDataEncoder
from common.features import IFeature, FeatureGenerator, resolve_feature

from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class DefaultEncoder(IDataEncoder):
    """
    :param feature_filter: Feature names to include in the order as the
        features should appear in the DataArray. If empty, all input features
        of the first sample will be included.

    Based on the feature_filter passed at initialization, the encoder creates a
    (1, n)-dimensional Numpy arrays from input samples, with the features ordered
    according to their order in the filter.

    The DefaultEncoder can be initialized without a feature filter. In this case, all
    features of the first received sample are used in their order of occurrence as the
    filter for all subsequent samples.
    """
    def __init__(self, feature_filter: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.feature_filter = None
        if feature_filter:
            self.feature_filter = [resolve_feature(f) for f in feature_filter]
        log.info(f"Applied feature filter: {self.feature_filter}")

    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None]:
        """
        :return: (1, n)-dimensional Numpy array, with n being the number of features in
         the feature_filter (or in the first sample, if no filter was provided).
        """
        sum_processing_time = 0
        packet_count = 0

        for sample in features:
            start_time_ref = time.process_time_ns()

            if not self.feature_filter:
                # All encoded samples will follow the first sample's feature scheme!
                self.feature_filter = list(sample.keys())
                log.info(f"Applied feature filter: {self.feature_filter}")

            encoding = np.fromiter(
                [sample[f] for f in self.feature_filter],
                dtype=np.float32,
            ).reshape(1, -1)

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1

            yield sample, encoding

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
