@echo off
setlocal
cd "%OCR_WORKDIR%" || cd "%~dp0"
set "PYTHON_EXE=%PYTHON_EXECUTABLE%"
if "%PYTHON_EXE%"=="" set "PYTHON_EXE=python"
%PYTHON_EXE% starter.py
