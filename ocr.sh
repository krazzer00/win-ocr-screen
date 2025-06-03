#!/bin/bash
# Use environment variables if provided
cd "${OCR_WORKDIR:-$(dirname "$0")}"
"${PYTHON_EXECUTABLE:-python}" starter.py
