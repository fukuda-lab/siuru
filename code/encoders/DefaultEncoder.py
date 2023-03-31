import time

from typing import Any, Dict, Union, Generator, Tuple, Optional, List

import numpy as np

from common.functions import report_performance
from encoders.IDataEncoder import IDataEncoder
from common.features import IFeature, FeatureGenerator

from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


class DefaultEncoder(IDataEncoder):
    def __init__(self, feature_filter: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.feature_filter = feature_filter
        log.info(f"Applying feature filter: {self.feature_filter}")

    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None]:
        sum_processing_time = 0
        packet_count = 0

        for sample in features:
            start_time_ref = time.process_time_ns()
            if self.feature_filter:
                encoding = np.fromiter(
                    [v for k, v in sample.items() if k.value in self.feature_filter],
                    dtype=float,
                )
            else:
                encoding = np.fromiter(sample.values(), dtype=float)

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1
            yield sample, encoding

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
