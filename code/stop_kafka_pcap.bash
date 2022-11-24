#!/usr/bin/env bash
# Delay setting errexit because "docker-compose down" does not like to exit with 0.
set -o nounset
set -o pipefail
set -x

# TODO make the volume name configurable over env, replace all references to pcap-data.

CODE_DIR="$( realpath $( dirname "${BASH_SOURCE[0]}" ) )"

# Shut down containers started in run_kafka_pcap.
cd "$CODE_DIR/Kafka"
docker-compose down --volumes
cd ".."
set -o errexit

# Extract data and store it neatly, then get rid of the Docker volume.
timestamp=$(date +%s)
data_dir="$CODE_DIR/../data/${timestamp}-pcap-data"
mkdir "$data_dir"

container_name="temp-$timestamp"
docker container create --name $container_name -v pcap-data:/data hello-world
docker cp $container_name:/data "$data_dir/"
docker stop "$container_name"
docker rm "$container_name"
docker volume rm pcap-data
