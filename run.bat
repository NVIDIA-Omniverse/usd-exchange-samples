@echo off

setlocal enabledelayedexpansion

pushd "%~dp0"

set "SCRIPT_DIR=%~dp0"
if not defined USDEX_SAMPLES_CONFIG set "USDEX_SAMPLES_CONFIG=release"
set "RUNTIME_DIR=%SCRIPT_DIR%_install\windows-x86_64\%USDEX_SAMPLES_CONFIG%"
set "PATH=%RUNTIME_DIR%\bin;%PATH%"

:: Read samples from allSamples.txt
set "SAMPLES="
for /f "usebackq delims=" %%i in ("%SCRIPT_DIR%allSamples.txt") do (
    set "SAMPLES=!SAMPLES! %%i"
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
        set "SAMPLE_PATH=%RUNTIME_DIR%\bin\%%s.exe"
        if exist "!SAMPLE_PATH!" (
            call "!SAMPLE_PATH!" !scriptArgs!
            set "SAMPLE_EXIT_CODE=!ERRORLEVEL!"
            if not "!SAMPLE_EXIT_CODE!"=="0" (
                goto :exit
            )
        ) else (
            echo ERROR: %%s not found at !SAMPLE_PATH!
            set "SAMPLE_EXIT_CODE=3"
            goto :exit
        )
    )

    echo.
    echo === All samples completed ===
    set "SAMPLE_EXIT_CODE=0"
    goto :exit
)

set "SAMPLE=%RUNTIME_DIR%\bin\%1.exe"
if exist "%SAMPLE%" (
    goto :run_sample
)
echo "%SAMPLE%" does not exist, run one of the existing samples, eg. 'run.bat createStage':
echo  all (runs all samples in order)
for %%s in (%SAMPLES%) do (
    echo  %%s
)
set "SAMPLE_EXIT_CODE=3"
goto :exit

:run_sample
:: capture the remaining args in `scriptArgs`
if not "%~2"=="" (
    for /f "usebackq tokens=1*" %%i in (`echo %*`) DO @ set scriptArgs=%%j
)
call "%SAMPLE%" %scriptArgs%
set "SAMPLE_EXIT_CODE=%ERRORLEVEL%"

:exit
popd
exit /b %SAMPLE_EXIT_CODE%
