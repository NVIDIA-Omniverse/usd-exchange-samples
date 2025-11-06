@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set SOURCE_DIR=%SCRIPT_DIR%..\..\source
set PYTHONPATH=%SOURCE_DIR%\python;%SOURCE_DIR%\tests;%PYTHONPATH%

REM Check for --reuse argument and rebuild args without it
set REUSE_VENV=0
set ARGS=
:parse_args
if "%1"=="--reuse" (
    set REUSE_VENV=1
    shift
    goto :parse_args
)
if "%1"=="" goto :done_parsing
set ARGS=!ARGS! %1
shift
goto :parse_args
:done_parsing

echo Running script in "%SCRIPT_DIR%..\.."
pushd "%SCRIPT_DIR%..\.." > nul

REM Setup the build environment
set VENV=.\_build\tests\venv

if %REUSE_VENV%==1 (
    if exist "%VENV%" (
        echo Reusing existing venv: %VENV%
        goto :activate_venv
    ) else (
        echo No existing venv found, creating new one: %VENV%
    )
)

echo Building: %VENV%
if exist "%VENV%" (
    rd /s /q "%VENV%"
)

call %SCRIPT_DIR%..\packman\python.bat -m venv "%VENV%"
if %errorlevel% neq 0 ( exit /b %errorlevel% )

:activate_venv
call "%VENV%\Scripts\activate.bat"
if %errorlevel% neq 0 ( exit /b %errorlevel% )

if %REUSE_VENV%==0 (
    REM Get the usd-exchange version from packman XML
    for /f "delims=" %%i in ('call %SCRIPT_DIR%..\packman\python.bat "%SCRIPT_DIR%get_usdex_version.py"') do set USDEX_VERSION=%%i

    REM Install packages with optional private index
    echo Installing usd-exchange wheel version !USDEX_VERSION! from !PIP_EXTRA_INDEX_URL!
    python.exe -m pip install usd-exchange[test]==!USDEX_VERSION!
    if !errorlevel! neq 0 ( exit /b !errorlevel! )
)

REM Run the tests with the filtered arguments
python.exe -m unittest discover -v -s source\tests !ARGS!
if !errorlevel! neq 0 ( exit /b !errorlevel! )

endlocal
