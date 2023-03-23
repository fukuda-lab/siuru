import argparse
import itertools
import json
import os
import time
from typing import List

from jinja2 import Template

from common.functions import time_now, project_root, git_tag
from dataloaders import *
from encoders.IDataEncoder import IDataEncoder
from models import *
from preprocessors import *
from encoders import *

from pipeline_logger import PipelineLogger
from prediction_output import Prediction
from reporting.InfluxDBReporter import InfluxDBReporter

log = PipelineLogger.get_logger()


def main():
    """
    Start the IoT anomaly detection pipeline.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config-path", type=str, required=True)

    # TODO Add feature selection when you have a lot of free time...

    # Reporting options.
    parser.add_argument("--influx-token", type=str, required=False)

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
        configuration = json.loads(template.render())
    assert configuration, "Could not load configuration file!"
    log.debug("Configuration loaded!")

    feature_stream = []

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

    model_specification = configuration["MODEL"]
    # Initialize model from class name.
    model_name = model_specification["class"]
    model_class = globals()[model_name]
    model_instance: IAnomalyDetectionModel = model_class(**model_specification)

    encoder_name = model_specification["encoder"]["class"]
    encoder_class = globals()[encoder_name]
    encoder_instance: IDataEncoder = encoder_class(**model_specification["encoder"]["kwargs"])

    log.info("Encoding features.")
    encoded_feature_generator = encoder_instance.encode(feature_stream)

    # Start model and reporting.
    if not model_specification["use_existing_model"]:
        # Train the model.
        # TODO Define training and test data split.
        model_instance.train(
            encoded_feature_generator,
            path_to_store=model_instance.store_file
        )
    else:  # Prediction time!
        reporter = None
        if (
            args.influx_url
            or args.influx_org
            or args.influx_token
            or args.influx_bucket
        ):
            assert (
                args.influx_url
                and args.influx_org
                and args.influx_token
                and args.influx_bucket
            ), "Set InfluxDB index, token and bucket values to activate reporting!"
            reporter = InfluxDBReporter(
                args.influx_url, args.influx_org, args.influx_token, args.influx_bucket
            )

        if args.random_forest:
            predictor = random_forest.RandomForestModel(model_store_file)
            count = 0
            start = time.perf_counter()
            for sample, metadata in zip(encoded_feature_generator, metadata_generator):
                # TODO Metadata must be passed depending on data the model was
                #  trained with... how?
                model_output = predictor.predict_packet(sample.reshape(1, -1))
                if reporter:
                    p = Prediction(
                        predictor.name, feature_list, sample, metadata, model_output
                    )
                    reporter.report(p, "kaiyodai_ship")
                count += 1
            end = time.perf_counter()
            packets_per_second = count / (end - start)
            log.info(
                f"Predicted {count} samples in {end - start} seconds ({packets_per_second} packets/s)."
            )
        if args.autoencoder:
            pass


if __name__ == "__main__":
    main()
