import argparse
import itertools
import os
import time

from dataloaders.MawiLoader import MawiLoaderDummy
from encoders.DefaultEncoder import DefaultEncoder
from models import random_forest, mlp_autoencoder
from dataloaders.MQTTsetLoader import MQTTsetLoader
from pipeline_logger import PipelineLogger
from prediction_output import Prediction
from reporting.InfluxDBReporter import InfluxDBReporter

log = PipelineLogger.get_logger()


def main():
    """
    Start the IoT anomaly detection pipeline.
    """
    parser = argparse.ArgumentParser()

    # Input options.
    parser.add_argument("-p", "--preprocessor", type=str, required=True)
    parser.add_argument("-f", "--files", type=str, required=False, nargs="+")
    parser.add_argument("-d", "--device", type=str, required=False)

    # Feature selection options.
    # TODO Add feature selection when you have a lot of free time...
    # parser.add_argument("-p", "--packet-features", choices=[x for x in PacketFeature], default="all")
    # parser.add_argument("-h", "--host-features", choices=[x for x in HostFeature], default="all")
    # parser.add_argument("-o", "--open-flow-features", choices=[x for x in FlowFeature], default="all")

    # TODO Feature encoding options.

    # Output number of received data points. Iterates over all elements in generator.
    parser.add_argument("-c", "--count", action="store_true")

    # Anomaly detection options.
    parser.add_argument("-t", "--train", action="store_true")
    parser.add_argument("-s", "--store-path", type=str, required=False)
    parser.add_argument("-r", "--random-forest", action="store_true")
    parser.add_argument("-a", "--autoencoder", action="store_true")

    # Reporting options.
    parser.add_argument("--influx-url", type=str, required=False)
    parser.add_argument("--influx-org", type=str, required=False)
    parser.add_argument("--influx-bucket", type=str, required=False)
    parser.add_argument("--influx-token", type=str, required=False)

    log.debug("Parsing arguments.")
    args = parser.parse_args()

    # TODO update MawiLoader to use new DataLoader signature!
    available_dataloaders = [MQTTsetLoader, MawiLoaderDummy]

    feature_generators_list = []
    metadata_generators_list = []
    label_generators_list = []
    # TODO determine feature list as union from different data loaders,
    #  not just first signature.
    feature_list = []

    model_store_file = None
    # Check that the desired model saving path is free.
    if args.train and args.store_path:
        model_store_file = os.path.abspath(args.store_path)
        if os.path.exists(model_store_file):
            log.error(f"Model storing path already exists: {model_store_file}")
            return
        model_store_dir = os.path.dirname(model_store_file)
        if not os.path.exists(model_store_dir):
            os.mkdir(model_store_dir)
    elif not args.train and args.store_path:
        model_store_file = os.path.abspath(args.store_path)
        if not os.path.exists(model_store_file):
            log.error(f"No file found under the path: {model_store_file}")
            return

    # Pass input for processing.
    if args.files:
        for file in args.files:
            # Find a suitable dataloader.
            dataloader_kwargs = {
                "filepath": file,
                "preprocessor_path": args.preprocessor,
            }
            loadable = False
            for loader in available_dataloaders:
                if loader.can_load(file):
                    log.info(
                        f"Adding {loader.__name__} to pipeline for input file: {file}"
                    )
                    loader_inst = loader()
                    feature_generators_list.append(
                        loader_inst.get_features(**dataloader_kwargs)
                    )
                    metadata_generators_list.append(
                        loader_inst.get_metadata(**dataloader_kwargs)
                    )
                    label_generators_list.append(
                        loader_inst.get_labels(**dataloader_kwargs)
                    )
                    if not feature_list:
                        feature_list = loader_inst.feature_signature()
                    loadable = True
                    break
            if not loadable:
                log.error(f"No data preprocessor available for file: {file}")
                return

    elif args.device:
        # TODO: Implement feature processing for network interface capture.
        raise NotImplementedError(
            "TODO: Implement network device input to feature processor."
        )

    feature_generator = itertools.chain.from_iterable(feature_generators_list)
    metadata_generator = itertools.chain.from_iterable(metadata_generators_list)
    label_generator = itertools.chain.from_iterable(label_generators_list)

    if args.count:
        count = 0
        for _ in feature_generator:
            count += 1
        log.info(f"Counted {count} data points.")
        return

    # Pick encoding -- there is only one for now.
    log.info("Encoding features.")
    e = DefaultEncoder()
    encoded_feature_generator = e.encode(feature_generator)

    # Start models and reporting.
    if args.train:
        if args.random_forest:
            random_forest.train(
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
            predictor = random_forest.RF(model_store_file)
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
