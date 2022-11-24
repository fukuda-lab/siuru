#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# TODO make the volume name configurable over env, replace all references to pcap-data.

# Always rebuild the kafka-pcap container because docker-compose does not update it.
cd "$( dirname "${BASH_SOURCE[0]}" )/Kafka/kafka-pcap"
docker build . -t kafka-pcap:latest
cd ..
docker volume create --name=pcap-data

# Run zookeeper, kafka, and kafka-pcap all in one go.
docker-compose up -d
