from typing import Any, Dict, Union, Generator, Tuple, Optional, List

import numpy as np

from encoders.IDataEncoder import IDataEncoder
from common.features import IFeature, FeatureGenerator


class DefaultEncoder(IDataEncoder):
    def __init__(self, feature_filter: Optional[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.feature_filter = feature_filter

    def encode(
        self, features: FeatureGenerator, **kwargs
    ) -> Generator[Tuple[Dict[IFeature, Any], np.ndarray], None, None]:
        # TODO check if batching and returning multiple features is faster.
        # Reference: RF with single-feature processing managed 181 packets/s.
        for sample in features:
            if self.feature_filter:
                yield sample, np.fromiter(
                    [v for k, v in sample.items() if k.value in self.feature_filter],
                    dtype=float,
                )
            else:
                yield sample, np.fromiter(sample.values(), dtype=float)
