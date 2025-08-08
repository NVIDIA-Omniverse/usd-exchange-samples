@echo off

setlocal enabledelayedexpansion

pushd "%~dp0"

set ROOT_DIR=%~dp0

set RUNTIME_DIR=%ROOT_DIR%_build\windows-x86_64\release
set PYTHONHOME=%RUNTIME_DIR%\python-runtime
set PYTHON=%PYTHONHOME%\python.exe

set PATH=%PATH%;%PYTHONHOME%;
set PYTHONPATH=%RUNTIME_DIR%\python;%RUNTIME_DIR%\bindings-python;source

if not exist "%PYTHON%" (
    echo Python, USD, and Omniverse dependencies are missing.  Run "repo.bat build" to configure them.
    popd
    exit /b
)

:: Read samples from allSamples.txt
set SAMPLES=
for /f "usebackq delims=" %%i in ("%SCRIPT_DIR%allSamples.txt") do (
    set SAMPLES=!SAMPLES! %%i
)

:: Check if user wants to run all samples
if "%1"=="all" (
    echo Running all samples in order...

    :: capture the remaining args in `scriptArgs`
    if not "%~2"=="" (
        for /f "usebackq tokens=1*" %%i in (`echo %*`) DO @ set scriptArgs=%%j
    )

    for %%s in (%SAMPLES%) do (
        echo.
        echo === Running %%s ===
        set SAMPLE_PATH=source\%%s\%%s.py
        if exist "!SAMPLE_PATH!" (
            "%PYTHON%" -s "!SAMPLE_PATH!" !scriptArgs!
        ) else (
            echo WARNING: %%s not found at !SAMPLE_PATH!
        )
    )

    echo.
    echo === All samples completed ===
    popd
    exit /b 0
)

"%PYTHON%" -s %*

popd

EXIT /B %ERRORLEVEL%
