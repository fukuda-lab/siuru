import argparse
import itertools
import os
import subprocess
import sys

import encode_features
import models.random_forest
from dataloaders.MQTTsetLoader import MQTTsetLoader
from pipeline_logger import PipelineLogger
import preprocess_features

log = PipelineLogger.get_logger()


def main():
    """
    Start the IoT anomaly detection pipeline.

    :return: TODO Exit code?
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
    # parser.add_argument("-o", "--open-flow-features", choices=[x for x in OpenFlowFeature], default="all")

    # TODO Feature encoding options.

    # Output number of received data points. Iterates over all elements in generator.
    parser.add_argument("-c", "--count", action="store_true")

    # Anomaly detection options.
    parser.add_argument("-t", "--train", action="store_true")
    # TODO Load a named model instead of hardcoded options.
    parser.add_argument("-r", "--random-forest", action="store_true")
    parser.add_argument("-a", "--autoencoder", action="store_true")

    # TODO Reporting options.

    log.debug("Parsing arguments.")
    args = parser.parse_args()

    available_dataloaders = [MQTTsetLoader]

    feature_generators = []
    label_generators = []

    # Pass input for processing.
    if args.files:
        for file in args.files:
            # Find a suitable dataloader.
            dataloader_kwargs = {
                "filepath": file,
                "preprocessor_path": args.preprocessor
            }
            loadable = False
            for loader in available_dataloaders:
                if loader.can_load(file):
                    log.info(f"Adding {loader.__name__} to pipeline for input file: {file}")
                    loader_inst = loader()
                    feature_generators.append(loader_inst.preprocess(**dataloader_kwargs))
                    label_generators.append(loader_inst.get_labels(**dataloader_kwargs))
                    loadable = True
                    break
            if not loadable:
                log.error(f"No data preprocessor available for file: {file}")
                return

    elif args.device:
        raise NotImplementedError("TODO: Implement network device input to feature processor.")

    processed_feature_generator = itertools.chain.from_iterable(feature_generators)
    label_generator = itertools.chain.from_iterable(label_generators)

    if args.count:
        count = 0
        for _ in processed_feature_generator:
            count += 1
        log.info(f"Counted {count} data points.")
        return

    # Pick encoding -- there is only one for now.
    log.info("Encoding features.")
    encoded_feature_generator = encode_features.default_encoding(processed_feature_generator)

    # Start models and reporting.
    if args.train:
        if args.random_forest:
            models.random_forest.train(encoded_feature_generator, label_generator)
        if args.autoencoder:
            pass
    else:  # TODO Run classifier in a separate thread.
        if args.random_forest:
            pass
        if args.autoencoder:
            pass


if __name__ == '__main__':
    main()
