import argparse
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
    parser.add_argument("-f", "--file", type=str, required=False)
    parser.add_argument("-s", "--stdin", action="store_true")
    parser.add_argument("-p", "--pipe", type=str, required=False)

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
        log.info(f"Reading from file: {args.file}")
        raise NotImplementedError("TODO: Implement file input to feature processor.")
    elif args.stdin:
        log.info(f"Processing features from stdin.")
        processed_feature_generator = preprocess_features.preprocess((line for line in sys.stdin))
    elif args.pipe:
        raise NotImplementedError("TODO: Implement file input to feature processor.")

    # Pick encoding -- there is only one for now.
    assert processed_feature_generator

    log.info("Encoding features.")
    encoded_feature_generator = encode_features.default_encoding(processed_feature_generator)

    if args.count:
        count = 0
        for elem in encoded_feature_generator:
            count += 1
        log.info(f"Counted {count} data points.")

    # Start models and reporting.
    if args.train:
        if args.random_forest:
            pass
            # models.random_forest.train(encoded_feature_generator)
        if args.autoencoder:
            pass
    else:  # TODO Run classifier in a separate thread.
        if args.random_forest:
            pass
        if args.autoencoder:
            pass


if __name__ == '__main__':
    main()
