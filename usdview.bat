@echo off

setlocal

set USDVIEW_SCRIPT=%~dp0_build\target-deps\usd\release\scripts\usdview_gui.bat

if not exist "%USDVIEW_SCRIPT%" (
    echo "%USDVIEW_SCRIPT%" does not exist, run "repo build" to fetch the USD libraries.
    exit /b 3
)
start "" /B "%USDVIEW_SCRIPT%" %*
