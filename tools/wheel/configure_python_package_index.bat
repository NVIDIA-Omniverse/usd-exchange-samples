@echo off
rem SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
rem SPDX-License-Identifier: MIT

rem Configure pip and uv from one tool-neutral setting.
set "_USDEX_INDEX_FILE=%~dp0..\ci\python-package-index-url.txt"

if not defined USDEX_PYPI_EXTRA_INDEX_URL if exist "%_USDEX_INDEX_FILE%" set /p USDEX_PYPI_EXTRA_INDEX_URL=<"%_USDEX_INDEX_FILE%"

if defined USDEX_PYPI_EXTRA_INDEX_URL (
    if not defined PIP_EXTRA_INDEX_URL set "PIP_EXTRA_INDEX_URL=%USDEX_PYPI_EXTRA_INDEX_URL%"
    if not defined UV_EXTRA_INDEX_URL set "UV_EXTRA_INDEX_URL=%USDEX_PYPI_EXTRA_INDEX_URL%"
)

set "_USDEX_INDEX_FILE="
