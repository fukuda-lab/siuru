# syntax=docker/dockerfile:1
FROM ubuntu:20.04
ENV TZ=Europe/Berlin
ENV DEBIAN_FRONTEND=noninteractive

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

# Copy only the needed files for each build step to avoid triggering
# unnecessary layer rebuilds: https://stackoverflow.com/a/45929376
COPY ./requirements.txt /code/requirements.txt
RUN pip3 install -r code/requirements.txt

COPY ./cpp-extract-features /code/cpp-extract-features
RUN cd /code/cpp-extract-features/PcapPlusPlus && \
    cmake -S . -B build-docker && \
    cmake --build build-docker && \
    cmake --install build-docker

COPY ./CMakeLists.txt /code/CMakeLists.txt
RUN cd /code/cpp-extract-features && \
    mkdir cmake-build && \
    cd cmake-build && \
    cmake ../.. && \
    cmake --build . --config Release && \
    setcap cap_net_raw+ep $(pwd)/pcap-feature-extraction
# TODO test if the setcap command is needed for live traffic capture in Docker.

# Copy the codebase (which is the most likely part to change) as late
# as possible to reduce the number of layers needing to be rebuilt.
COPY ./ /code/
