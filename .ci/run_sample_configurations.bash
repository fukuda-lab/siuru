#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail


# Set path variables.
repo_root="$(realpath $(dirname $BASH_SOURCE[0])/..)"
conf_path="$repo_root/configurations/examples"

# Move to repository root to make sure all subsequent commands
# run from the right directory.
cd "$repo_root"

# Run all training examples sequentially.
counter=1
for p in $(ls $conf_path/train); do
    echo "-----------------------------------------------"
    echo "$counter: running example configuration from $p"
    echo "-----------------------------------------------"
    ((++counter))

    python3 code/IoT-AD.py -c "$conf_path/train/$p" || \
    { echo "Error while running $conf_path/train/$p"; exit 1; }
done

# Run all test examples sequentially.
counter=1
for p in $(ls $conf_path/test); do
    echo "-----------------------------------------------"
    echo "$counter: running example configuration from $p"
    echo "-----------------------------------------------"
    ((++counter))

    python3 code/IoT-AD.py -c "$conf_path/test/$p" || \
    { echo "Error while running $conf_path/test/$p"; exit 1; }
done

echo "---------"
echo "Finished!"
echo "---------"
