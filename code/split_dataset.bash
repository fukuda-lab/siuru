#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

valid_args=true

if (( $# == 0 )); then
    valid_args=false
else
    if [[ "$1" != "head-tail" && "$1" != "round-robin" ]]; then
        valid_args=false
    fi
    if [[ "$1" == "head-tail" && $# != 5 ]]; then
        valid_args=false
    elif [[ "$1" == "round-robin" && $# != 6 ]]; then
        valid_args=false
    fi
fi

if [[ $valid_args != "true" ]]; then
    echo "Provided parameters don't match the expected signature! Here's help:"
    echo ""
    echo "========================== split_dataset.bash ============================"
    echo "Split captured packets by flow into a training, validation, and test set."
    echo "========================================================================="
    echo ""
    echo "Usage: ./split_dataset.bash <head-tail|round-robin> <args ...>"
    echo "Args head-tail: <input-file> <output-dir> <%train> <%validation>"
    echo "Args round-robin: <input-file> <output-dir> <#train> <#validation> <#test>"
    echo ""
    echo "head-tail: Writes the flows in input data to separate files (can be many!),"
    echo "then merges them into [train|validate|test].pcapng files in the output dir."
    echo "train.pcapng will contain the first <%train> percent of all created files,"
    echo "validation the next <%validation> percent, remaining ones will be in test."
    echo ""
    echo "round-robin: Writes the packets to <#train + #validation + #test> files,"
    echo "then merges them into [train|validate|test].pcapng files in output directory."
    echo "train.pcapng will contain flows from the first <#train> files,"
    echo "validation the next <#validation> files, remaining ones will be in test."
    echo "The file for each flow is assigned circularly, hence the name round-robin."
    echo ""
    exit 1
fi

mode=$1
pcap_path=$2
output_path=$3

# Save output files with the same extension as input.
extension="${pcap_path##*.}"

mkdir $output_path
tmp_dir=$output_path/pcapsplitter-tmp
mkdir $tmp_dir

# TODO Handle non-UDP/TCP packets if you need to work with datasets that contain them!
# All packets which aren't UDP or TCP (hence don't belong to any connection) will be
# written to one output file, separate from the other output files (usually file#0).

if [[ "$mode" == "round-robin" ]]; then
    train_set=$4
    validation_set=$5
    test_set=$6
    split_count=$((train_set + validation_set + test_set))

    PcapSplitter -f $pcap_path -o $tmp_dir -m connection -p $split_count
else
    train_percent=$4
    validation_percent=$5
    test_percent=$((100 - train_percent - validation_percent))

    PcapSplitter -f $pcap_path -o $tmp_dir -m connection

    file_count=$(ls -1q $tmp_dir | wc -l)
    train_set=$(echo "$file_count * $train_percent / 100" | bc)
    validation_set=$(echo "$file_count * $validation_percent / 100" | bc)
    test_set=$((file_count - train_set - validation_set))
fi

train_files=()
validation_files=()
test_files=()

for f in $(ls $tmp_dir); do
    if ((0 < train_set--)); then
        train_files+=($tmp_dir/$f)
    elif ((0 < validation_set--)); then
        validation_files+=($tmp_dir/$f)
    else
        test_files+=($tmp_dir/$f)
    fi
done

readme_file="$output_path/README.md"
touch "$readme_file"

echo "PCAP files created with split_dataset.bash" >> "$readme_file"
echo "Mode: $mode" >> "$readme_file"
echo "Source file: $pcap_path" >> "$readme_file"
if [[ "$mode" == "round-robin" ]]; then
    echo "Files in training set: ${#train_files[@]}" >> "$readme_file"
    echo "Files in validation set: ${#validation_files[@]}" >> "$readme_file"
    echo "Files in test set: ${#test_files[@]}" >> "$readme_file"
else
    echo "Flows in training set: ${#train_files[@]}" >> "$readme_file"
    echo "Flows in validation set: ${#validation_files[@]}" >> "$readme_file"
    echo "Flows in test set: ${#test_files[@]}" >> "$readme_file"
fi

# Only call mergecap if there are files to be merged. Skip if e.g.
# no validation set was requested.
if (( ${#train_files[@]} )); then
    mergecap -w $output_path/train.$extension ${train_files[@]}
fi

if (( ${#validation_files[@]} )); then
    mergecap -w $output_path/validation.$extension ${validation_files[@]}
fi

if (( ${#test_files[@]} )); then
    mergecap -w $output_path/test.$extension ${test_files[@]}
fi

rm -r $tmp_dir
