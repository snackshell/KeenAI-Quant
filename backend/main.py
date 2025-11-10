"""
KeenAI-Quant Backend API
FastAPI application for trading system control and monitoring
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from backend.api.routes import trading, agents, data, performance, chat
from backend.websocket.routes import websocket_router
from backend.config import Config

# Load configuration
config = Config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("🚀 Starting KeenAI-Quant Backend API...")
    print(f"   Environment: {config.get('environment', 'development')}")
    print(f"   Trading pairs: {', '.join(config.trading.pairs)}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down KeenAI-Quant Backend API...")


# Create FastAPI app
app = FastAPI(
    title="KeenAI-Quant API",
    description="AI-Powered Quantitative Trading System for 4 Pairs",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration - Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(data.router, prefix="/api/data", tags=["Market Data"])
app.include_router(performance.router, prefix="/api/performance", tags=["Performance"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

# Import backtest router
from backend.api.routes import backtest
app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtesting"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KeenAI-Quant API",
        "version": "0.1.0",
        "status": "running",
        "pairs": config.trading.pairs
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-11-09T00:00:00Z"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
