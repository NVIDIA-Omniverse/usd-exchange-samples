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

"${PYTHON}" -s source/assetValidator/assetValidatorBootstrap.py "$@"

popd > /dev/null
