FROM ubuntu

RUN apt clean && \
    apt update && \
    apt -y upgrade && \
    apt -y install \
    tcpdump \
    libpcap-dev

RUN git clone http://github.com/seladb/PcapPlusPlus.git && \
    cd PcapPlusPlus && \
    cmake -S . -B build && \
    cmake --build build && \
    cd build && \
    cmake --install build

VOLUME /pcap
RUN mkdir /pcap-src
ADD packet-capture/* /pcap-src/
CMD /pcap-src/capture.sh
