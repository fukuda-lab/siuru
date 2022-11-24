# kafka-pcap

A modified example from [SINETStream-demo](https://github.com/nii-gakunin-cloud/sinetstream-demo/) that can log network traffic sent to the Kafka broker.

> **Warning**
> The example code here and scripts use legacy ``docker-compose`` calls!

## Usage

First configure your Kafka container environment as described [in this SINETStream demo](https://github.com/nii-gakunin-cloud/sinetstream-demo/blob/main/option/Server/Kafka/README.en.md) and
build the kafka-pcap image:

```bash
cd code/Kafka/kafka-pcap
docker build . -t kafka-pcap:latest
```

Then you can run the modified Kafka demo with packet capture.
The name of the volume (pcap-data) is specified in `docker-compose.yml`.

```bash
cd code/Kafka
# Startup:
docker volume create --name=pcap-data
docker-compose up -d

# Start test apps as separate processes, see instructions below.
# Let the system run, PCAP data will be logged into attached volume.

# Fetch the logged data using a dummy container with the volume attached:
docker-compose down --volumes
docker container create --name temp -v pcap-data:/data hello-world
docker cp temp:/data ./pcap-data
docker rm temp

# To remove logged data:
docker volume rm pcap-data

# Optionally remove all unused volumes:
docker volume prune
```

You can find scripts that automate the above process under ``code/start_kafka_pcap.bash``
and ``code/stop_kafka_pcap.bash``.

## Test applications
Very basic apps to create some test traffic are available under ``code/Kafka/test-apps``.
Python virtual environment recommended. Install required Python packages with:

```bash
pip install -r requirements.txt
```

Then you can start the test applications stored in ``code/Kafka/test-apps``.
Note that the Kafka Docker container can take ~15 seconds to start up.
The broker will be unresponsive during that time.

```bash
cd Kafka
python test-apps/test-producer.py -s text-1
```
In another terminal, run the consumer:
```bash
cd Kafka
python test-apps/test-consumer.py -s text-1
```