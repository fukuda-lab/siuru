# internship-Laura-Lahesoo
Materials and code from NII internship in IoT anomaly detection.

## data

Pcap files stored with timestamps. Data is automatically moved here when you run the
`code/stop_kafka_pcap.bash` script.

While timestamps in pcap file names are in UST, packets inside have JST timestamps (+9).

### Working with large files

Split up large pcap files before trying to load them with Scapy:

```bash
editcap -c 100000 200608241400.dump 200608241400_split.pcap
```

Extract packets in range 1 to 1000 (inclusive) from a capture file:

```bash
editcap -r 200608241400.dump 200608241400_part_1_1000.dump 1-1000
```

``editcap`` is a command line tool distributed with Wireshark.
See [usage manual](https://www.wireshark.org/docs/man-pages/editcap.html) for details.

## C++ feature extraction

Installed dependencies:
```bash
libpcap0.8 libpcap0.8-dev libpcap0.8-dbg
```

## Sample: load and process features

```bash
cd cmake-build-debug
./pcap-feature-extraction stream-file /path/to/data/MQTTset/Data/PCAP/capture_flood.pcap | python ../code/IoT-AD.py -s
```