"""Data Ingestion endpoints for Excel/CSV file upload, column mapping, and validation."""

import csv
import io
import json
import os
import uuid

import aiofiles
import pandas as pd
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.models.claim import ClaimRecord, IngestionBatch
from app.schemas.queue import (
    BatchSummaryResponse,
    ColumnMappingRecommendation,
    FilePreviewRecord,
    FilePreviewResponse,
    FileValidationResponse,
    TargetFieldDefinition,
    ValidationIssue,
)
from app.services.audit_service import extract_client_context, log_audit_event_async
from app.services.excel_parser import (
    TARGET_CLAIM_FIELDS,
    auto_detect_column_mapping,
    extract_columns_and_samples,
    validate_and_normalize_claim_data,
)

router = APIRouter()

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _parse_content_to_dataframe(content: bytes, filename: str) -> tuple[pd.DataFrame, list[str], str]:
    """Helper to parse uploaded raw bytes into pandas DataFrame."""
    sheet_names = []
    file_type = "CSV Document (.csv)"
    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        file_type = "Microsoft Excel (.xlsx)" if filename.endswith(".xlsx") else "Microsoft Excel 97-2003 (.xls)"
        try:
            excel_file = pd.ExcelFile(io.BytesIO(content))
            sheet_names = excel_file.sheet_names
            df = excel_file.parse(sheet_names[0])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse Excel spreadsheet: {e}")
    else:
        try:
            df = pd.read_csv(io.BytesIO(content), dtype=str)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse CSV document: {e}")

    df.columns = [str(col).strip() for col in df.columns]
    return df, sheet_names, file_type


@router.post("/preview", response_model=FilePreviewResponse)
async def preview_excel_file(file: UploadFile = File(...)):
    """Inspect and preview an uploaded spreadsheet before ingesting into queue."""
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are supported.")

    content = await file.read()
    filesize_bytes = len(content)

    if filesize_bytes < 1024:
        filesize_formatted = f"{filesize_bytes} B"
    elif filesize_bytes < 1024 * 1024:
        filesize_formatted = f"{(filesize_bytes / 1024):.1f} KB"
    else:
        filesize_formatted = f"{(filesize_bytes / (1024 * 1024)):.2f} MB"

    df, sheet_names, file_type = _parse_content_to_dataframe(content, file.filename)
    detected_columns, column_samples = extract_columns_and_samples(df)

    # Generate mapping recommendations
    raw_recs = auto_detect_column_mapping(detected_columns)
    mapping_recommendations = [ColumnMappingRecommendation(**r) for r in raw_recs]

    # Target fields metadata
    target_fields = [
        TargetFieldDefinition(
            key=f["key"],
            label=f["label"],
            required=f["required"],
            description=f["description"],
        )
        for f in TARGET_CLAIM_FIELDS
    ]

    # Compute default normalization analysis
    norm_result = validate_and_normalize_claim_data(
        df=df,
        column_mapping=None,
        existing_claims=set(),
        duplicate_strategy="SKIP",
    )

    preview_records = [FilePreviewRecord(**rec) for rec in norm_result["preview_records"]]

    return FilePreviewResponse(
        filename=file.filename,
        filesize_bytes=filesize_bytes,
        filesize_formatted=filesize_formatted,
        file_type=file_type,
        total_records=norm_result["total_rows"],
        valid_records=norm_result["valid_rows"],
        invalid_records=norm_result["invalid_rows"],
        sheet_names=sheet_names,
        detected_columns=detected_columns,
        column_samples=column_samples,
        target_fields=target_fields,
        mapping_recommendations=mapping_recommendations,
        florida_claims_count=norm_result["florida_count"],
        texas_claims_count=norm_result["texas_count"],
        cross_state_claims_count=norm_result["cross_state_count"],
        estimated_bot_runs=norm_result["estimated_bots"],
        preview_records=preview_records,
    )


