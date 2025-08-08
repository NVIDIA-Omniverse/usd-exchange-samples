#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export RUNTIME_DIR=${SCRIPT_DIR}/_build/linux-x86_64/release
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${RUNTIME_DIR}
pushd "$SCRIPT_DIR" > /dev/null

# Read samples from allSamples.txt
samples=()
while IFS= read -r line; do
    # Skip empty lines and lines starting with #
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        samples+=("$line")
    fi
done < "${SCRIPT_DIR}/allSamples.txt"

# Check if user wants to run all samples
if [ "$1" = "all" ]; then
    echo "Running all samples in order..."

    for sample in "${samples[@]}"; do
        echo ""
        echo "=== Running $sample ==="
        SAMPLE_PATH=${RUNTIME_DIR}/${sample}
        if [ -f "${SAMPLE_PATH}" ]; then
            ${SAMPLE_PATH} "${@:2}"
        else
            echo "WARNING: ${sample} not found at ${SAMPLE_PATH}"
        fi
    done

    echo ""
    echo "=== All samples completed ==="
    popd > /dev/null
    exit 0
fi

export SAMPLE=${RUNTIME_DIR}/${1}

if [ ! -f "${SAMPLE}" ]; then
    echo "<${SAMPLE}> does not exist, run one of the existing samples, eg. './run.sh createStage': "
    echo " all (runs all samples in order)"
    for sample in "${samples[@]}"; do
        echo " $sample"
    done
    popd > /dev/null
    exit 3
fi

${SAMPLE} "${@:2}"
popd > /dev/null
