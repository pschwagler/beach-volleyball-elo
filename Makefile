.PHONY: help install dev dev-backend watch build start clean test

help:
	@echo "Beach Volleyball ELO - Available Commands:"
	@echo ""
	@echo "  make install      - Install all dependencies (Python + Frontend)"
	@echo "  make dev          - Start backend + frontend watch"
	@echo "  make dev-backend  - Start backend only"
	@echo "  make watch        - Watch and rebuild frontend only"
	@echo "  make build        - Build frontend for production"
	@echo "  make start        - Build frontend + start backend"
	@echo "  make clean        - Remove build artifacts and database"
	@echo "  make test         - Run tests"
	@echo ""
	@echo "Quick Start:"
	@echo "  make dev          → Visit http://localhost:8000 and code!"
	@echo ""

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

dev:
	@echo "🚀 Starting backend + frontend watch in parallel..."
	@echo "📡 Backend: http://localhost:8000 (auto-reload)"
	@echo "🎨 Frontend: auto-rebuilding on file changes"
	@echo ""
	@echo "Press Ctrl+C to stop both"
	@echo ""
	@trap 'kill 0' EXIT; \
	(cd frontend && npm run build -- --watch) & \
	uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

dev-backend:
	@echo "Starting backend only with auto-reload..."
	@echo "Visit: http://localhost:8000"
	uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

watch:
	@echo "Watching frontend files and rebuilding on changes..."
	@echo "Backend must be running (make dev-backend in another terminal)"
	@echo "Visit: http://localhost:8000 (refresh browser after changes)"
	cd frontend && npm run build -- --watch

build:
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "✅ Frontend built!"

start: build
	@echo "Starting production server..."
	uvicorn backend.api.main:app --host 0.0.0.0 --port 8000

clean:
	@echo "Cleaning up..."
	rm -rf backend/database/volleyball.db
	rm -rf frontend/dist
	rm -rf **/__pycache__
	rm -rf backend/**/__pycache__
	@echo "✅ Cleanup complete!"

test:
	@echo "Running tests..."
	python3 -m pytest