@router.post("/validate", response_model=FileValidationResponse)
async def validate_spreadsheet_mapping(
    file: UploadFile = File(...),
    mapping: str = Form("{}"),
    duplicate_strategy: str = Form("SKIP"),
    db: AsyncSession = Depends(get_db),
):
    """Validate uploaded spreadsheet against custom column mapping and database duplicate check."""
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are supported.")

    try:
        column_mapping = json.loads(mapping) if mapping else {}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in mapping parameter: {e}")

    content = await file.read()
    df, _, _ = _parse_content_to_dataframe(content, file.filename)

    # Fetch existing claims from database for duplicate verification
    existing_q = await db.execute(select(ClaimRecord.claim_number))
    existing_claims = {str(c) for c in existing_q.scalars().all() if c}

    norm_result = validate_and_normalize_claim_data(
        df=df,
        column_mapping=column_mapping,
        existing_claims=existing_claims,
        duplicate_strategy=duplicate_strategy,
    )

    issues = [ValidationIssue(**i) for i in norm_result["issues"]]
    preview_records = [FilePreviewRecord(**rec) for rec in norm_result["preview_records"]]

    can_proceed = norm_result["valid_rows"] > 0

    return FileValidationResponse(
        filename=file.filename,
        total_rows=norm_result["total_rows"],
        valid_rows=norm_result["valid_rows"],
        invalid_rows=norm_result["invalid_rows"],
        duplicate_rows=norm_result["duplicate_rows"],
        duplicate_strategy=duplicate_strategy,
        florida_claims_count=norm_result["florida_count"],
        texas_claims_count=norm_result["texas_count"],
        cross_state_claims_count=norm_result["cross_state_count"],
        estimated_bot_runs=norm_result["estimated_bots"],
        issues=issues,
        preview_records=preview_records,
        can_proceed=can_proceed,
    )


@router.post("/upload", response_model=BatchSummaryResponse)
async def upload_excel_file(
    file: UploadFile = File(...),
    mapping: str | None = Form(None),
    duplicate_strategy: str = Form("SKIP"),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Accept an Excel or CSV file, persist to disk, and trigger background parsing with column mapping."""
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are supported.")

    mapping_dict = None
    if mapping:
        try:
            mapping_dict = json.loads(mapping)
        except Exception:
            mapping_dict = None

    batch_id = str(uuid.uuid4())
    stored_filename = f"{batch_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)

    # Create IngestionBatch DB record with mapping config
    batch = IngestionBatch(
        id=batch_id,
        filename=file.filename,
        status="PROCESSING",
        total_records=0,
        processed_records=0,
        failed_records=0,
        duplicate_records=0,
        invalid_records=0,
        mapping_config=mapping_dict,
    )
    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    ctx = extract_client_context(request)
    await log_audit_event_async(
        session=db,
        action="BATCH_IMPORTED",
        entity_type="BATCH",
        description=f"Uploaded batch spreadsheet '{file.filename}' (ID: {batch_id})",
        entity_id=batch_id,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={
            "filename": file.filename,
            "filesize_bytes": len(content),
            "duplicate_strategy": duplicate_strategy,
            "has_custom_mapping": bool(mapping_dict),
        },
    )
    await db.commit()

    # Dispatch Celery background task to parse and ingest rows
    celery_app.send_task(
        "app.tasks.ingest_tasks.parse_and_ingest_file_task",
        args=[batch_id, file_path, mapping_dict, duplicate_strategy],
        queue="ingest",
    )

    return batch


@router.get("/batches/{batch_id}", response_model=BatchSummaryResponse)
async def get_batch_status(batch_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the current processing status and metrics for an ingestion batch."""
    q = select(IngestionBatch).where(IngestionBatch.id == batch_id)
    res = await db.execute(q)
    batch = res.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Ingestion batch '{batch_id}' not found.")
    return batch


@router.get("/batches/{batch_id}/failed-rows")
async def download_failed_rows_csv(batch_id: str, db: AsyncSession = Depends(get_db)):
    """Download a CSV containing all failed, invalid, or skipped duplicate rows for a batch."""
    q = select(IngestionBatch).where(IngestionBatch.id == batch_id)
    res = await db.execute(q)
    batch = res.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Ingestion batch '{batch_id}' not found.")

    failed_data = batch.failed_rows_data or []
    output = io.StringIO()

    if not failed_data:
        # Generate empty report with informative headers
        writer = csv.writer(output)
        writer.writerow(["row_number", "claim_number", "status", "reason"])
        writer.writerow(["-", "-", "INFO", "No failed, invalid, or skipped duplicate rows in this batch."])
    else:
        # Determine all distinct fieldnames
        fieldnames = ["row_number", "claim_number", "status", "reason"]
        all_keys = set()
        for item in failed_data:
            all_keys.update(item.keys())
        extra_keys = sorted(all_keys - set(fieldnames))
        fieldnames.extend(extra_keys)

        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in failed_data:
            writer.writerow(item)

    output.seek(0)
    clean_filename = f"failed_rows_{batch.filename.replace(' ', '_')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{clean_filename}"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )


@router.get("/sample/excel", summary="Download sample claim Excel file (.xlsx)")
async def download_sample_excel():
    """Download template Excel file with realistic test claim data."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "sample_claims.xlsx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample Excel file not found.")
    return FileResponse(
        path=file_path,
        filename="sample_claims.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/sample/csv", summary="Download sample claim CSV file (.csv)")
async def download_sample_csv():
    """Download template CSV file with realistic test claim data."""
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "sample_claims.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Sample CSV file not found.")
    return FileResponse(
        path=file_path,
        filename="sample_claims.csv",
        media_type="text/csv",
    )

