@echo off

setlocal

pushd "%~dp0"

set SCRIPT_DIR=%~dp0
set RUNTIME_DIR=%SCRIPT_DIR%_build\windows-x86_64\release
set SAMPLE=%RUNTIME_DIR%\%1.exe

if not exist "%SAMPLE%" (
    echo "%SAMPLE%" does not exist, run one of the existing samples, eg. 'run.bat createStage':
    echo  createStage
    echo  createCameras
    echo  createLights
    echo  createMaterials
    echo  createMesh
    echo  createReferences
    echo  createSkeleton
    echo  createTransforms
    echo  setDisplayNames


    popd
    exit /b 3
)

:: capture the remaining args in `scriptArgs`
if not "%~2"=="" (
    for /f "usebackq tokens=1*" %%i in (`echo %*`) DO @ set scriptArgs=%%j
)

call "%SAMPLE%" %scriptArgs%

popd

EXIT /B %ERRORLEVEL%
