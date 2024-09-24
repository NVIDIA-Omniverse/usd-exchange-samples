#!/bin/bash

set -e

export RUNTIME_PATH=./usdex/linux-x86_64/release
export LD_LIBRARY_PATH=${RUNTIME_PATH}/lib:${LD_LIBRARY_PATH}

./release/UsdTraverse "$@"
