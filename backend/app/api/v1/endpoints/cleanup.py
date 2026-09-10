"""API endpoints for the Enterprise Data Cleanup & Retention Engine."""

import logging

from fastapi import APIRouter, HTTPException, Request

from app.schemas.cleanup import (
    CategoryMetadata,
    CleanupExecuteRequest,
    CleanupExecuteResponse,
    CleanupPreviewRequest,
    CleanupPreviewResponse,
)
from app.services.audit_service import extract_client_context
from app.services.cleanup_service import (
    calculate_cleanup_preview,
    execute_enterprise_cleanup,
    get_all_categories_metadata,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cleanup", tags=["Cleanup & Retention"])


@router.get("/categories", response_model=list[CategoryMetadata])
async def list_cleanup_categories():
    """List all available data retention categories with real-time record and file counts."""
    return await get_all_categories_metadata()


@router.post("/preview", response_model=CleanupPreviewResponse)
async def preview_cleanup(request: CleanupPreviewRequest):
    """Calculate affected database records and files for the specified categories and time range without deleting anything."""
    try:
        return await calculate_cleanup_preview(
            categories=request.categories,
            time_scope=request.time_scope,
            n_units=request.n_units,
            start_date=request.start_date,
            end_date=request.end_date,
            before_date=request.before_date,
            after_date=request.after_date,
        )
    except Exception as e:
        logger.error(f"Failed to generate cleanup preview: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to generate preview: {e!s}")


@router.post("/execute", response_model=CleanupExecuteResponse)
async def execute_cleanup(
    payload: CleanupExecuteRequest,
    request: Request = None,
):
    """Execute enterprise cleanup across selected categories and time scopes with transactional safety and audit logging."""
    if not payload.confirmed and not payload.dry_run:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set confirmed=true to permanently delete records.",
        )

    ctx = extract_client_context(request)
    operator = ctx.get("user_email") or ctx.get("user_id") or "API_OPERATOR"

    try:
        res = await execute_enterprise_cleanup(
            categories=payload.categories,
            time_scope=payload.time_scope,
            n_units=payload.n_units,
            start_date=payload.start_date,
            end_date=payload.end_date,
            before_date=payload.before_date,
            after_date=payload.after_date,
            operator=operator,
            dry_run=payload.dry_run,
        )
        return res
    except Exception as e:
        logger.error(f"Cleanup execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup execution failed: {e!s}")
