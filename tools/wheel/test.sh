#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SOURCE_DIR=${SCRIPT_DIR}/../../source
export PYTHONPATH=${SOURCE_DIR}/python:${SOURCE_DIR}/tests:${PYTHONPATH}

# Check for --reuse argument and rebuild args without it
REUSE_VENV=0
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --reuse)
            REUSE_VENV=1
            shift
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

echo "Running script in ${SCRIPT_DIR}/../.."
pushd "${SCRIPT_DIR}/../.." > /dev/null

# Setup the build environment
VENV=./_build/tests/venv

if [ ${REUSE_VENV} -eq 1 ]; then
    if [ -d "${VENV}" ]; then
        echo "Reusing existing venv: ${VENV}"
    else
        echo "No existing venv found, creating new one: ${VENV}"
        REUSE_VENV=0
    fi
fi

if [ ${REUSE_VENV} -eq 0 ]; then
    echo "Building: ${VENV}"
    if [ -d "${VENV}" ]; then
        rm -rf "${VENV}"
    fi

    ${SCRIPT_DIR}/../packman/python.sh -m venv "${VENV}"
    source "${VENV}/bin/activate"

    # Get the usd-exchange version from packman XML
    USDEX_VERSION=$(${SCRIPT_DIR}/../packman/python.sh "${SCRIPT_DIR}/get_usdex_version.py")

    # Install packages with optional private index
    echo "Installing usd-exchange wheel version ${USDEX_VERSION} from ${PIP_EXTRA_INDEX_URL}"
    python3 -m pip install "usd-exchange[test]==${USDEX_VERSION}"
else
    source "${VENV}/bin/activate"
fi

# Run the tests with the filtered arguments
python3 -m unittest discover -v -s source/tests "${ARGS[@]}"

popd > /dev/null
