#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Assemble the OpenUSD Exchange SDK + OpenUSD runtime and build the C++ samples against it with plain CMake.
# The SDK is consumed via find_package(usdex).
#
#   -d, --debug     build the debug config (default is release)
#   -x, --rebuild   wipe _build and _install (re-fetches deps), then build
#       --clean     wipe _build and _install, then exit
#       --generate  configure only, emitting compile_commands.json (no compile)
#   -h, --help      show this help and exit
#
# To develop against a local SDK build, use `./repo.sh source link <usd-exchange-package-name> <path-to-built-sdk-configuration>`
# so it resolves like any other packman package.

set -e
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
source "$SCRIPT_DIR/tools/wheel/configure_python_package_index.sh"
if [[ -n "${UV_EXTRA_INDEX_URL:-}" ]]; then
    echo "Using UV_EXTRA_INDEX_URL: ${UV_EXTRA_INDEX_URL}"
fi
cd "$SCRIPT_DIR"

CONFIG="release"
CMAKE_CONFIG="Release"
CLEAN=0
REBUILD=0
GENERATE=0
usage() {
    cat <<'EOF'
Build the OpenUSD Exchange SDK C++ samples against the SDK package (find_package(usdex)).

Usage: ./build.sh [options]
  -d, --debug     build the debug config (default is release)
  -x, --rebuild   wipe _build and _install (re-fetches deps), then build
      --clean     wipe _build and _install, then exit
      --generate  configure only, emitting compile_commands.json (no compile)
  -h, --help      show this help and exit
EOF
}
for arg in "$@"; do
    case "$arg" in
        -d|--debug) CONFIG="debug"; CMAKE_CONFIG="Debug" ;;
        -x|--rebuild) REBUILD=1 ;;
        --clean) CLEAN=1 ;;
        --generate) GENERATE=1 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "build.sh: unknown argument '$arg'" >&2; usage >&2; exit 2 ;;
    esac
done
PLATFORM="linux-$(uname -m)"

# -x/--rebuild wipes the build outputs then builds; --clean wipes and exits
if [ "$CLEAN" = 1 ] || [ "$REBUILD" = 1 ]; then
    echo "Cleaning _build and _install"
    rm -rf "$SCRIPT_DIR/_build" "$SCRIPT_DIR/_install"
    [ "$CLEAN" = 1 ] && exit 0
fi

# Bootstrap the SDK package so its shipped repo tools (fetch_deps, install_usdex) become available. The package
# version embeds the abi-tagged platform, so resolve that token for this one initial packman pull.
PLATFORM_TARGET_ABI="manylinux_2_35_$(uname -m)"
tools/packman/packman pull deps/target-deps.packman.xml -p "$PLATFORM_TARGET_ABI" \
    -t config="$CONFIG" -t platform_target_abi="$PLATFORM_TARGET_ABI" -t platform_host="$PLATFORM"
# Fetch every dependency (OpenUSD, cxxopts, ...) via the SDK's shipped tool, then assemble the runtime.
./repo.sh fetch_deps -c "$CONFIG"
./repo.sh install_usdex -c "$CONFIG" --install-rtx --install-python-libs --install-test \
    --install-extra-plugins usdSemantics --staging-dir _build --install-dir "_install/$PLATFORM/$CONFIG"
SDK_ROOT="$SCRIPT_DIR/_build/target-deps/usd-exchange/$CONFIG"
USD_ROOT="$SCRIPT_DIR/_build/target-deps/usd/$CONFIG"
TBB_ROOT="$SCRIPT_DIR/_build/target-deps/tbb/$CONFIG"
MATERIALX_ROOT="$SCRIPT_DIR/_build/target-deps/materialx/$CONFIG"
PYTHON_ROOT="$SCRIPT_DIR/_build/target-deps/python"
CXXOPTS_INCLUDE_DIR="$SCRIPT_DIR/_build/target-deps/cxxopts/include"
RUNTIME_DIR="$SCRIPT_DIR/_install/$PLATFORM/$CONFIG"

BUILD_DIR="_build/cmake/$PLATFORM/$CONFIG"
# prefer the packman-provided host cmake (fetched by fetch_deps into _build/host-deps); fall back to a system cmake
CMAKE="$SCRIPT_DIR/_build/host-deps/cmake/bin/cmake"
if [ -f "$CMAKE" ]; then
    chmod u+x "$CMAKE"  # packman zip extraction can drop the executable bit
else
    CMAKE="cmake"
fi
# CMAKE_EXPORT_COMPILE_COMMANDS emits compile_commands.json for IDEs and CI code-analysis tools.
"$CMAKE" -S "$SCRIPT_DIR" -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE="$CMAKE_CONFIG" \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_PREFIX_PATH="$SDK_ROOT" \
    -DUSDEX_USD_ROOT="$USD_ROOT" \
    -DUSDEX_TBB_ROOT="$TBB_ROOT" \
    -DUSDEX_MATERIALX_ROOT="$MATERIALX_ROOT" \
    -DUSDEX_PYTHON_ROOT="$PYTHON_ROOT" \
    -DSAMPLES_CXXOPTS_INCLUDE_DIR="$CXXOPTS_INCLUDE_DIR" \
    -DUSDEX_SAMPLES_RUNTIME_DIR="$RUNTIME_DIR"

# --generate stops after configure (compile_commands.json is already written); skip the compile
if [ "$GENERATE" = 1 ]; then
    echo "Generated compile_commands.json in: $BUILD_DIR"
    exit 0
fi

BUILD_JOBS="${CMAKE_BUILD_PARALLEL_LEVEL:-${OMNI_REPO_BUILD_JOBS:-$(nproc)}}"
"$CMAKE" --build "$BUILD_DIR" --parallel "$BUILD_JOBS"

echo "Samples built into: $RUNTIME_DIR"
