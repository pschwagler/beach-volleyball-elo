#!/bin/sh
set -e

echo "==================================="
echo "ENTRYPOINT SCRIPT IS RUNNING"
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la
echo "Python version:"
python --version
echo "Uvicorn location:"
which uvicorn
echo "==================================="

echo "Starting uvicorn on port 8000..."
uvicorn api:app --host 0.0.0.0 --port 8000

