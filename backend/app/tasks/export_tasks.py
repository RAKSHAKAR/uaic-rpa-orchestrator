"""Asynchronous Celery export tasks for large claim datasets (§55).

Generates CSV, Excel (.xlsx), and JSON exports in the background, updates
task execution progress, and persists exports for operator retrieval.
"""

import asyncio
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import desc, or_, select

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord

logger = logging.getLogger("uaic_orchestrator.tasks.export")

EXPORT_DIR = Path("./exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


async def _generate_export_data(
    export_format: str,
    filters: dict[str, Any] | None = None,
    claim_ids: list[str] | None = None,
    task_instance: Any = None,
) -> dict[str, Any]:
    """Execute asynchronous database extraction and format serialization."""
    filters = filters or {}
    export_id = str(uuid.uuid4())
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    async with AsyncSessionLocal() as db:
        query = select(ClaimRecord)

        if claim_ids:
            query = query.where(ClaimRecord.id.in_(claim_ids))
        else:
            status = filters.get("status")
            if status:
                query = query.where(ClaimRecord.record_status == status)

            state = filters.get("state")
            if state:
                query = query.where(
                    or_(
                        ClaimRecord.policy_state == state,
                        ClaimRecord.loss_location_state == state,
                    )
                )

            search = filters.get("search")
            if search:
                pat = f"%{search.strip()}%"
                query = query.where(
                    or_(
                        ClaimRecord.claim_number.ilike(pat),
                        ClaimRecord.insured_last_name.ilike(pat),
                        ClaimRecord.claimant_last_name.ilike(pat),
                    )
                )

        query = query.order_by(desc(ClaimRecord.created_at))
        res = await db.execute(query)
        claims = res.scalars().all()

    total_rows = len(claims)
    logger.info(f"Generating export {export_id} for {total_rows} claims in format {export_format}")

    if task_instance:
        task_instance.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": total_rows, "percent": 10, "status": "Extracting claim records"},
        )

    export_rows = []
    for idx, c in enumerate(claims):
        insured = f"{c.insured_first_name or ''} {c.insured_last_name or ''}".strip()
        claimant = f"{c.claimant_first_name or ''} {c.claimant_last_name or ''}".strip()
        driver = f"{c.driver_first_name or ''} {c.driver_last_name or ''}".strip()

        export_rows.append({
            "Primary Key": c.primary_key or "",
            "Claim Number": c.claim_number,
            "Exposure Number": c.exposure_number or "1",
            "Insured First Name": c.insured_first_name or "",
            "Insured Last Name": c.insured_last_name or "",
            "Insured Party": insured or "N/A",
            "Claimant First Name": c.claimant_first_name or "",
            "Claimant Last Name": c.claimant_last_name or "",
            "Claimant Party": claimant or "N/A",
            "Driver First Name (Insured Vehicle)": c.driver_first_name or "",
            "Driver Last Name (Insured Vehicle)": c.driver_last_name or "",
            "Driver": driver or "N/A",
            "DOL": c.dol or "",
            "Policy State": c.policy_state or "",
            "Loss Location State": c.loss_location_state or "",
            "Status": c.record_status.value if hasattr(c.record_status, "value") else str(c.record_status),
            "Fuzzy Match": c.fuzzy_match_status.value if hasattr(c.fuzzy_match_status, "value") else str(c.fuzzy_match_status),
            "Total Duration (s)": c.total_duration_seconds or "",
            "Broward Bot": c.fl_botstatus_broward.value if hasattr(c.fl_botstatus_broward, "value") else str(c.fl_botstatus_broward),
            "Hillsborough Bot": c.fl_botstatus_hillsborough.value if hasattr(c.fl_botstatus_hillsborough, "value") else str(c.fl_botstatus_hillsborough),
            "Miami-Dade Bot": c.fl_botstatus_miami.value if hasattr(c.fl_botstatus_miami, "value") else str(c.fl_botstatus_miami),
            "Travis Bot": c.te_botstatus_travis.value if hasattr(c.te_botstatus_travis, "value") else str(c.te_botstatus_travis),
            "Dallas Bot": c.te_botstatus_dallas.value if hasattr(c.te_botstatus_dallas, "value") else str(c.te_botstatus_dallas),
            "Harris JP Bot": c.te_botstatus_harris.value if hasattr(c.te_botstatus_harris, "value") else str(c.te_botstatus_harris),
            "Harris Clerk Bot": c.te_botstatus_cclerk.value if hasattr(c.te_botstatus_cclerk, "value") else str(c.te_botstatus_cclerk),
            "Harris District Bot": c.te_botstatus_hcdistrict.value if hasattr(c.te_botstatus_hcdistrict, "value") else str(c.te_botstatus_hcdistrict),
            "Created At": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else "",
        })

        if task_instance and total_rows > 0 and (idx + 1) % max(1, total_rows // 5) == 0:
            pct = 10 + int(((idx + 1) / total_rows) * 70)
            task_instance.update_state(
                state="PROGRESS",
                meta={"current": idx + 1, "total": total_rows, "percent": pct, "status": "Formatting rows"},
            )

    df = pd.DataFrame(export_rows)
    ext = "xlsx" if export_format.lower() in ("xlsx", "excel") else ("json" if export_format.lower() == "json" else "csv")
    filename = f"claims_export_{timestamp}_{export_id[:8]}.{ext}"
    target_path = EXPORT_DIR / filename

    if ext == "csv":
        df.to_csv(target_path, index=False, encoding="utf-8")
    elif ext == "json":
        df.to_json(target_path, orient="records", indent=2)
    else:
        with pd.ExcelWriter(target_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Claims")

    file_size = target_path.stat().st_size

    if task_instance:
        task_instance.update_state(
            state="PROGRESS",
            meta={"current": total_rows, "total": total_rows, "percent": 100, "status": "Finalizing export file"},
        )

    return {
        "export_id": export_id,
        "filename": filename,
        "total_rows": total_rows,
        "format": ext,
        "file_size": file_size,
        "file_path": str(target_path),
        "status": "SUCCESS",
    }


@celery_app.task(bind=True, name="uaic_orchestrator.tasks.export_claims_dataset_task")
def export_claims_dataset_task(
    self,
    export_format: str = "xlsx",
    filters: dict[str, Any] | None = None,
    claim_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Celery background worker entrypoint for generating large claim dataset exports."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    result = loop.run_until_complete(
        _generate_export_data(
            export_format=export_format,
            filters=filters,
            claim_ids=claim_ids,
            task_instance=self,
        )
    )
    return result
