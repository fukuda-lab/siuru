import argparse
import itertools
import json
import os
import subprocess
import time
from datetime import datetime
from typing import List

from jinja2 import Template

from dataloaders import *
from models import *

from encoders.DefaultEncoder import DefaultEncoder
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

    def git_tag():
        get_git_tag_cmd = ["git", "rev-parse", "--short", "HEAD"]
        tag_result = subprocess.run(get_git_tag_cmd, capture_output=True)
        if tag_result.returncode == 0:
            tag = tag_result.stdout.decode("utf-8").strip()
            check_modifications_cmd = ["git", "diff", "--quiet", "--exit-code"]
            mod_result = subprocess.run(check_modifications_cmd)
            if mod_result.returncode != 0:
                tag += "-edited"
        else:
            tag = "undefined"
        return tag

    def time_now():
        return datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

    def project_root():
        return os.path.abspath(os.path.join(__file__, ".."))

    log.debug(f"Loading configuration from: {config_path}")
    with open(config_path) as config_file:
        template = Template(config_file.read())
        template.globals["timestamp"] = time_now
        template.globals["project_root"] = project_root
        template.globals["git_tag"] = git_tag
        configuration = json.loads(template.render())
    assert configuration, "Could not load configuration file!"
    log.debug("Configuration loaded!")

    feature_generators_list = []
    metadata_generators_list = []
    label_generators_list = []
    feature_list = []

    for data_source in configuration["DATA_SOURCES"]:
        loader_name = data_source["loader"]
        loader_class = globals()[loader_name]
        loader: IDataLoader = loader_class(**data_source)

        feature_generators_list.append(loader.get_features())
        metadata_generators_list.append(loader.get_metadata())
        label_generators_list.append(loader.get_labels())

        if not feature_list:
            # TODO determine feature list as union from different data loaders,
            #  not just first signature.
            feature_list = loader.feature_signature()

        log.info(f"Adding {loader.__name__} to pipeline.")
        log.debug(f"File to be loaded: {data_source['path']}")

    model_instances: List[IAnomalyDetectionModel] = []

    for model in configuration["MODELS"]:
        # Initialize model from class name.
        model_name = model["module"]
        model_class = globals()[model_name]
        model_instance: IAnomalyDetectionModel = model_class()
        model_instances.append(model_instance)

    feature_generator = itertools.chain.from_iterable(feature_generators_list)
    metadata_generator = itertools.chain.from_iterable(metadata_generators_list)
    label_generator = itertools.chain.from_iterable(label_generators_list)

    # Pick encoding -- there is only one for now.
    log.info("Encoding features.")
    e = DefaultEncoder()
    encoded_feature_generator = e.encode(feature_generator)

    # Start models and reporting.
    for model in model_instances:
        if not model.use_existing_model:
            # Train the model.
            # TODO Define training and test data split.
            model.train(
                encoded_feature_generator,
                label_generator,
                path_to_store=model_store_file,
                feature_names=[str(f) for f in feature_list],
            )
        if args.autoencoder:
            # TODO: AE can be trained with anomalous or non-anomalous data, make the choice explicit!
            feats = list(encoded_feature_generator)
            labels = list(label_generator)
            mlp_autoencoder.train(
                # Training AE to predict non-anomalous data, testing against anomalous.
                (f for i, f in enumerate(feats) if labels[i] == 0),
                (f for i, f in enumerate(feats) if labels[i] == 1),
            )
    else:  # Prediction time!
        reporter = None
        labels = list(label_generator)
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
