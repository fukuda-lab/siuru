#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# TODO limiting the split count means packets will be written in a round-robin policy.
# Instead, we may wish to split X first flows to test, then X to validation, then test.
# Easiest way is to not limit the file count (each flow is written into a separate file)
# and calculate the number of flows for each set after splitting finishes.

if [[ $# != 5 || "$1" == "--help" ]]; then
    echo ""
    echo "Usage: ./split_dataset.bash <input-file> <output-dir> <split-count> <train-count> <validation-count>"
    echo ""
    echo "Split a PCAP file to #(split-count) files by flow, then merge them into a"
    echo "train-validation-test set stored as [train|validate|test].pcap in the output directory."
    echo "The training set will contain flows from the first #(train-count) files,"
    echo "validation the next #(validation-count) files, and the remaining files will be in test."
    echo ""
    exit 1
fi

pcap_path=$1
output_path=$2
split_count=$3
train_set=$4
validation_set=$5
test_set=$((split_count - train_set - validation_set))

mkdir -p $output_path

# TODO Handle non-UDP/TCP packets if you need to work with datasets that contain them!
# All packets which aren't UDP or TCP (hence don't belong to any connection) will be
# written to one output file, separate from the other output files (usually file#0).
PcapSplitter -f $pcap_path -o $output_path -m connection -p $split_count

train_files=()
validation_files=()
test_files=()

for f in $(ls $output_path); do
    if ((0 < train_set--)); then
        train_files+=($output_path/$f)
    elif ((0 < validation_set--)); then
        validation_files+=($output_path/$f)
    else
        test_files+=($output_path/$f)
    fi
done

echo
echo Training set:
for f in ${train_files[@]}; do
    echo "    $f"
done

echo
echo Validation set:
for f in ${validation_files[@]}; do
    echo "    $f"
done

echo
echo Test set:
for f in ${test_files[@]}; do
    echo "    $f"
done

mergecap -w $output_path/train.pcapng ${train_files[@]}
mergecap -w $output_path/validation.pcapng ${validation_files[@]}
mergecap -w $output_path/test.pcapng ${test_files[@]}
