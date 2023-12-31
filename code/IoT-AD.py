import argparse
import itertools
import json
import os
import time
from typing import List

from jinja2 import Template

import common.global_variables as global_variables
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
    config_file_name = os.path.basename(config_path).split('.')[0]
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
            template.globals["config_file_name"] = config_file_name
            configuration = json.loads(template.render())
        else:
            configuration = json.loads(config_path)
    if not configuration:
        log.error("Could not load configuration file!")
        exit(1)

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

    # Re-logging the path because file-based logger was not initialized before.
    log.debug(f"Running configuration: {config_path}")

    # Feature stream is a Python generator object: https://wiki.python.org/moin/Generators
    # It allows to process the samples memory-efficiently, avoiding the need to store all data in memory at the same time.
    feature_stream = itertools.chain([])

    # Initialize data loaders classes corresponding to each component under DATA_SOURCES in configuration.
    for data_source in configuration["DATA_SOURCES"]:
        loader_name = data_source["loader"]["class"]
        loader_class = globals()[loader_name]
        log.info(f"Adding {loader_class.__name__} to pipeline.")
        loader: IDataLoader = loader_class(**data_source["loader"]["kwargs"])
        new_feature_stream = loader.get_samples()

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
        model_instance.train(
            encoded_feature_generator, path_to_store=model_instance.store_file
        )

    else:
        # Prediction time!
        reporter_instances: List[IReporter] = []

        for output in configuration["OUTPUT"]:
            reporter_name = output["class"]
            reporter_class = globals()[reporter_name]
            reporter_instance = reporter_class(**output["kwargs"])
            reporter_instances.append(reporter_instance)

        for predicted_sample in model_instance.predict(encoded_feature_generator):
            for reporter_instance in reporter_instances:
                reporter_instance.report(predicted_sample)

        # Reporters may require special shutdown steps, for example disconnecting from
        # remote database or printing summaries of the processing -- call the handle for
        # each reporter.
        for reporter_instance in reporter_instances:
            reporter_instance.end_processing()

    pipeline_stopping_time = time.process_time_ns()
    full_pipeline_time = pipeline_stopping_time - pipeline_execution_start
    time_from_initialization = pipeline_stopping_time - class_initialization_start
    time_from_processing = pipeline_stopping_time - encoding_start

    report_performance(
        "FullPipeline",
        log,
        global_variables.global_pipeline_packet_count,
        full_pipeline_time,
    )
    report_performance(
        "FromInitializationStart",
        log,
        global_variables.global_pipeline_packet_count,
        time_from_initialization,
    )
    report_performance(
        "FromProcessingStart",
        log,
        global_variables.global_pipeline_packet_count,
        time_from_processing,
    )

    # See Table 1 at:
    # https://sec.cloudapps.cisco.com/security/center/resources/network_performance_metrics.html
    total_ethernet_bytes = global_variables.global_sum_ip_packet_sizes + global_variables.global_pipeline_packet_count * 38
    total_pipeline_bandwidth = (total_ethernet_bytes * 8 / 1000000) / (full_pipeline_time / 1000000000)
    from_init_bandwidth = (total_ethernet_bytes * 8 / 1000000) / (time_from_initialization / 1000000000)
    from_processing_bandwidth = (total_ethernet_bytes * 8 / 1000000) / (time_from_processing / 1000000000)
    log.info("---\nData volume and bandwidth:\n"
             f"  {global_variables.global_pipeline_packet_count} IP packets\n"
             f"  {global_variables.global_sum_ip_packet_sizes} bytes IP traffic\n"
             f"  {total_ethernet_bytes} bytes Ethernet traffic\n"
             f"  {round(total_pipeline_bandwidth, 2)} megabits/second "
             f"Ethernet traffic bandwidth for full pipeline\n"
             f"  {round(from_init_bandwidth, 2)} megabits/second "
             f"Ethernet traffic bandwidth from initialization start\n"
             f"  {round(from_processing_bandwidth, 2)} megabits/second "
             f"Ethernet traffic bandwidth from processing start\n"
    )



if __name__ == "__main__":

    # Argument parser initialization.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-path", type=str, required=True)
    parser.add_argument("--influx-token", type=str, required=False, default="")
    log.debug("Parsing arguments.")
    args = parser.parse_args()

    main(args.config_path, args.influx_token)
