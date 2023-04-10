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
    tcpdump \
    libpcap-dev \
    git \
    cmake \
    gcc \
    clang \
    clang-tools \
    python3 \
    python3-pip

RUN pip3 install -r code/requirements.txt

# Using "build-docker" to not collide with the "build" dir.
RUN cd /code/cpp-extract-features/PcapPlusPlus && \
    cmake -S . -B build-docker && \
    cmake --build build-docker && \
    cmake --install build-docker

RUN mkdir cmake-build-debug && \
    cd cmake-build-debug && \
    cmake ../code && \
    cmake --build .
