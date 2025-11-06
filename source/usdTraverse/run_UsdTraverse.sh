#!/bin/bash

set -e

export PLATFORM="linux-$(uname -m)"
export RUNTIME_PATH=./usdex/${PLATFORM}/release
export LD_LIBRARY_PATH=${RUNTIME_PATH}/lib:${LD_LIBRARY_PATH}

./release/UsdTraverse "$@"
