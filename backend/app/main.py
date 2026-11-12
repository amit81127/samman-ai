"""
SAMAAN AI — FastAPI Application Entry Point
==========================================
Initialises the FastAPI app, registers middleware, CORS, routers, and
startup/shutdown lifecycle hooks.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.logging import setup_logging
from app.integrations.gnani.client import close_gnani_clients
from app.api.v1.router import api_router
from app.integrations.llm.metrics import llm_metrics
from app.middleware.http_performance import (
    HTTPPerformanceMiddleware,
    SelectiveGZipMiddleware,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    setup_logging()
    await connect_to_mongo()

    worker_task = None
    worker_stop_event = asyncio.Event()
    if settings.WORKER_ENABLED:
        from app.core.database import get_database
        from app.workers.job_worker import JobWorker
        try:
            db = get_database()
            worker = JobWorker(db)
            worker_task = asyncio.create_task(worker.run_loop(worker_stop_event))
        except Exception as w_exc:
            import logging
            logging.getLogger("samaan.worker").warning("Embedded worker failed to start: %s", w_exc)

    yield

    if worker_task:
        worker_stop_event.set()
        try:
            await asyncio.wait_for(worker_task, timeout=5.0)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            worker_task.cancel()

    await close_gnani_clients()
    await close_mongo_connection()


app = FastAPI(
    title="SAMAAN AI API",
    description="Assistive & Augmentative Communication platform backend",
    version="1.0.0",
    docs_url="/docs" if settings.APP_DEBUG else None,
    redoc_url="/redoc" if settings.APP_DEBUG else None,
    openapi_url="/openapi.json" if settings.APP_DEBUG else None,
    lifespan=lifespan,
)

# ── HTTP Performance & Compression Middleware ─────────────────────────────
# 1. Innermost: Selective GZip Compression (level 5, min 500 bytes, skips audio/images)
app.add_middleware(
    SelectiveGZipMiddleware,
    minimum_size=500,
    compresslevel=5,
)

# 2. Middle: HTTP Timing, Structured Logging & Cache Control Headers
app.add_middleware(HTTPPerformanceMiddleware)

# 3. Outermost: CORS Handling (handles preflights immediately, wraps all outgoing responses)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_allowed_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,  # Required for HttpOnly cookie auth and Bearer headers
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=[
        "X-Speech-Job-Id",
        "Content-Disposition",
        "Content-Length",
        "Server-Timing",
        "X-Process-Time",
    ],
    max_age=86400,
)

# ── API Routers ───────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {"message": "SAMAAN AI API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Root"], include_in_schema=False)
async def root_health():
    """Operational health check endpoint for cloud platforms (Render, Railway)."""
    from app.core.database import get_database
    try:
        db = get_database()
        await db.command("ping")
        return {"status": "healthy", "database": "connected", "version": "1.0.0"}
    except Exception as exc:
        return Response(
            content='{"status":"unhealthy","database":"disconnected"}',
            status_code=503,
            media_type="application/json",
        )


@app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
async def metrics():
    """Prometheus exposition format metrics for system, HTTP, cache, and LLM telemetry."""
    from app.core.monitoring import system_metrics
    sys_content = system_metrics.generate_prometheus_metrics()
    llm_content = llm_metrics.generate_prometheus_metrics()
    combined = sys_content + "\n" + llm_content
    return Response(content=combined, media_type="text/plain")


@app.get("/health/detailed", tags=["Monitoring"])
async def detailed_health():
    """Real-time production dashboard metrics (P50/P95/P99 latencies, cache, CPU, memory)."""
    from app.core.monitoring import system_metrics
    from app.core.database import get_database
    db_connected = False
    try:
        db = get_database()
        await db.command("ping")
        db_connected = True
    except Exception:
        pass

    telemetry = system_metrics.get_system_metrics()
    telemetry["status"] = "healthy" if db_connected else "degraded"
    telemetry["database"] = "connected" if db_connected else "disconnected"
    return telemetry
