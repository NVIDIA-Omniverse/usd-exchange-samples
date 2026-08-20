#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

# Configure pip and uv from one tool-neutral setting.
_USDEX_INDEX_HELPER_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
_USDEX_INDEX_FILE="${_USDEX_INDEX_HELPER_DIR}/../ci/python-package-index-url.txt"

if [[ -z "${USDEX_PYPI_EXTRA_INDEX_URL:-}" && -f "${_USDEX_INDEX_FILE}" ]]; then
    IFS= read -r USDEX_PYPI_EXTRA_INDEX_URL < "${_USDEX_INDEX_FILE}"
fi

if [[ -n "${USDEX_PYPI_EXTRA_INDEX_URL:-}" ]]; then
    export USDEX_PYPI_EXTRA_INDEX_URL
    export PIP_EXTRA_INDEX_URL="${PIP_EXTRA_INDEX_URL:-${USDEX_PYPI_EXTRA_INDEX_URL}}"
    export UV_EXTRA_INDEX_URL="${UV_EXTRA_INDEX_URL:-${USDEX_PYPI_EXTRA_INDEX_URL}}"
fi

unset _USDEX_INDEX_FILE _USDEX_INDEX_HELPER_DIR
