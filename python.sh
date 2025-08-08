#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export RUNTIME_DIR=${SCRIPT_DIR}/_build/linux-x86_64/release
export PYTHONHOME=${RUNTIME_DIR}/python-runtime
export PYTHON=${PYTHONHOME}/python

export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PYTHONHOME}/lib:${RUNTIME_DIR}
export PYTHONPATH=${RUNTIME_DIR}/python:${RUNTIME_DIR}/bindings-python:source

echo Running script in "${SCRIPT_DIR}"
pushd "$SCRIPT_DIR" > /dev/null

if [ ! -f "${PYTHON}" ]; then
    echo "Python, USD, and Omniverse dependencies are missing. Run \"./repo.sh build\" to configure them."
    popd
    exit
fi

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
        SAMPLE_PATH=source/${sample}/${sample}.py
        if [ -f "${SAMPLE_PATH}" ]; then
            "${PYTHON}" -s "${SAMPLE_PATH}" "${@:2}"
        else
            echo "WARNING: ${sample} not found at ${SAMPLE_PATH}"
        fi
    done

    echo ""
    echo "=== All samples completed ==="
    popd > /dev/null
    exit 0
fi

"${PYTHON}" -s "$@"
popd > /dev/null
