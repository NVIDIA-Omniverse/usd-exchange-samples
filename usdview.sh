#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export USDVIEW_SCRIPT=${SCRIPT_DIR}/_build/target-deps/usd/release/scripts/usdview_gui.sh

if [ ! -f "${USDVIEW_SCRIPT}" ]; then
    echo "${USDVIEW_SCRIPT} does not exist, run "./repo.sh build" to fetch the USD libraries."
    exit 3
fi

${USDVIEW_SCRIPT} $@ &
