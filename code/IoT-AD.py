import argparse
import os
import subprocess
import sys

import encode_features
import models.random_forest
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
    parser.add_argument("-f", "--file", type=str, required=False)
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

    processed_feature_generator = None
    # Pass input for processing.
    if args.file:
        log.info(f"Processing features from file.")
        pcap_call = [args.preprocessor, "stream-file", args.file]
        process = subprocess.Popen(pcap_call, stdout=subprocess.PIPE, universal_newlines=True)
        processed_feature_generator = preprocess_features.preprocess((line for line in process.stdout.readlines()))
    elif args.device:
        raise NotImplementedError("TODO: Implement network device input to feature processor.")
    assert processed_feature_generator

    # Pick encoding -- there is only one for now.
    log.info("Encoding features.")
    encoded_feature_generator = encode_features.default_encoding(processed_feature_generator)

    # Label generators (or sources) -- hardcoded for now.
    all_labels = {
        "MQTTset/Data/PCAP/capture_flood.pcap": [1 for _ in range(613)]
    }
    if args.file:
        # Extract relative path to dataset. Assumes there is no subdirectory named "data"!
        path_components = args.file.split(os.path.sep)
        try:
            data_dir_idx = len(path_components) - path_components[::-1].index("data") - 1
        except ValueError:
            log.error(f"Path {args.file} is not under the data directory!")
            return
        relative_data_path = os.path.join(*path_components[data_dir_idx+1:])
        if relative_data_path not in all_labels:
            log.error(f"Labels not defined for {relative_data_path}")
            return
        dataset_labels = all_labels[relative_data_path]
    else:
        dataset_labels = None

    if args.count:
        count = 0
        for _ in encoded_feature_generator:
            count += 1
        log.info(f"Counted {count} data points.")
        return

    # Start models and reporting.
    if args.train:
        if args.random_forest:
            models.random_forest.train(encoded_feature_generator, dataset_labels)
        if args.autoencoder:
            pass
    else:  # TODO Run classifier in a separate thread.
        if args.random_forest:
            pass
        if args.autoencoder:
            pass


if __name__ == '__main__':
    main()
