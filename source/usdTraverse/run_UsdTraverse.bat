@echo off

setlocal

if not defined CONFIG set CONFIG=release
set RUNTIME_PATH=usdex/windows-x86_64/%CONFIG%
set PATH=%RUNTIME_PATH%/bin;%PATH%
x64\%CONFIG%\UsdTraverse.exe %*
