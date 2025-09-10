"""FastAPI application for Ultimate Trading Solution."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ultimate_trading_solution.core.config import settings
from ultimate_trading_solution.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Ultimate Trading Solution API", version=settings.version)
    
    # TODO: Initialize database, Redis, etc.
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ultimate Trading Solution API")


# Create FastAPI application
app = FastAPI(
    title="Ultimate Trading Solution API",
    description="A comprehensive trading solution with advanced analytics and automation",
    version=settings.version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Ultimate Trading Solution API",
        "version": settings.version,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


# TODO: Add API routes
# from ultimate_trading_solution.api.routes import market, trading, portfolio
# app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
# app.include_router(trading.router, prefix="/api/v1/trading", tags=["trading"])
# app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
