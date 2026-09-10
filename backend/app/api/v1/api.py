"""Unified V1 Router combining all endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    audit,
    claims,
    cleanup,
    health,
    ingest,
    matches,
    notifications,
    queue,
    settings,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(health.portals_router, prefix="/portals", tags=["Portals"])
api_router.include_router(claims.router, prefix="/claims", tags=["Claims"])
api_router.include_router(queue.router, prefix="/queue", tags=["Queue Orchestration"])
api_router.include_router(matches.router, prefix="/matches", tags=["Fuzzy Matching"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["Data Ingestion"])
api_router.include_router(settings.router, prefix="/settings", tags=["System Settings"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(cleanup.router)


