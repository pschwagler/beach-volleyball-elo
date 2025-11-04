#!/bin/bash
# Build script for Railway deployment

echo "🔨 Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete! Frontend ready in frontend/dist/"
echo "🚀 You can now deploy to Railway or run locally with: uvicorn api:app"

