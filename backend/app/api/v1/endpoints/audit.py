"""FastAPI route handlers for querying and exporting audit logs."""

import csv
import io
import json
import logging
from datetime import UTC, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogResponse,
    AuditLogStatsResponse,
)

logger = logging.getLogger("uaic_orchestrator.api.audit")
router = APIRouter()


def _build_audit_filter_query(
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    claim_number: str | None = None,
    user_id: str | None = None,
    status_filter: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
):
    """Build SQLAlchemy filter expressions for audit logs."""
    filters = []

    if action:
        actions = [a.strip().upper() for a in action.split(",") if a.strip()]
        if len(actions) == 1:
            filters.append(AuditLog.action == actions[0])
        elif len(actions) > 1:
            filters.append(AuditLog.action.in_(actions))

    if entity_type:
        types = [t.strip().upper() for t in entity_type.split(",") if t.strip()]
        expanded_types = set()
        for t in types:
            if t in ("MATCH_PAIR", "MATCH"):
                expanded_types.add("MATCH")
                expanded_types.add("MATCH_PAIR")
            elif t == "SETTINGS":
                expanded_types.add("SETTINGS")
                expanded_types.add("BRANDING")
            else:
                expanded_types.add(t)
        if len(expanded_types) == 1:
            filters.append(AuditLog.entity_type == list(expanded_types)[0])
        elif len(expanded_types) > 1:
            filters.append(AuditLog.entity_type.in_(list(expanded_types)))

    if entity_id:
        filters.append(AuditLog.entity_id == entity_id)
    if claim_number:
        filters.append(AuditLog.claim_number.ilike(f"%{claim_number.strip()}%"))
    if user_id:
        filters.append(
            or_(
                AuditLog.user_id.ilike(f"%{user_id.strip()}%"),
                AuditLog.user_email.ilike(f"%{user_id.strip()}%"),
            )
        )
    if status_filter:
        statuses = [s.strip().upper() for s in status_filter.split(",") if s.strip()]
        expanded_statuses = set()
        for s in statuses:
            if s in ("FAILED", "FAILURE", "ERROR"):
                expanded_statuses.add("FAILED")
                expanded_statuses.add("FAILURE")
                expanded_statuses.add("ERROR")
            else:
                expanded_statuses.add(s)
        if len(expanded_statuses) == 1:
            filters.append(AuditLog.status == list(expanded_statuses)[0])
        elif len(expanded_statuses) > 1:
            filters.append(AuditLog.status.in_(list(expanded_statuses)))

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            filters.append(AuditLog.timestamp >= dt_from)
        except Exception:
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            # If time is 00:00:00, extend to end of day
            if dt_to.time() == time(0, 0, 0):
                dt_to = datetime.combine(dt_to.date(), time(23, 59, 59, 999999))
            filters.append(AuditLog.timestamp <= dt_to)
        except Exception:
            pass

    if search:
        s = f"%{search.strip()}%"
        filters.append(
            or_(
                func.coalesce(AuditLog.description, "").ilike(s),
                func.coalesce(AuditLog.claim_number, "").ilike(s),
                func.coalesce(AuditLog.action, "").ilike(s),
                func.coalesce(AuditLog.entity_type, "").ilike(s),
                func.coalesce(AuditLog.user_id, "").ilike(s),
                func.coalesce(AuditLog.user_email, "").ilike(s),
                func.coalesce(AuditLog.ip_address, "").ilike(s),
                func.coalesce(AuditLog.entity_id, "").ilike(s),
            )
        )

    return filters


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=500, description="Items per page"),
    action: str | None = Query(None, description="Filter by action"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: str | None = Query(None, description="Filter by entity ID"),
    claim_number: str | None = Query(None, description="Filter by claim number"),
    user_id: str | None = Query(None, description="Filter by operator username or email"),
    status: str | None = Query(None, description="Filter by status (SUCCESS, FAILURE, etc.)"),
    date_from: str | None = Query(None, description="Start date ISO string"),
    date_to: str | None = Query(None, description="End date ISO string"),
    search: str | None = Query(None, description="Search keyword"),
    sort_by: str = Query("timestamp", description="Column to sort by: timestamp, action, entity_type, status, user_id, claim_number"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    db: AsyncSession = Depends(get_db),
) -> AuditLogListResponse:
    """List paginated audit log entries with multi-dimensional filtering."""
    filters = _build_audit_filter_query(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        claim_number=claim_number,
        user_id=user_id,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    # Count query
    count_stmt = select(func.count(AuditLog.id))
    if filters:
        count_stmt = count_stmt.where(*filters)
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    # Data query with dynamic sorting
    offset = (page - 1) * page_size
    data_stmt = select(AuditLog)
    if filters:
        data_stmt = data_stmt.where(*filters)

    sort_cols = {
        "timestamp": AuditLog.timestamp,
        "action": AuditLog.action,
        "entity_type": AuditLog.entity_type,
        "status": AuditLog.status,
        "user_id": AuditLog.user_id,
        "claim_number": AuditLog.claim_number,
    }
    target_col = sort_cols.get((sort_by or "timestamp").lower(), AuditLog.timestamp)
    order_clause = target_col.asc() if (sort_dir or "desc").lower() == "asc" else target_col.desc()
    data_stmt = data_stmt.order_by(order_clause).offset(offset).limit(page_size)

    res = await db.execute(data_stmt)
    items = res.scalars().all()
    total_pages = max(1, (total + page_size - 1) // page_size)

    return AuditLogListResponse(
        items=[AuditLogResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=AuditLogStatsResponse)
async def get_audit_log_stats(
    db: AsyncSession = Depends(get_db),
) -> AuditLogStatsResponse:
    """Retrieve high-level KPI metrics and distributions across audit events."""
    # Total count
    total_stmt = select(func.count(AuditLog.id))
    total_events = (await db.execute(total_stmt)).scalar() or 0

    # Today count
    today_start = datetime.combine(datetime.now(UTC).date(), time(0, 0, 0))
    today_stmt = select(func.count(AuditLog.id)).where(AuditLog.timestamp >= today_start)
    total_today = (await db.execute(today_stmt)).scalar() or 0

    # Counts by action
    action_stmt = select(AuditLog.action, func.count(AuditLog.id)).group_by(AuditLog.action)
    action_rows = (await db.execute(action_stmt)).all()
    by_action = {row[0]: row[1] for row in action_rows}

    # Counts by entity type
    entity_stmt = select(AuditLog.entity_type, func.count(AuditLog.id)).group_by(AuditLog.entity_type)
    entity_rows = (await db.execute(entity_stmt)).all()
    by_entity = {row[0]: row[1] for row in entity_rows}

    # Counts by status
    status_stmt = select(AuditLog.status, func.count(AuditLog.id)).group_by(AuditLog.status)
    status_rows = (await db.execute(status_stmt)).all()
    by_status = {row[0]: row[1] for row in status_rows}

    total_failures = by_status.get("FAILURE", 0) + by_status.get("FAILED", 0)
    total_claims_ops = by_entity.get("CLAIM", 0)
    total_settings_ops = by_entity.get("SETTINGS", 0) + by_entity.get("BRANDING", 0)
    total_match_reviews = by_entity.get("MATCH", 0)

    return AuditLogStatsResponse(
        total_events=total_events,
        total_today=total_today,
        total_claims_ops=total_claims_ops,
        total_settings_ops=total_settings_ops,
        total_match_reviews=total_match_reviews,
        total_failures=total_failures,
        by_action=by_action,
        by_entity_type=by_entity,
        by_status=by_status,
    )


@router.get("/export")
async def export_audit_logs(
    format: str = Query("csv", pattern="^(csv|json|xlsx|pdf)$", description="Export format: csv, json, xlsx, or pdf"),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    entity_id: str | None = Query(None),
    claim_number: str | None = Query(None),
    status: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    search: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export filtered audit logs in CSV, JSON, or Excel format for compliance audits."""
    filters = _build_audit_filter_query(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        claim_number=claim_number,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )

    data_stmt = select(AuditLog)
    if filters:
        data_stmt = data_stmt.where(*filters)
    data_stmt = data_stmt.order_by(AuditLog.timestamp.desc()).limit(5000)

    items = (await db.execute(data_stmt)).scalars().all()
    filename_ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if format == "json":
        data = [
            AuditLogResponse.model_validate(item).model_dump(mode="json")
            for item in items
        ]
        content = json.dumps(data, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="audit_logs_{filename_ts}.json"'
            },
        )

    if format == "xlsx":
        import pandas as pd
        rows = [
            {
                "ID": item.id,
                "Timestamp (UTC)": item.timestamp.isoformat() if item.timestamp else "",
                "User ID": item.user_id,
                "User Email": item.user_email,
                "IP Address": item.ip_address or "",
                "Action": item.action,
                "Entity Type": item.entity_type,
                "Entity ID": item.entity_id or "",
                "Claim Number": item.claim_number or "",
                "Status": item.status,
                "Description": item.description,
                "Details (JSON)": json.dumps(item.details) if item.details else "",
            }
            for item in items
        ]
        df = pd.DataFrame(rows)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Audit Trail")
        out.seek(0)
        return Response(
            content=out.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="audit_logs_{filename_ts}.xlsx"'
            },
        )

    if format == "pdf":
        import asyncio
        try:
            pdf_bytes = await asyncio.to_thread(_render_audit_pdf_sync, items)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="audit_logs_{filename_ts}.pdf"',
                    "Content-Length": str(len(pdf_bytes)),
                },
            )
        except Exception as e:
            logger.error(f"Error generating audit PDF: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate audit PDF report: {e}",
            )

    # Default CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Timestamp (UTC)",
            "User ID",
            "User Email",
            "IP Address",
            "Action",
            "Entity Type",
            "Entity ID",
            "Claim Number",
            "Status",
            "Description",
            "Details (JSON)",
        ]
    )

    for item in items:
        writer.writerow(
            [
                item.id,
                item.timestamp.isoformat() if item.timestamp else "",
                item.user_id,
                item.user_email,
                item.ip_address or "",
                item.action,
                item.entity_type,
                item.entity_id or "",
                item.claim_number or "",
                item.status,
                item.description,
                json.dumps(item.details) if item.details else "",
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="audit_logs_{filename_ts}.csv"'
        },
    )


def _render_audit_pdf_sync(items: list) -> bytes:
    """Render authentic PDF document from audit items using Playwright."""
    from playwright.sync_api import sync_playwright

    rows_html = "".join(
        f"<tr>"
        f"<td style='white-space:nowrap;font-family:monospace;'>{item.timestamp.strftime('%Y-%m-%d %H:%M:%S') if item.timestamp else '-'}</td>"
        f"<td><span style='background:#e0e7ff;color:#3730a3;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:9px;font-weight:600;'>{item.action}</span></td>"
        f"<td><strong>{item.entity_type}</strong></td>"
        f"<td style='font-family:monospace;'>{item.claim_number or item.entity_id or '-'}</td>"
        f"<td>{item.user_email or item.user_id}</td>"
        f"<td style='font-weight:600;color:{'#15803d' if item.status == 'SUCCESS' else '#b91c1c'};'>{item.status}</td>"
        f"<td>{item.description or ''}</td>"
        f"</tr>"
        for item in items
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>UAIC Audit Trail & Compliance Ledger</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 15px; font-size: 10px; color: #1e293b; line-height: 1.4; }}
  h1 {{ font-size: 16px; margin: 0 0 4px 0; color: #0f172a; }}
  .meta {{ font-size: 9px; color: #64748b; margin-bottom: 12px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  th {{ background: #f1f5f9; text-align: left; padding: 5px 6px; font-weight: 600; font-size: 9px; text-transform: uppercase; border-bottom: 2px solid #cbd5e1; }}
  td {{ padding: 5px 6px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
</style>
</head>
<body>
  <h1>UAIC Claim & RPA Orchestrator — Audit Trail & Provenance Ledger</h1>
  <div class="meta">Generated on {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')} • Total Filtered Records: {len(items)} • Compliance & Governance Standard §73</div>
  <table>
    <thead>
      <tr>
        <th>Timestamp (UTC)</th>
        <th>Action</th>
        <th>Entity</th>
        <th>Target</th>
        <th>Operator</th>
        <th>Status</th>
        <th>Description</th>
      </tr>
    </thead>
    <tbody>
      {rows_html if rows_html else "<tr><td colspan='7' style='text-align:center;padding:20px;color:#94a3b8;'>No audit records found</td></tr>"}
    </tbody>
  </table>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        pdf_bytes = page.pdf(
            format="A4",
            landscape=True,
            print_background=True,
            margin={"top": "8mm", "bottom": "8mm", "left": "8mm", "right": "8mm"},
        )
        browser.close()
        return pdf_bytes


@router.get("/{id}", response_model=AuditLogResponse)
async def get_audit_log_detail(
    id: str,
    db: AsyncSession = Depends(get_db),
) -> AuditLogResponse:
    """Retrieve details of a single audit log event."""
    stmt = select(AuditLog).where(AuditLog.id == id)
    res = await db.execute(stmt)
    entry = res.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit log entry '{id}' not found.",
        )
    return AuditLogResponse.model_validate(entry)
