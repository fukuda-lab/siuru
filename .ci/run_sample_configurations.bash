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

# Run all examples sequentially.
counter=1
for p in $(ls -r $conf_path); do
    echo "-----------------------------------------------"
    echo "$counter: running example configuration from $p"
    echo "-----------------------------------------------"
    ((++counter))

    python3 code/IoT-AD.py -c "$conf_path/$p"
done