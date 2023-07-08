import argparse
import itertools
import json
import os
import time
from typing import List

from jinja2 import Template

from common.functions import report_performance, time_now, project_root, git_tag
from dataloaders import *
from models import *
from preprocessors import *
from encoders import *
from reporting import *

from common.pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


def main(args_config_path, args_influx_token):
    """
    Run the IoT anomaly detection pipeline based on a configuration file.
    """

    pipeline_execution_start = time.process_time_ns()
    log_time_tag = time_now()

    # Load configuration file that specifies pipeline components.
    config_path = os.path.abspath(args_config_path)
    assert os.path.exists(config_path), "Config file not found!"
    log.debug(f"Loading configuration from: {config_path}")
    with open(config_path) as config_file:
        if ".jinja" in config_path:
            # New functions for templating can be registered here.
            template = Template(config_file.read())
            template.globals["timestamp"] = log_time_tag
            template.globals["project_root"] = project_root()
            template.globals["git_tag"] = git_tag()
            template.globals["influx_token"] = args_influx_token
            configuration = json.loads(template.render())
        else:
            configuration = json.loads(config_path)
    if not configuration:
        log.error("Could not load configuration file!")
        exit(1)
    log.debug("Configuration loaded!")

    class_initialization_start = time.process_time_ns()

    # Initialize file loggers.
    if "LOG" in configuration:
        for log_config in configuration["LOG"]:
            log_level = log_config.get("level", "DEBUG")
            # Default location is under the /logs directory in this repository.
            log_path = log_config.get(
                "path",
                os.path.join(
                    project_root(), "logs", "other", f"{log_time_tag}-log.txt"
                ),
            )
            if not os.path.exists(os.path.dirname(log_path)):
                os.makedirs(os.path.dirname(log_path))
            PipelineLogger.add_file_logger(log_level, log_path)

    # Feature stream is a Python generator object: https://wiki.python.org/moin/Generators
    # It allows to process the samples memory-efficiently, avoiding the need to store all data in memory at the same time.
    feature_stream = itertools.chain([])

    # Initialize data loaders classes corresponding to each component under DATA_SOURCES in configuration.
    for data_source in configuration["DATA_SOURCES"]:
        loader_name = data_source["loader"]["class"]
        loader_class = globals()[loader_name]
        log.info(f"Adding {loader_class.__name__} to pipeline.")
        loader: IDataLoader = loader_class(**data_source["loader"]["kwargs"])
        new_feature_stream = loader.get_features()

        # Initialize preprocessors specific to the data sources. Allowing each data source to specify its own preprocessor means data from different storage formats and with different processing needs can be combined to train models or perform prediction.
        for preprocessor_specification in data_source["preprocessors"]:
            preprocessor_name = preprocessor_specification["class"]
            preprocessor_class = globals()[preprocessor_name]
            log.info(f"Adding {preprocessor_class.__name__} to pipeline.")
            preprocessor: IPreprocessor = preprocessor_class(
                **preprocessor_specification["kwargs"]
            )
            new_feature_stream = preprocessor.process(new_feature_stream)

        feature_stream = itertools.chain(feature_stream, new_feature_stream)

    # If no model is specified, count the number of samples in the loaded data.
    # Just a convenience function, might be removed later.
    if len(configuration["MODEL"]) == 0:
        log.info("No model specified - counting input data points:")
        count = 0
        for _ in feature_stream:
            count += 1
        log.info(f"{count} elements.")
        exit(0)

    # Initialize model class based on the component specification in the configuration.
    model_specification = configuration["MODEL"]
    model_name = model_specification["class"]
    model_class = globals()[model_name]
    model_instance: IAnomalyDetectionModel = model_class(
        full_config_json=json.dumps(configuration, indent=4), **model_specification
    )

    # Initialize encoder class for the model. Encoders are model-specific to allow running multiple models simultaneously in the future, where each may require their own encoder instance.
    encoder_name = model_specification["encoder"]["class"]
    encoder_class = globals()[encoder_name]
    encoder_instance: IDataEncoder = encoder_class(
        **model_specification["encoder"]["kwargs"]
    )
    log.info("Encoding features.")

    # This moment is important for performance measurement because encoding is the first step
    # where features are actually processed. Until here, the generator data has not been consumed, so no data processing needed to take place).
    encoding_start = time.process_time_ns()

    encoded_feature_generator = encoder_instance.encode(feature_stream)

    # Sanity check - peek at the first sample, print its fields and encoded format.
    peeker, encoded_feature_generator = itertools.tee(encoded_feature_generator)
    first_sample = next(peeker)
    if not first_sample:
        log.warning("No data in encoded feature stream!")
    elif len(first_sample) == 2:  # Assure sample matches the intended signature.
        log.debug("Features of the first sample:")
        first_sample_data, _ = first_sample
        if isinstance(first_sample_data, list):
            # Extract first sample from list as encoded by MultiSampleEncoder. Otherwise, the first_sample_data object is already a dict containing the features of a single sample.
            first_sample_data = first_sample_data[0]
        for k, v in first_sample_data.items():
            log.debug(f" | {k}: {v}")

    if model_specification["train_new_model"]:
        # Train the model.
        start = time.process_time_ns()
        model_instance.train(
            encoded_feature_generator, path_to_store=model_instance.store_file
        )
        end = time.process_time_ns()
        sample_count = 0  # Not supported during training yet.
        report_performance("Training", log, sample_count, end - start)

    else:
        # Prediction time!
        reporter_instances: List[IReporter] = []

        for output in configuration["OUTPUT"]:
            reporter_name = output["class"]
            reporter_class = globals()[reporter_name]
            reporter_instance = reporter_class(**output["kwargs"])
            reporter_instances.append(reporter_instance)

        sample_count = 0
        start = time.process_time_ns()

        for sample, encoding in encoded_feature_generator:
            for predicted_sample in model_instance.predict(sample, encoding):
                for reporter_instance in reporter_instances:
                    reporter_instance.report(predicted_sample)
                sample_count += 1
            if sample_count % 1000 == 0:
                log.debug(f"    Processed samples so far: {sample_count}")
        end = time.process_time_ns()
        report_performance("Predict + report", log, sample_count, end - start)

        # Reporters may require special shutdown steps, for example disconnecting from remote database or printing summaries of the processing -- call the handle for each reporter.
        for reporter_instance in reporter_instances:
            reporter_instance.end_processing()

    pipeline_stopping_time = time.process_time_ns()

    report_performance(
        "IoT-AD full pipeline",
        log,
        sample_count,
        time.process_time_ns() - pipeline_execution_start,
    )
    report_performance(
        "IoT-AD from initialization",
        log,
        sample_count,
        time.process_time_ns() - class_initialization_start,
    )
    report_performance(
        "IoT-AD from encoding",
        log,
        sample_count,
        time.process_time_ns() - encoding_start,
    )


if __name__ == "__main__":

    # Argument parser initialization.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-path", type=str, required=True)
    parser.add_argument("--influx-token", type=str, required=False, default="")
    log.debug("Parsing arguments.")
    args = parser.parse_args()

    main(args.config_path, args.influx_token)
