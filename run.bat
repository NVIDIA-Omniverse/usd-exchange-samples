@echo off

setlocal enabledelayedexpansion

pushd "%~dp0"

set SCRIPT_DIR=%~dp0
set RUNTIME_DIR=%SCRIPT_DIR%_build\windows-x86_64\release

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
        set SAMPLE_PATH=%RUNTIME_DIR%\%%s.exe
        if exist "!SAMPLE_PATH!" (
            call "!SAMPLE_PATH!" !scriptArgs!
        ) else (
            echo WARNING: %%s not found at !SAMPLE_PATH!
        )
    )

    echo.
    echo === All samples completed ===
    popd
    exit /b 0
)

set SAMPLE=%RUNTIME_DIR%\%1.exe
if exist "%SAMPLE%" (
    goto :run_sample
)
echo "%SAMPLE%" does not exist, run one of the existing samples, eg. 'run.bat createStage':
echo  all (runs all samples in order)
for %%s in (%SAMPLES%) do (
    echo  %%s
)
popd
exit /b 3

:run_sample
:: capture the remaining args in `scriptArgs`
if not "%~2"=="" (
    for /f "usebackq tokens=1*" %%i in (`echo %*`) DO @ set scriptArgs=%%j
)
call "%SAMPLE%" %scriptArgs%

popd

EXIT /B %ERRORLEVEL%
