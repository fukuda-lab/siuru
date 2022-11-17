# kafka-pcap

A modified example from [SINETStream-demo](https://github.com/nii-gakunin-cloud/sinetstream-demo/) that can log network traffic sent to the Kafka broker.

## Usage

Requires configuring Kafka container as described [in SINETStream demo](https://github.com/nii-gakunin-cloud/sinetstream-demo/blob/main/option/Server/Kafka/README.en.md).
Then you can run the modified Kafka demo with packet capture: 

```bash
# Startup:
docker volume create --name=pcap-capture
docker-compose up -d

# Start test apps as separate processes. Let the system run, PCAP data will be logged.

# When done:
docker-compose down --volumes
docker container create --name temp -v pcap-capture:/data hello-world
docker cp temp:/data ./pcap-capture
docker rm temp

# To remove logged data:
docker volume rm pcap-capture
docker volume prune
```

## Test applications
Python virtual environment recommended.
Note that the Kafka container takes ~10 seconds to start up and is unresponsive until then.

```bash
pip install -r requirements.txt
python test-apps/test-producer.py -s text-1
```

```bash
python test-apps/test-consumer.py -s text-1
```