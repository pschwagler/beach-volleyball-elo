#!/bin/sh
echo "=== DEBUG INFO ==="
echo "PORT variable: '${PORT}'"
echo "All environment variables:"
env | grep -i port || echo "No PORT variables found"
echo "=================="

# Use PORT if set, otherwise default to 8000
PORT=${PORT:-8000}
echo "Using port: $PORT"

exec uvicorn api:app --host 0.0.0.0 --port "$PORT"

