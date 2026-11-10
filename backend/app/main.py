"""
SAMAAN AI — FastAPI Application Entry Point
==========================================
Initialises the FastAPI app, registers middleware, CORS, routers, and
startup/shutdown lifecycle hooks.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.logging import setup_logging
from app.integrations.gnani.client import close_gnani_clients
from app.api.v1.router import api_router
from app.integrations.llm.metrics import llm_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    setup_logging()
    await connect_to_mongo()
    yield
    await close_gnani_clients()
    await close_mongo_connection()


app = FastAPI(
    title="SAMAAN AI API",
    description="Assistive & Augmentative Communication platform backend",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# ── CORS Middleware ───────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # Required for HttpOnly cookie auth
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {"message": "SAMAAN AI API", "version": "1.0.0", "docs": "/docs"}


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def metrics():
    """Prometheus exposition format metrics for Gemini LLM and system performance."""
    content = llm_metrics.generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain")
