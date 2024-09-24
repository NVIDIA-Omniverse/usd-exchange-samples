#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export RUNTIME_DIR=${SCRIPT_DIR}/_build/linux-x86_64/release
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${RUNTIME_DIR}
export SAMPLE=${RUNTIME_DIR}/${1}
pushd "$SCRIPT_DIR" > /dev/null

if [ ! -f "${SAMPLE}" ]; then
    echo "<${SAMPLE}> does not exist, run one of the existing samples, eg. './run.sh createStage': "
    echo " createStage"
    echo " createCameras"
    echo " createLights"
    echo " createMesh"
    echo " createMaterials"
    echo " createReferences"
    echo " createSkeleton"
    echo " createTransforms"
    echo " setDisplayNames"
    popd > /dev/null
    exit 3
fi

${SAMPLE} "${@:2}"
popd > /dev/null
