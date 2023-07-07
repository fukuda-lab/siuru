# Tutorial: Extending the SIURU pipeline with custom components

SIURU pipelines consist of five categories:
1. dataloaders
2. preprocessors
3. encoders
4. models
5. reporters

Each of these components have a generic interface that defines the flow of data between pipeline building blocks. By writing components that adhere to the interfaces, you can later build custom pipelines just by specifying the components in a configuration file. Custom keyword arguments can be supplied to the components over the configuration files, as well.

## Adding a dataloader

As can be seen in `IDataLoader.py`, where the interface of the data loading components is specified, a data loader should define two functions:

```python
class IDataLoader(ABC):
    """
    Generic interface for data loading modules to implement.
    """

    def __init__(self, **kwargs):
        pass

    @staticmethod
    @abstractmethod
    def feature_signature() -> List[IFeature]:
        return []

    @abstractmethod
    def get_features(self) -> FeatureGenerator:
        """
        Yields a dictionary of preprocessed features per sample.
        """
        yield {}
```

The feature signature is a list of feature specifiers from the `common/features.py` feature collection file. The signature accessible under `feature_signature()` declares the features which will be available in the `FeatureGenerator` object returned by `get_features()`. In the future, the signatures of various components can be used to validate that the features required by one component will be made accessible by a preceding component, allowing to check that the SIURU pipeline is valid before executing it.



TODO: add a data loader example, e.g. for NetFlow datasets.


## Adding a feature preprocessor

Let's go through the steps for creating a custom preprocessing component. We will implement a simple preprocessor that can read the labels for a Kitsune dataset from the .csv format and add these to the features parsed from raw packets.

The feature preprocessor interface is as follows:

```python
class IPreprocessor(ABC):
    @staticmethod
    @abstractmethod
    def input_signature() -> List[IFeature]:
        pass

    @staticmethod
    @abstractmethod
    def output_signature() -> List[IFeature]:
        pass

    @abstractmethod
    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        pass
```

The input and output signature functions are similar to the `feature_signature()` function of data loaders, but since data passes through preprocessors, separate signatures are needed for the input and output feature sets. The input signature is essentially a list of feature requirements set by the preprocessor, while the output signature acts as a promise to provide certain features to downstream components.

First, create a new template class `KitsuneLabelProcessor.py` and add the class to `code/preprocessors/__init__.py`. The last step is required for the reflection-based pipeline builder to find the class based on its name.

Then, specify the initialization steps. The preprocessor must know from which file the labels should be loaded, so we add a keyword argument:

```python
class KitsuneLabelProcessor(IPreprocessor):
    def __init__(self, label_file: str):
        self.csv_reader = csv.reader(label_file)
```

The labeler does not depend on any preexisting features, so we can leave the input signature empty. The output signature defines a new prediction field, the ground truth:
```python
    @staticmethod
    def input_signature() -> List[IFeature]:
        return []

    @staticmethod
    def output_signature() -> List[IFeature]:
        return [PredictionField.GROUND_TRUTH]
```

To define the processing function, we iterate over the input feature generator and augment each element with the label provided from the file:

```python
    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        # According to Kitsune dataset creators,
        # column 0 is the index, column 1 is the label.

        for f in features:
            f[PredictionField.GROUND_TRUTH] = int(self.csv_reader.__next__())
            yield f
```

Although it might seem like an overkill for such a simple preprocessor, logging and profiling options should be added to every more complicated preprocessor to quickly debug or detect pipeline malfunctions. The full code could look as follows:


```python
import csv
import time
from typing import List

from common.features import FeatureGenerator, IFeature, PredictionField
from common.functions import report_performance
from common.pipeline_logger import PipelineLogger
from preprocessors import IPreprocessor

log = PipelineLogger.get_logger()


class KitsuneLabelProcessor(IPreprocessor):

    @staticmethod
    def input_signature() -> List[IFeature]:
        return []

    @staticmethod
    def output_signature() -> List[IFeature]:
        return [PredictionField.GROUND_TRUTH]

    def __init__(self, label_file: str):
        self.csv_reader = csv.reader(label_file)

    def process(self, features: FeatureGenerator) -> FeatureGenerator:
        sum_processing_time = 0
        packet_count = 0

        # According to Kitsune dataset creators,
        # column 0 is the index, column 1 is the label.

        for f in features:
            start_time_ref = time.process_time_ns()

            f[PredictionField.GROUND_TRUTH] = int(self.csv_reader.__next__())

            sum_processing_time += time.process_time_ns() - start_time_ref
            packet_count += 1

            yield f

        report_performance(type(self).__name__, log, packet_count, sum_processing_time)
```