import argparse
import itertools
import json
import os
import time
from typing import List

from jinja2 import Template

from common.functions import time_now, project_root, git_tag
from dataloaders import *
from models import *
from preprocessors import *
from encoders import *
from reporting import *

from pipeline_logger import PipelineLogger

log = PipelineLogger.get_logger()


def main():
    """
    Run the IoT anomaly detection pipeline based on a configuration file.
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config-path", type=str, required=True)
    parser.add_argument("--influx-token", type=str, required=False, default="")

    log.debug("Parsing arguments.")
    args = parser.parse_args()

    config_path = os.path.abspath(args.config_path)
    assert os.path.exists(config_path), "Config file not found!"

    log.debug(f"Loading configuration from: {config_path}")
    with open(config_path) as config_file:
        template = Template(config_file.read())
        template.globals["timestamp"] = time_now()
        template.globals["project_root"] = project_root()
        template.globals["git_tag"] = git_tag()
        template.globals["influx_token"] = args.influx_token
        configuration = json.loads(template.render())
    assert configuration, "Could not load configuration file!"
    log.debug("Configuration loaded!")

    # TODO add logfile path and level to configurations,
    #  then initialize a file logger!

    feature_stream = itertools.chain([])

    for data_source in configuration["DATA_SOURCES"]:
        loader_name = data_source["loader"]["class"]
        loader_class = globals()[loader_name]
        log.info(f"Adding {loader_class.__name__} to pipeline.")
        loader: IDataLoader = loader_class(**data_source["loader"]["kwargs"])
        new_feature_stream = loader.get_features()

        for preprocessor_specification in data_source["preprocessors"]:
            preprocessor_name = preprocessor_specification["class"]
            preprocessor_class = globals()[preprocessor_name]
            log.info(f"Adding {preprocessor_class.__name__} to pipeline.")
            preprocessor: IPreprocessor = preprocessor_class(
                **preprocessor_specification["kwargs"]
            )
            new_feature_stream = preprocessor.process(new_feature_stream)

        feature_stream = itertools.chain(feature_stream, new_feature_stream)

    if len(configuration["MODEL"]) == 0:
        log.info("No model specified - counting input data points:")
        count = 0
        for _ in feature_stream:
            count += 1
        log.info(f"{count} elements.")
        exit(0)

    model_specification = configuration["MODEL"]
    # Initialize model from class name.
    model_name = model_specification["class"]
    model_class = globals()[model_name]
    model_instance: IAnomalyDetectionModel = model_class(
        full_config_json=json.dumps(configuration, indent=4), **model_specification
    )

    encoder_name = model_specification["encoder"]["class"]
    encoder_class = globals()[encoder_name]
    encoder_instance: IDataEncoder = encoder_class(
        **model_specification["encoder"]["kwargs"]
    )

    log.info("Encoding features.")
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
            # This is a hacky way to support both lists of sample features
            # (as encoded my MultiSampleEncoder) and a dict containing the
            # features of a single sample.
            # TODO make more elegant (or move the logging to the encoder)!
            first_sample_data = first_sample_data[0]
        for k, v in first_sample_data.items():
            log.debug(f" | {k}: {v}")

    if model_specification["train_new_model"]:
        # Train the model.
        start = time.perf_counter()
        model_instance.train(
            encoded_feature_generator, path_to_store=model_instance.store_file
        )
        end = time.perf_counter()
        log.info(f"Trained new model in {end - start} seconds.")

    else:
        # Prediction time!
        reporter_instances: List[IReporter] = []

        for output in configuration["OUTPUT"]:
            reporter_name = output["class"]
            reporter_class = globals()[reporter_name]
            reporter_instance = reporter_class(**output["kwargs"])
            reporter_instances.append(reporter_instance)

        count = 0
        start = time.perf_counter()

        for sample, encoding in encoded_feature_generator:
            for predicted_sample in model_instance.predict(sample, encoding):
                for reporter_instance in reporter_instances:
                    reporter_instance.report(predicted_sample)
                count += 1

        end = time.perf_counter()
        packets_per_second = count / (end - start)
        log.info(
            f"Predicted and reported {count} samples in {end - start} seconds"
            f" ({packets_per_second} packets/s)."
        )

        for reporter_instance in reporter_instances:
            reporter_instance.end_processing()


if __name__ == "__main__":
    main()
