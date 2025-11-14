"""
Beach Volleyball ELO API Server

FastAPI server that provides REST endpoints for ELO calculations and statistics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.api.routes import router
from backend.database import db
from backend.services import data_service, sheets_service, calculation_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Beach Volleyball ELO API",
    description="API for calculating and retrieving beach volleyball ELO ratings and statistics",
    version="2.0.0"
)

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Set limiter in router module so routes can use it
from backend.api import routes
routes.limiter = limiter


@app.on_event("startup")
async def startup_event():
    """Initialize database and auto-populate if empty."""
    logger.info("Starting up Beach Volleyball ELO API...")
    
    # Initialize database (create tables if they don't exist)
    db.init_database()
    logger.info("Database initialized")
    
    # Auto-populate if database is empty
    if data_service.is_database_empty():
        logger.info("Database is empty, auto-populating from Google Sheets...")
        try:
            match_list = sheets_service.load_matches_from_sheets()
            tracker = calculation_service.process_matches(match_list)
            data_service.flush_and_repopulate(tracker, match_list)
            logger.info(f"Auto-populated with {len(tracker.players)} players and {len(match_list)} matches")
        except Exception as e:
            logger.error(f"Failed to auto-populate database: {str(e)}")
            logger.warning("API will start without data. Use /api/calculate to populate manually.")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the React frontend."""
    try:
        # Try to serve React build first
        with open("frontend/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to simple HTML
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Beach Volleyball ELO</title>
                    <style>
                        body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                        h1 { color: #667eea; }
                        a { color: #667eea; }
                    </style>
                </head>
                <body>
                    <h1>🏐 Beach Volleyball ELO API</h1>
                    <p>API is running successfully!</p>
                    <h2>Available Resources:</h2>
                    <ul>
                        <li><a href="/docs">📚 API Documentation</a> - Interactive API docs</li>
                        <li><a href="/api/health">❤️ Health Check</a> - System status</li>
                    </ul>
                    <p><em>Note: Run frontend build to see the web interface.</em></p>
                </body>
            </html>
        """)


# Mount static assets from React build
try:
    # Mount assets directory
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
except:
    # Assets directory might not exist yet (before build)
    pass


# Serve static files (images, etc.) from dist - must be after all API routes
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files from frontend/dist directory."""
    # Don't serve API routes through this catch-all
    if file_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try to serve the requested file
    full_path = Path(f"frontend/dist/{file_path}")
    if full_path.is_file():
        return FileResponse(full_path)
    
    # If file not found, serve index.html (for React Router)
    return FileResponse("frontend/dist/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

