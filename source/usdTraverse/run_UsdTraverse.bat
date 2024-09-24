@echo off

setlocal

set RUNTIME_PATH=usdex/windows-x86_64/release
set PATH=%RUNTIME_PATH%/lib;%PATH%
x64\release\UsdTraverse.exe %*
