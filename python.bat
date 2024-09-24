@echo off

setlocal

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

"%PYTHON%" -s %*

popd

EXIT /B %ERRORLEVEL%
