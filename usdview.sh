#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export USDVIEW_SCRIPT=${SCRIPT_DIR}/_build/target-deps/usd/release/scripts/usdview_gui.sh
export USDVIEW_VENV=${SCRIPT_DIR}/_build/usdview_venv

if [ ! -f "${USDVIEW_SCRIPT}" ]; then
    echo "${USDVIEW_SCRIPT} does not exist, run "./repo.sh build" to fetch the USD libraries."
    exit 3
fi

if [ -d "${USDVIEW_VENV}" ]; then
    echo "Using existing venv: ${USDVIEW_VENV}"
    source ${USDVIEW_VENV}/bin/activate
else
    echo "Building venv: ${USDVIEW_VENV}"
    ./python.sh -m venv ${USDVIEW_VENV}
    source ${USDVIEW_VENV}/bin/activate
    python -m pip install -r ${SCRIPT_DIR}/_build/target-deps/usd/release/requirements.txt
fi

${USDVIEW_SCRIPT} $@
