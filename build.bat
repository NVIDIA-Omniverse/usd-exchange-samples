:: SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
:: SPDX-License-Identifier: MIT
::
:: Assemble the OpenUSD Exchange SDK + OpenUSD runtime and build the C++ samples against it with plain CMake.
:: The SDK is consumed via find_package(usdex).
::
::   -d, --debug     build the debug config (default is release)
::   -x, --rebuild   wipe _build and _install (re-fetches deps), then build
::       --clean     wipe _build and _install, then exit
::       --generate  configure only, emitting compile_commands.json (no compile)
::   -h, --help      show this help and exit
::
:: To develop against a local SDK build, use `repo.bat source link <usd-exchange-package-name> <path-to-built-sdk-configuration>`
:: so it resolves like any other packman package.
@echo off
setlocal enabledelayedexpansion
pushd "%~dp0"
call tools\wheel\configure_python_package_index.bat
if defined UV_EXTRA_INDEX_URL echo Using UV_EXTRA_INDEX_URL: !UV_EXTRA_INDEX_URL!

set "CONFIG=release"
set "CMAKE_CONFIG=Release"
set "CLEAN=0"
set "REBUILD=0"
set "GENERATE=0"
:parseargs
if "%~1"=="" goto :parsed
if /i "%~1"=="-h" goto :usage
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="-d" (set "CONFIG=debug" & set "CMAKE_CONFIG=Debug" & shift & goto :parseargs)
if /i "%~1"=="--debug" (set "CONFIG=debug" & set "CMAKE_CONFIG=Debug" & shift & goto :parseargs)
if /i "%~1"=="-x" (set "REBUILD=1" & shift & goto :parseargs)
if /i "%~1"=="--rebuild" (set "REBUILD=1" & shift & goto :parseargs)
if /i "%~1"=="--clean" (set "CLEAN=1" & shift & goto :parseargs)
if /i "%~1"=="--generate" (set "GENERATE=1" & shift & goto :parseargs)
echo build.bat: unknown argument "%~1" 1>&2
echo Run "build.bat --help" for usage. 1>&2
popd
exit /b 2
:parsed
set "PLATFORM=windows-x86_64"
rem abi-tagged platform for the bootstrap pull; the OpenUSD/usd-exchange windows packages are built with the v143 toolset
set "PLATFORM_TARGET_ABI=windows_v143_x86_64"

if "%CLEAN%%REBUILD%"=="00" goto :skipclean
echo Cleaning _build and _install
rmdir /s /q _build 2>nul
rmdir /s /q _install 2>nul
if "%CLEAN%"=="1" (popd & exit /b 0)
:skipclean

rem Bootstrap the SDK package so its shipped repo tools (fetch_deps, install_usdex) become available.
call tools\packman\packman pull deps\target-deps.packman.xml -p %PLATFORM_TARGET_ABI% -t config=%CONFIG% -t platform_target_abi=%PLATFORM_TARGET_ABI% -t platform_host=%PLATFORM% || goto :error
rem Fetch every dependency via the SDK's shipped tool, then assemble the runtime.
call repo.bat fetch_deps -c %CONFIG% || goto :error
call repo.bat install_usdex -c %CONFIG% --install-rtx --install-python-libs --install-test --install-extra-plugins usdSemantics --staging-dir _build --install-dir _install\%PLATFORM%\%CONFIG% || goto :error
set "SDK_ROOT=%CD%\_build\target-deps\usd-exchange\%CONFIG%"
set "USD_ROOT=%CD%\_build\target-deps\usd\%CONFIG%"
set "TBB_ROOT=%CD%\_build\target-deps\tbb\%CONFIG%"
set "MATERIALX_ROOT=%CD%\_build\target-deps\materialx\%CONFIG%"
set "PYTHON_ROOT=%CD%\_build\target-deps\python"
set "CXXOPTS_INCLUDE_DIR=%CD%\_build\target-deps\cxxopts\include"
set "RUNTIME_DIR=%CD%\_install\%PLATFORM%\%CONFIG%"

set "BUILD_DIR=_build\cmake\%PLATFORM%\%CONFIG%"
rem prefer the packman-provided host cmake (fetched by fetch_deps into _build\host-deps); fall back to a system cmake
set "CMAKE=%CD%\_build\host-deps\cmake\bin\cmake.exe"
if not exist "%CMAKE%" set "CMAKE=cmake"
rem -T v143 pins the MSVC toolset so the samples link the SDK & OpenUSD with a matching ABI.
rem CMAKE_EXPORT_COMPILE_COMMANDS emits compile_commands.json for IDEs and CI code-analysis tools.
"%CMAKE%" -S "%CD%" -B "%BUILD_DIR%" -T v143 ^
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ^
    -DCMAKE_PREFIX_PATH="%SDK_ROOT%" ^
    -DUSDEX_USD_ROOT="%USD_ROOT%" ^
    -DUSDEX_TBB_ROOT="%TBB_ROOT%" ^
    -DUSDEX_MATERIALX_ROOT="%MATERIALX_ROOT%" ^
    -DUSDEX_PYTHON_ROOT="%PYTHON_ROOT%" ^
    -DSAMPLES_CXXOPTS_INCLUDE_DIR="%CXXOPTS_INCLUDE_DIR%" ^
    -DUSDEX_SAMPLES_RUNTIME_DIR="%RUNTIME_DIR%" || goto :error

rem --generate stops after configure (compile_commands.json is already written); skip the compile
if "%GENERATE%"=="1" (echo Generated compile_commands.json in: %BUILD_DIR% & popd & exit /b 0)

"%CMAKE%" --build "%BUILD_DIR%" --config %CMAKE_CONFIG% --parallel || goto :error

echo Samples built into: %RUNTIME_DIR%
popd
exit /b 0
:usage
echo Build the OpenUSD Exchange SDK C++ samples against the SDK package ^(find_package^(usdex^)^).
echo.
echo Usage: build.bat [options]
echo   -d, --debug     build the debug config ^(default is release^)
echo   -x, --rebuild   wipe _build and _install ^(re-fetches deps^), then build
echo       --clean     wipe _build and _install, then exit
echo       --generate  configure only, emitting compile_commands.json ^(no compile^)
echo   -h, --help      show this help and exit
popd
exit /b 0
:error
popd
exit /b 1
