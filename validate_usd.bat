@echo off

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%tools\wheel\configure_python_package_index.bat"
set PYTHONPATH=%SCRIPT_DIR%source\python
set PACKMAN_PYTHON=%SCRIPT_DIR%tools\packman\python.bat
set VENV=%SCRIPT_DIR%_build\usdex_env

if exist "%VENV%" (
    echo Using existing venv: %VENV%
    call "%VENV%\Scripts\activate.bat"
    if %errorlevel% neq 0 ( exit /b %errorlevel% )
) else (
    echo Building venv: %VENV%
    call %PACKMAN_PYTHON% -m venv "%VENV%"
    if %errorlevel% neq 0 ( exit /b %errorlevel% )

    REM Get the usd-exchange version from packman XML
    for /f "delims=" %%i in ('call %PACKMAN_PYTHON% "%SCRIPT_DIR%\tools\wheel\get_usdex_version.py"') do set USDEX_VERSION=%%i

    call "%VENV%\Scripts\activate.bat"
    if %errorlevel% neq 0 ( exit /b %errorlevel% )

    REM Install usd-exchange package and test option to get the usd-validation-nvidia package
    echo Installing usd-exchange wheel version !USDEX_VERSION! from !PIP_EXTRA_INDEX_URL!
    python.exe -m pip install usd-exchange[test]==!USDEX_VERSION!
    if !errorlevel! neq 0 ( exit /b !errorlevel! )
)

python.exe %SCRIPT_DIR%\source\validateUsd\validateUsdBootstrap.py %*

EXIT /B %ERRORLEVEL%
