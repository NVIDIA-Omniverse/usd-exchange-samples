@echo off

setlocal

set SCRIPT_DIR=%~dp0
set USD_INSTALL_DIR=%SCRIPT_DIR%_build\target-deps\usd\release
set USDVIEW_SCRIPT=%USD_INSTALL_DIR%\scripts\usdview_gui.bat
set USDVIEW_VENV=%SCRIPT_DIR%_build\usdview_venv

if not exist "%USDVIEW_SCRIPT%" (
    echo %USDVIEW_SCRIPT% does not exist, run "repo.bat build" to fetch the USD libraries.
    exit /b 3
)

if exist "%USDVIEW_VENV%" (
    echo Using existing venv: %USDVIEW_VENV%
    call %USDVIEW_VENV%\Scripts\activate.bat
) else (
    echo Building venv: %USDVIEW_VENV%
    call .\python.bat -m venv "%USDVIEW_VENV%"
    call "%USDVIEW_VENV%\Scripts\activate.bat"
    call python.exe -m pip install -r %USD_INSTALL_DIR%\requirements.txt
)

%USDVIEW_SCRIPT% %*
