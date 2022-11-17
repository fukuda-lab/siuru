FROM ubuntu

RUN apt clean && \
    apt update && \
    apt -y upgrade && \
    apt -y install \
    tcpdump

VOLUME /pcap
RUN mkdir /pcap-src
ADD packet-capture/* /pcap-src/
CMD /pcap-src/capture.sh
