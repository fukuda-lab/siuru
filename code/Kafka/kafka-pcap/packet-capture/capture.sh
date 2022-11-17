#!/usr/bin/env bash
set -o errexit
set -o nounset

# -c: Exit after logging 10.000.000 packets. Assuming each packet is
#     around 100 bytes, tcpdump exits after logging 1 GB data.
# -G: A new logfile is created each minute.

tcpdump \
-c ${PCAP_MAX_PACKET_COUNT:-10000000} \
-G 60 \
-w /pcap/packets-%F-%T.pcap \
"dst port ${DESTINATION_PORT}" \
-i any \
-Z root
