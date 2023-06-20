# syntax=docker/dockerfile:1
FROM ubuntu:20.04
ENV TZ=Europe/Berlin
ENV DEBIAN_FRONTEND=noninteractive

COPY ./ /code/

RUN apt-get clean && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install \
    apt-utils \
    wireshark-common \
    tcpdump \
    libpcap-dev \
    git \
    cmake \
    gcc \
    clang \
    clang-tools \
    python3 \
    python3-pip \
    bc

RUN pip3 install -r code/requirements.txt

# Using "build-docker" to not collide with the "build" dir.
RUN cd /code/cpp-extract-features/PcapPlusPlus && \
    cmake -S . -B build-docker && \
    cmake --build build-docker && \
    cmake --install build-docker

RUN cd /code/cpp-extract-features && \
    mkdir cmake-build && \
    cd cmake-build && \
    cmake ../.. && \
    cmake --build . --config Release && \
    setcap cap_net_raw+ep $(pwd)/pcap-feature-extraction

# TODO test if the setcap command is needed for live traffic capture in Docker.
