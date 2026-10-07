#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source "${SCRIPT_DIR}/tools/wheel/configure_python_package_index.sh"
export PYTHONPATH="${SCRIPT_DIR}/source/python"
export PACKMAN_PYTHON="${SCRIPT_DIR}/tools/packman/python.sh"
export VENV="${SCRIPT_DIR}/_build/usdex_env"

if [[ -d "${VENV}" ]]; then
    echo "Using existing venv: ${VENV}"
    source "${VENV}/bin/activate"
else
    echo "Building venv: ${VENV}"
    "${PACKMAN_PYTHON}" -m venv "${VENV}"

    # Get the usd-exchange version from packman XML
    USDEX_VERSION=$("${PACKMAN_PYTHON}" "${SCRIPT_DIR}/tools/wheel/get_usdex_version.py")

    source "${VENV}/bin/activate"

    # Install packages with optional private index
    echo "Installing usd-exchange wheel version ${USDEX_VERSION} from ${PIP_EXTRA_INDEX_URL}"
    python3 -m pip install "usd-exchange[test]==${USDEX_VERSION}"
fi

python3 "${SCRIPT_DIR}/source/validateUsd/validateUsdBootstrap.py" "$@"
