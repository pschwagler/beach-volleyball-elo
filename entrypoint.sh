#!/bin/sh
set -e

echo "Starting Beach Volleyball ELO API on port 8000..."
exec uvicorn api:app --host 0.0.0.0 --port 8000

