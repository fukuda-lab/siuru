import argparse
import re
import sys

import encode_features
import models.random_forest
import preprocess_features


def main():
    """
    Start the IoT anomaly detection pipeline.

    :return: TODO Exit code?
    """

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    input_parser = subparsers.add_parser("input")
    input_parser.add_argument("-f", "--file", type=str, required=False)
    input_parser.add_argument("-s", "--stdin", action="store_true")
    input_parser.add_argument("-p", "--pipe", type=str, required=False)

    # TODO Add feature selection when you have a lot of free time...
    # feature_select_parser = subparsers.add_parser("select")
    # feature_select_parser.add_argument("-p", "--packet-features", choices=[x for x in PacketFeature], default="all")
    # feature_select_parser.add_argument("-h", "--host-features", choices=[x for x in HostFeature], default="all")
    # feature_select_parser.add_argument("-o", "--open-flow-features", choices=[x for x in OpenFlowFeature], default="all")

    feature_encoding_parser = subparsers.add_parser("encode")

    anomaly_detection_parser = subparsers.add_parser("model")
    anomaly_detection_parser.add_argument("-t", "--train", action="store_true")
    # TODO Load a named model instead of hardcoded options.
    anomaly_detection_parser.add_argument("-r", "--random-forest", action="store_true")
    anomaly_detection_parser.add_argument("-a", "--autoencoder", action="store_true")

    report_parser = subparsers.add_parser("report")

    input_args = input_parser.parse_args()
    detection_args = anomaly_detection_parser.parse_args()

    processed_feature_generator = None
    # Pass input for processing.
    if input_args.file:
        raise NotImplementedError("TODO: Implement file input to feature processor.")
    elif input_args.stdin:
        processed_feature_generator = preprocess_features.preprocess((line for line in sys.stdin))
    elif input_args.pipe:
        raise NotImplementedError("TODO: Implement file input to feature processor.")

    # Pick encoding -- there is only one for now.
    assert processed_feature_generator
    encoded_feature_generator = encode_features.default_encoding(processed_feature_generator)

    # Start models and reporting.
    if detection_args.train:
        if detection_args.random_forest:
            models.random_forest.train(encoded_feature_generator)
        if detection_args.autoencoder:
            pass
    else:  # TODO Run classifier in a separate thread.
        if detection_args.random_forest:
            pass
        if detection_args.autoencoder:
            pass


if __name__ == '__main__':
    main()
