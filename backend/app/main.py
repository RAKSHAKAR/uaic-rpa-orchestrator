"""FastAPI Main Application Entrypoint."""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# On Windows, Playwright requires ProactorEventLoop for subprocess creation
if sys.platform == "win32":
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db

# Setup logging
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
)

# Route file logs to standardized logs/ directory
possible_log_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs")),
]
log_dir = None
for candidate in possible_log_dirs:
    if os.path.isdir(candidate):
        log_dir = candidate
        break
if not log_dir:
    log_dir = possible_log_dirs[0]
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        pass

if log_dir and os.path.isdir(log_dir):
    try:
        backend_log_file = os.path.join(
            log_dir, f"backend_{datetime.now(UTC).strftime('%Y-%m-%d')}.log"
        )
        file_handler = logging.FileHandler(backend_log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
    except Exception:
        pass

logger = logging.getLogger("uaic_orchestrator")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events with clean connection pool disposal."""
    logger.info("Starting UAIC Claim & RPA Orchestrator Backend (Python 3.14.7)...")
    await init_db()
    logger.info("Database schema initialized successfully.")
    yield
    logger.info("Shutting down UAIC Claim & RPA Orchestrator Backend...")
    from app.core.database import engine, task_engine
    try:
        await engine.dispose()
        await task_engine.dispose()
        logger.info("Database connection pools disposed cleanly.")
    except Exception as e:
        logger.warning(f"Note on DB engine disposal: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Distributed Task Orchestration, RapidFuzz Deduplication, and County Court RPA Platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": False,
        "deepLinking": False,
        "displayRequestDuration": True,
        "tryItOutEnabled": True,
    },
)

# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition", "Content-Length"],
    )

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_PREFIX,
    }
