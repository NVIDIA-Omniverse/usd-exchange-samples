#!/bin/bash

set -e

export CONFIG="${CONFIG:-release}"
export PLATFORM="linux-$(uname -m)"
export RUNTIME_PATH="./usdex/${PLATFORM}/${CONFIG}"
export LD_LIBRARY_PATH="${RUNTIME_PATH}/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

"./${CONFIG}/UsdTraverse" "$@"
