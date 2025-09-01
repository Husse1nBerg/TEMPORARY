"""
CROPS Price Tracker Backend
FastAPI application for real-time price scraping and monitoring
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import uvicorn
from datetime import datetime

from app.config import settings
from app.database import engine, Base, get_db
from app.api import auth, prices, products, stores, scraper
from app.tasks.celery_app import celery_app
from app.services.price_service import PriceService
from app.scrapers import (
    GourmetScraper,
    RDNAScraper,
    MetroScraper,
    SpinneysScraper,
    RabbitScraper,
    TalabatScraper,
    InstashopScraper,
    BreadfastScraper
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting CROPS Price Tracker Backend...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Initialize scrapers
    logger.info("Initializing scrapers...")
    
    # Start periodic tasks
    from app.tasks.scraping_tasks import setup_periodic_tasks
    setup_periodic_tasks()
    logger.info("Periodic scraping tasks scheduled")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CROPS Price Tracker Backend...")

# Create FastAPI app
app = FastAPI(
    title="CROPS Price Tracker API",
    description="Real-time grocery price tracking and monitoring system",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "CROPS Price Tracker API",
        "version": "1.0.0"
    }

# API status endpoint
@app.get("/api/status", tags=["System"])
async def api_status(db=Depends(get_db)):
    """Get API and database status"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        db_status = "disconnected"
    
    # Check Redis/Celery status
    try:
        celery_status = celery_app.control.inspect().stats()
        worker_status = "active" if celery_status else "inactive"
    except Exception as e:
        logger.error(f"Celery connection error: {e}")
        worker_status = "disconnected"
    
    return {
        "api": "online",
        "database": db_status,
        "worker": worker_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(stores.router, prefix="/api/stores", tags=["Stores"])
app.include_router(prices.router, prefix="/api/prices", tags=["Prices"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["Scraper"])

# WebSocket endpoint for real-time updates
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time price updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )