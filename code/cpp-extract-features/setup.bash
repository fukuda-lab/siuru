#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

conan install "pcapplusplus/[>0]@" -u
