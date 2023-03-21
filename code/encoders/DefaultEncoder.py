from typing import Any, Dict, Union, Generator

import numpy as np

from encoders.IDataEncoder import IDataEncoder
from prediction_output import PredictionField
from common.features import IFeature


class DefaultEncoder(IDataEncoder):
    def encode(
        self,
        data: Generator[
            Dict[IFeature, Any],
            None,
            None,
        ],
    ) -> Generator[np.array, None, None]:
        for sample in data:
            # TODO check if batching and returning multiple features is faster.
            # Reference: RF with single-feature processing managed 181 packets/s.
            yield np.fromiter(sample.values(), dtype=float)
