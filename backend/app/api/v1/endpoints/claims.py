import asyncio
import io
import logging
import math
import os
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.config import settings
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.claim import (
    BotStatusEnum,
    ClaimRecord,
    FuzzyMatchStatusEnum,
    RecordStatusEnum,
)
from app.models.error_screenshot import ErrorScreenshot
from app.schemas.audit import AuditLogResponse
from app.schemas.claim import (
    BotStatusDetail,
    BulkActionRequest,
    BulkActionResponse,
    ClaimCombinedLogsResponse,
    ClaimCreate,
    ClaimListResponse,
    ClaimResponse,
    ClaimUpdate,
    CleanDatabaseResponse,
    ExceptionLogEntry,
    ProcessingLogEntry,
)
from app.scripts.clean_history import clear_database_records, purge_redis_queues
from app.services.audit_service import (
    extract_client_context,
    log_audit_event_async,
    record_audit_event_background,
)
from app.services.excel_parser import resolve_county_bot_targets
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.api.claims")
router = APIRouter()


# Stage key name aliases — maps non-canonical keys recorded by various scrapers/tasks
# to the canonical keys expected by the frontend telemetry UI.
_STAGE_KEY_ALIASES: dict[str, str] = {
    "captcha_bypass": "captcha",
    "cloudflare_bypass": "captcha",
    "captcha_solve": "captcha",
    "turnstile_bypass": "captcha",
    "court_scraping": "result_retrieval",
    "scraping": "result_retrieval",
    "data_extraction": "result_retrieval",
    "results_parsing": "result_retrieval",
    "guidewire_mock": "guidewire_trigger",
    "guidewire_dispatch": "guidewire_trigger",
    "guidewire_api": "guidewire_trigger",
    "excel_ingestion": "browser_launch",
    "browser_start": "browser_launch",
    "context_launch": "browser_launch",
    "navigation": "website_navigation",
    "page_navigation": "website_navigation",
    "portal_navigation": "website_navigation",
    "data_entry": "data_filling",
    "form_fill": "data_filling",
    "form_filling": "data_filling",
    "search_submit": "submit",
    "page_submit": "submit",
    "form_submit": "submit",
    "db_save": "database_save",
    "db_commit": "database_save",
    "db_write": "database_save",
}


def _normalize_stage_keys(stages: dict) -> dict:
    """Map alternative stage key names to their canonical frontend-expected keys.
    Preserves all existing data; only renames keys that have known aliases.
    Canonical keys: browser_launch, website_navigation, data_filling, captcha,
                    submit, result_retrieval, database_save, fuzzy_matching, guidewire_trigger.
    """
    if not stages:
        return stages
    normalized: dict = {}
    for k, v in stages.items():
        canonical = _STAGE_KEY_ALIASES.get(k, k)
        # Don't overwrite if canonical key already present with real data
        if canonical not in normalized:
            normalized[canonical] = v
        elif not normalized[canonical]:
            normalized[canonical] = v
    return normalized


def _build_bot_details(claim: ClaimRecord) -> list[BotStatusDetail]:
    """Helper to construct list of 8 county bot details with dynamic portal URLs from settings.
    Falls back to scraped_cases count per county when te_jsonbody_* / fl_jsonbody_* are empty.
    """
    try:
        from app.services.settings_service import get_system_settings_sync
        portals_cfg = get_system_settings_sync().portals
    except Exception:
        portals_cfg = None

    broward_url = portals_cfg.broward_url if portals_cfg else "https://www.browardclerk.org/"
    hillsborough_url = portals_cfg.hillsborough_url if portals_cfg else "https://hover.hillsclerk.com/"
    miami_url = portals_cfg.miami_url if portals_cfg else "https://www2.miamidadeclerk.gov/ocs"
    travis_url = portals_cfg.travis_url if portals_cfg else "https://odysseyweb.traviscountytx.gov/Portal/"
    dallas_url = portals_cfg.dallas_url if portals_cfg else "https://courtsportal.dallascounty.org/DALLASPROD/Home/"
    harris_jp_url = portals_cfg.harris_jp_url if portals_cfg else "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/"
    harris_cclerk_url = portals_cfg.harris_cclerk_url if portals_cfg else "https://www.cclerk.hctx.net/Applications/WebSearch/"
    harris_district_url = portals_cfg.harris_district_url if portals_cfg else "https://www.hcdistrictclerk.com/"

    # Build per-county scraped case count from the scraped_cases relationship
    # so the bot grid always shows correct counts even when te_jsonbody_*/fl_jsonbody_* are empty.
    scraped_by_county: dict[str, int] = {}
    if hasattr(claim, "scraped_cases") and claim.scraped_cases:
        for sc in claim.scraped_cases:
            county = (sc.county_name or "").lower()
            scraped_by_county[county] = scraped_by_county.get(county, 0) + 1

    def _case_count(json_body, county_keywords: list[str]) -> int:
        """Return case count from json_body field, falling back to scraped_cases count."""
        if isinstance(json_body, list) and json_body:
            return len(json_body)
        # Fallback: count from ScrapedCourtCase records by county keyword match
        for county_lower, cnt in scraped_by_county.items():
            if any(kw in county_lower for kw in county_keywords):
                return cnt
        return 0

    bots = [
        BotStatusDetail(
            name="Broward County (FL)",
            website_url=broward_url,
            target=claim.fl_website_broward or "No",
            status=claim.fl_botstatus_broward or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.fl_jsonbody_broward, ["broward"]),
        ),
        BotStatusDetail(
            name="Hillsborough County (FL)",
            website_url=hillsborough_url,
            target=claim.fl_website_hillsborough or "No",
            status=claim.fl_botstatus_hillsborough or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.fl_jsonbody_hillsborough, ["hillsborough"]),
        ),
        BotStatusDetail(
            name="Miami-Dade County (FL)",
            website_url=miami_url,
            target=claim.fl_website_miami or "No",
            status=claim.fl_botstatus_miami or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.fl_jsonbody_miami, ["miami", "miami-dade", "miamidade"]),
        ),
        BotStatusDetail(
            name="Travis County (TX)",
            website_url=travis_url,
            target=claim.te_website_travis or "No",
            status=claim.te_botstatus_travis or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.te_jsonbody_travis, ["travis"]),
        ),
        BotStatusDetail(
            name="Dallas County (TX)",
            website_url=dallas_url,
            target=claim.te_website_dallas or "No",
            status=claim.te_botstatus_dallas or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.te_jsonbody_dallas, ["dallas"]),
        ),
        BotStatusDetail(
            name="Harris County JP (TX)",
            website_url=harris_jp_url,
            target=claim.te_website_harris or "No",
            status=claim.te_botstatus_harris or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.te_jsonbody_harris, ["harris"]),
        ),
        BotStatusDetail(
            name="Harris County Clerk (TX)",
            website_url=harris_cclerk_url,
            target=claim.te_website_cclerk or "No",
            status=claim.te_botstatus_cclerk or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.te_jsonbody_cclerk, ["harris"]),
        ),
        BotStatusDetail(
            name="Harris District Clerk (TX)",
            website_url=harris_district_url,
            target=claim.te_website_hcdistrict or "No",
            status=claim.te_botstatus_hcdistrict or BotStatusEnum.NOT_TRIGGERED,
            cases_found=_case_count(claim.te_jsonbody_hcdistrict, ["harris"]),
        ),
    ]
    return bots


_build_bot_status_list = _build_bot_details


def _normalize_action_timings(action_timings: dict | None) -> dict | None:
    """Normalize stage key names inside action_timings before returning to frontend.
    Applies _normalize_stage_keys to both top-level stages dict and per-portal stages dicts.
    """
    if not action_timings:
        return action_timings
    timings = dict(action_timings)
    # Normalize top-level stages
    if "stages" in timings and isinstance(timings["stages"], dict):
        timings["stages"] = _normalize_stage_keys(timings["stages"])
    # Normalize per-portal stages
    if "portals" in timings and isinstance(timings["portals"], dict):
        portals = dict(timings["portals"])
        for portal_key, portal_data in portals.items():
            if isinstance(portal_data, dict) and "stages" in portal_data:
                portal_data = dict(portal_data)
                portal_data["stages"] = _normalize_stage_keys(portal_data["stages"])
                portals[portal_key] = portal_data
        timings["portals"] = portals
    return timings


def _map_claim_to_response(claim: ClaimRecord) -> ClaimResponse:

    insured_name = f"{claim.insured_first_name or ''} {claim.insured_last_name or ''}".strip() or "N/A"
    claimant_name = f"{claim.claimant_first_name or ''} {claim.claimant_last_name or ''}".strip() or "N/A"
    driver_name = f"{claim.driver_first_name or ''} {claim.driver_last_name or ''}".strip() or "N/A"

    court_cases = []
    if hasattr(claim, "scraped_cases") and claim.scraped_cases:
        from app.schemas.claim import ScrapedCaseResponse
        for sc in claim.scraped_cases:
            party_searched = getattr(sc, "party_name_searched", None)
            if not party_searched and isinstance(getattr(sc, "raw_payload", None), dict):
                party_searched = sc.raw_payload.get("PartyNameSearched")
            source_url = getattr(sc, "county_website", getattr(sc, "source_url", None))
            court_cases.append(
                ScrapedCaseResponse(
                    id=sc.id,
                    county_name=sc.county_name,
                    case_number=sc.case_number,
                    case_style=sc.case_style,
                    filing_date=sc.filing_date or (
                        sc.raw_payload.get("FilingDate")
                        or sc.raw_payload.get("filing_date")
                        or sc.raw_payload.get("Filing Date")
                        or sc.raw_payload.get("SuitFiledDate")
                        or sc.raw_payload.get("suit_filed_date")
                        or sc.raw_payload.get("DateFiled")
                        or sc.raw_payload.get("date_filed")
                        or sc.raw_payload.get("Filed")
                        or sc.raw_payload.get("filed")
                        or sc.raw_payload.get("filed_date")
                        if isinstance(sc.raw_payload, dict)
                        else None
                    ) or claim.dol,
                    case_status=sc.case_status,
                    case_type=sc.case_type,
                    raw_payload=sc.raw_payload,
                    party_name_searched=party_searched,
                    source_url=source_url,
                    created_at=sc.created_at,
                )
            )

    return ClaimResponse(
        id=claim.id,
        batch_id=claim.batch_id,
        claim_number=claim.claim_number,
        exposure_number=claim.exposure_number,
        primary_key=claim.primary_key,
        dol=claim.dol,
        insured_name=insured_name,
        claimant_name=claimant_name,
        driver_name=driver_name,
        insured_first_name=claim.insured_first_name,
        insured_last_name=claim.insured_last_name,
        claimant_first_name=claim.claimant_first_name,
        claimant_last_name=claim.claimant_last_name,
        driver_first_name=claim.driver_first_name,
        driver_last_name=claim.driver_last_name,
        loss_location_state=claim.loss_location_state,
        policy_state=claim.policy_state,
        record_status=claim.record_status,
        fuzzy_match_status=claim.fuzzy_match_status,
        bots=_build_bot_details(claim),
        court_cases=court_cases,
        final_matched_json=claim.final_matched_json,
        activity_id=claim.activity_id,
        retry_count=claim.retry_count,
        last_error=claim.last_error,
        action_timings=_normalize_action_timings(claim.action_timings),
        total_duration_seconds=claim.total_duration_seconds,
        created_by=getattr(claim, "created_by", None) or "system",
        modified_by=getattr(claim, "modified_by", None) or "system",
        created_on=claim.created_at,
        modified_on=claim.updated_at,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
    )


@router.get("", response_model=ClaimListResponse)
async def list_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    status: str | None = None,
    fuzzy_status: str | None = None,
    state: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    search: str | None = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    """List all ingested claims with multi-field filtering, search, sorting, and pagination."""
    query = select(ClaimRecord)
    
    if status and status.strip():
        try:
            status_enum = RecordStatusEnum(status.strip())
            query = query.where(ClaimRecord.record_status == status_enum)
        except ValueError:
            pass
    if fuzzy_status and fuzzy_status.strip():
        try:
            fuzzy_enum = FuzzyMatchStatusEnum(fuzzy_status.strip())
            query = query.where(ClaimRecord.fuzzy_match_status == fuzzy_enum)
        except ValueError:
            pass
    if state:
        st_clean = state.strip().upper()
        patterns = [st_clean]
        if st_clean in ("FL", "FLORIDA"):
            patterns = ["FL", "FLORIDA"]
        elif st_clean in ("TX", "TEXAS"):
            patterns = ["TX", "TEXAS"]
        query = query.where(
            or_(
                func.upper(ClaimRecord.loss_location_state).in_(patterns),
                func.upper(ClaimRecord.policy_state).in_(patterns),
            )
        )
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.where(
            or_(
                ClaimRecord.claim_number.ilike(search_pattern),
                ClaimRecord.insured_last_name.ilike(search_pattern),
                ClaimRecord.insured_first_name.ilike(search_pattern),
                ClaimRecord.claimant_last_name.ilike(search_pattern),
                ClaimRecord.claimant_first_name.ilike(search_pattern),
            )
        )

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    # Dynamic sorting
    sort_attr_map = {
        "created_at": ClaimRecord.created_at,
        "updated_at": ClaimRecord.updated_at,
        "claim_number": ClaimRecord.claim_number,
        "insured_last_name": ClaimRecord.insured_last_name,
        "claimant_last_name": ClaimRecord.claimant_last_name,
        "record_status": ClaimRecord.record_status,
        "total_duration_seconds": ClaimRecord.total_duration_seconds,
    }
    target_column = sort_attr_map.get(sort_by, ClaimRecord.created_at)
    order_func = desc if sort_order.lower() == "desc" else asc
    query = query.order_by(order_func(target_column)).offset((page - 1) * page_size).limit(page_size)

    records_res = await db.execute(query)
    records = records_res.scalars().all()

    items = [_map_claim_to_response(r) for r in records]
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return ClaimListResponse(total=total, items=items, page=page, page_size=page_size, total_pages=total_pages)


@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    payload: ClaimCreate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create a new claim record with field validation and bot target assignment."""
    # Prevent duplicate claim numbers
    existing = await db.execute(select(ClaimRecord).where(ClaimRecord.claim_number == payload.claim_number.strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Claim '{payload.claim_number}' already exists in system.")

    # Automatically resolve county bot targets if not explicitly set
    targets = resolve_county_bot_targets(payload.policy_state, payload.loss_location_state)
    ctx = extract_client_context(request)
    creator_email = payload.created_by or ctx["user_email"] or "user"
    
    claim = ClaimRecord(
        claim_number=payload.claim_number.strip(),
        exposure_number=payload.exposure_number or "1",
        primary_key=payload.primary_key.strip() if payload.primary_key else None,
        insured_first_name=payload.insured_first_name.strip() if payload.insured_first_name else None,
        insured_last_name=payload.insured_last_name.strip() if payload.insured_last_name else None,
        claimant_first_name=payload.claimant_first_name.strip() if payload.claimant_first_name else None,
        claimant_last_name=payload.claimant_last_name.strip() if payload.claimant_last_name else None,
        driver_first_name=payload.driver_first_name.strip() if payload.driver_first_name else None,
        driver_last_name=payload.driver_last_name.strip() if payload.driver_last_name else None,
        dol=payload.dol,
        loss_location_state=payload.loss_location_state,
        policy_state=payload.policy_state,
        record_status=RecordStatusEnum.NEW,
        fuzzy_match_status=FuzzyMatchStatusEnum.NEW,
        created_by=creator_email,
        modified_by=creator_email,
        fl_website_broward=payload.fl_website_broward or targets["fl_broward"],
        fl_website_hillsborough=payload.fl_website_hillsborough or targets["fl_hillsborough"],
        fl_website_miami=payload.fl_website_miami or targets["fl_miami"],
        te_website_travis=payload.te_website_travis or targets["te_travis"],
        te_website_dallas=payload.te_website_dallas or targets["te_dallas"],
        te_website_harris=payload.te_website_harris or targets["te_harris"],
        te_website_cclerk=payload.te_website_cclerk or targets["te_cclerk"],
        te_website_hcdistrict=payload.te_website_hcdistrict or targets["te_hcdistrict"],
    )
    db.add(claim)
    await db.commit()
    await db.refresh(claim)
    await log_audit_event_async(
        session=db,
        action="CLAIM_CREATED",
        entity_type="CLAIM",
        description=f"Created new claim record '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={
            "claim_number": claim.claim_number,
            "policy_state": claim.policy_state,
            "loss_location_state": claim.loss_location_state,
        },
    )
    await db.commit()

    logger.info(f"Created new single claim record: {claim.claim_number} (ID: {claim.id})")
    return _map_claim_to_response(claim)


@router.get("/stats")
async def get_claim_stats(db: AsyncSession = Depends(get_db)):
    """Summary metrics of all claims across all stages."""
    total_q = await db.execute(select(func.count(ClaimRecord.id)))
    total = total_q.scalar_one()

    new_q = await db.execute(select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.NEW))
    new_count = new_q.scalar_one()

    in_progress_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(
            ClaimRecord.record_status.in_([
                RecordStatusEnum.SCRAPING_IN_PROGRESS,
                RecordStatusEnum.SCRAPING_COMPLETED,
            ])
        )
    )
    in_progress = in_progress_q.scalar_one()

    match_found_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.MATCH_FOUND)
    )
    match_found = match_found_q.scalar_one()

    review_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.MANUAL_REVIEW)
    )
    manual_review = review_q.scalar_one()

    no_match_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.NO_MATCH_FOUND)
    )
    no_match_found = no_match_q.scalar_one()

    failed_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.FAILED)
    )
    failed = failed_q.scalar_one()

    completed_q = await db.execute(
        select(func.count(ClaimRecord.id)).where(ClaimRecord.record_status == RecordStatusEnum.COMPLETED)
    )
    completed = completed_q.scalar_one()

    return {
        "total_claims": total,
        "new": new_count,
        "in_progress": in_progress,
        "match_found": match_found,
        "manual_review": manual_review,
        "no_match_found": no_match_found,
        "failed": failed,
        "completed": completed,
    }


@router.get("/export")
async def export_claims(
    format: str = Query("xlsx", pattern="^(xlsx|csv)$"),
    status: str | None = None,
    state: str | None = None,
    search: str | None = None,
    claim_ids: str | None = Query(None, description="Comma-separated IDs for export selected"),
    db: AsyncSession = Depends(get_db),
):
    """Export claims as formatted Excel (.xlsx) or CSV (.csv) file respecting current filters."""
    query = select(ClaimRecord)

    if claim_ids:
        id_list = [i.strip() for i in claim_ids.split(",") if i.strip()]
        if id_list:
            query = query.where(ClaimRecord.id.in_(id_list))
    else:
        if status and status.strip():
            try:
                status_enum = RecordStatusEnum(status.strip())
                query = query.where(ClaimRecord.record_status == status_enum)
            except ValueError:
                pass
        if state:
            st_clean = state.strip().upper()
            patterns = [st_clean]
            if st_clean in ("FL", "FLORIDA"):
                patterns = ["FL", "FLORIDA"]
            elif st_clean in ("TX", "TEXAS"):
                patterns = ["TX", "TEXAS"]
            query = query.where(
                or_(
                    func.upper(ClaimRecord.loss_location_state).in_(patterns),
                    func.upper(ClaimRecord.policy_state).in_(patterns),
                )
            )
        if search:
            pat = f"%{search.strip()}%"
            query = query.where(
                or_(
                    ClaimRecord.claim_number.ilike(pat),
                    ClaimRecord.insured_last_name.ilike(pat),
                    ClaimRecord.claimant_last_name.ilike(pat),
                )
            )

    query = query.order_by(desc(ClaimRecord.created_at)).limit(5000)
    res = await db.execute(query)
    claims = res.scalars().all()

    export_rows = []
    for c in claims:
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

    df = pd.DataFrame(export_rows)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if format == "csv":
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=claims_export_{timestamp}.csv"},
        )
    else:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Claims")
        out.seek(0)
        return Response(
            content=out.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=claims_export_{timestamp}.xlsx"},
        )


class AsyncExportRequest(BaseModel):
    format: str = "xlsx"
    status: str | None = None
    state: str | None = None
    search: str | None = None
    claim_ids: list[str] | None = None


@router.post("/export-async")
async def trigger_async_export(payload: AsyncExportRequest):
    """Trigger background Celery export task for large claim datasets."""
    filters = {
        "status": payload.status,
        "state": payload.state,
        "search": payload.search,
    }
    try:
        if getattr(celery_app.conf, "task_always_eager", False):
            from app.tasks.export_tasks import export_claims_dataset_task
            task = export_claims_dataset_task.apply(
                kwargs={
                    "export_format": payload.format,
                    "filters": filters,
                    "claim_ids": payload.claim_ids,
                }
            )
            return {
                "success": True,
                "task_id": task.id,
                "message": f"Asynchronous export task queued in {payload.format.upper()} format.",
            }

        task = celery_app.send_task(
            "app.tasks.export_tasks.export_claims_dataset_task",
            kwargs={
                "export_format": payload.format,
                "filters": filters,
                "claim_ids": payload.claim_ids,
            },
            queue="notifications",
            retry=False,
            retry_policy={"max_retries": 0},
        )
        return {
            "success": True,
            "task_id": task.id,
            "message": f"Asynchronous export task queued in {payload.format.upper()} format.",
        }
    except Exception as e:
        logger.warning(f"Celery broker unavailable, falling back to in-process export: {e}")
        from app.tasks.export_tasks import _generate_export_data
        result = await _generate_export_data(
            export_format=payload.format,
            filters=filters,
            claim_ids=payload.claim_ids,
        )
        return {
            "success": True,
            "task_id": f"sync-{result['export_id']}",
            "direct_result": result,
            "message": f"Export completed ({result['total_rows']} rows).",
        }


@router.get("/export-async/{task_id}/status")
async def get_async_export_status(task_id: str):
    """Poll progress status of an asynchronous background export task."""
    if task_id.startswith("sync-"):
        export_id = task_id.replace("sync-", "")
        from app.tasks.export_tasks import EXPORT_DIR
        matches = list(EXPORT_DIR.glob(f"*{export_id[:8]}*"))
        filename = matches[0].name if matches else f"claims_export_{export_id}.xlsx"
        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "percent": 100,
            "result": {
                "filename": filename,
                "download_url": f"/api/v1/claims/export-async/download/{filename}",
            },
        }

    from celery.result import AsyncResult

    from app.core.celery_app import celery_app

    res = AsyncResult(task_id, app=celery_app)
    if res.state == "PROGRESS":
        info = res.info or {}
        return {
            "task_id": task_id,
            "status": "PROGRESS",
            "percent": info.get("percent", 50),
            "current": info.get("current", 0),
            "total": info.get("total", 0),
            "message": info.get("status", "Generating export file..."),
        }
    elif res.state == "SUCCESS":
        result_data = res.result or {}
        filename = result_data.get("filename", "")
        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "percent": 100,
            "result": {
                **result_data,
                "download_url": f"/api/v1/claims/export-async/download/{filename}",
            },
        }
    elif res.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "FAILURE",
            "percent": 0,
            "error": str(res.result),
        }
    else:
        return {
            "task_id": task_id,
            "status": res.state or "PENDING",
            "percent": 20,
            "message": "Export task queued...",
        }


@router.get("/export-async/download/{filename}")
async def download_async_export_file(filename: str):
    """Stream generated export file to client."""
    from app.tasks.export_tasks import EXPORT_DIR
    target = EXPORT_DIR / filename
    if not target.exists():
        matches = list(EXPORT_DIR.glob(f"*{filename}*"))
        if matches:
            target = matches[0]
        else:
            raise HTTPException(status_code=404, detail="Export file not found or has expired.")

    media_type = "text/csv"
    if target.suffix == ".xlsx":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif target.suffix == ".json":
        media_type = "application/json"

    return FileResponse(
        path=str(target),
        media_type=media_type,
        filename=target.name,
    )


@router.post("/clean", response_model=CleanDatabaseResponse)
async def clean_database_and_queues(request: Request = None):
    """Purge all claims, scraped cases, match results, batch logs, and Celery Redis queues."""
    try:
        deleted_queues = purge_redis_queues()
        counts = await clear_database_records()
        ctx = extract_client_context(request)
        record_audit_event_background(
            action="DATABASE_CLEARED",
            entity_type="SYSTEM",
            description="Operator purged all claim records, scraped cases, and worker queues",
            user_id=ctx["user_id"],
            user_email=ctx["user_email"],
            ip_address=ctx["ip_address"],
            user_agent=ctx["user_agent"],
            status="WARNING",
            details={"cleared_counts": counts, "redis_keys_purged": deleted_queues},
        )
        return CleanDatabaseResponse(
            success=True,
            message=f"Database and worker queues cleaned successfully ({deleted_queues} Redis keys purged).",
            cleared_counts=counts,
        )
    except Exception as e:
        logger.error(f"Failed to clean database: {e}")
        raise HTTPException(status_code=500, detail=f"Database cleanup failed: {e!s}")


@router.post("/bulk-delete", response_model=BulkActionResponse)
async def bulk_delete_claims(
    payload: BulkActionRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete multiple selected claims and their associated scraped cases and match results."""
    if not payload.claim_ids:
        return BulkActionResponse(success=True, affected_count=0, message="No claim IDs provided.")
    
    # In SQLite / SQLAlchemy, cascading relationship takes care of children
    query = select(ClaimRecord).where(ClaimRecord.id.in_(payload.claim_ids))
    res = await db.execute(query)
    claims_to_del = res.scalars().all()
    count = len(claims_to_del)
    claim_numbers = [c.claim_number for c in claims_to_del]
    for c in claims_to_del:
        await db.delete(c)
    await db.commit()

    ctx = extract_client_context(request)
    await log_audit_event_async(
        session=db,
        action="BULK_CLAIMS_DELETED",
        entity_type="CLAIM",
        description=f"Bulk deleted {count} claims ({', '.join(claim_numbers[:5])}{'...' if count > 5 else ''})",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"deleted_count": count, "claim_ids": payload.claim_ids},
    )
    await db.commit()

    logger.info(f"Bulk deleted {count} claims.")
    return BulkActionResponse(success=True, affected_count=count, message=f"Successfully deleted {count} claims.")


@router.post("/bulk-status", response_model=BulkActionResponse)
async def bulk_update_claim_status(
    payload: BulkActionRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update status for multiple selected claims."""
    if not payload.claim_ids or not payload.status:
        raise HTTPException(status_code=400, detail="Both claim_ids and status are required.")
    
    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    query = select(ClaimRecord).where(ClaimRecord.id.in_(payload.claim_ids))
    res = await db.execute(query)
    claims_to_update = res.scalars().all()
    count = len(claims_to_update)
    for c in claims_to_update:
        c.record_status = payload.status
        c.modified_by = modifier_email
    await db.commit()

    await log_audit_event_async(
        session=db,
        action="BULK_STATUS_CHANGED",
        entity_type="CLAIM",
        description=f"Updated status to {payload.status.value} for {count} claims",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"new_status": payload.status.value, "claim_ids": payload.claim_ids},
    )
    await db.commit()

    return BulkActionResponse(success=True, affected_count=count, message=f"Status updated to {payload.status.value} for {count} claims.")


@router.post("/bulk-start", response_model=BulkActionResponse)
async def bulk_start_claims(
    payload: BulkActionRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Queue scraping automation tasks for multiple selected claims."""
    if not payload.claim_ids:
        return BulkActionResponse(success=True, affected_count=0, message="No claim IDs provided.")
    
    settings = await get_system_settings_async()
    if not settings.automation.anticaptcha_api_key or not settings.automation.anticaptcha_api_key.strip():
        raise HTTPException(
            status_code=422,
            detail="Anti-Captcha API key is not configured in Automation Settings. Cannot start scrapers."
        )

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    query = select(ClaimRecord).where(ClaimRecord.id.in_(payload.claim_ids))
    res = await db.execute(query)
    claims = res.scalars().all()
    count = 0
    for c in claims:
        c.record_status = RecordStatusEnum.NEW
        c.retry_count += 1
        c.modified_by = modifier_email
        celery_app.send_task(
            "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
            args=[c.id],
            queue="scrapers",
        )
        count += 1
    await db.commit()

    await log_audit_event_async(
        session=db,
        action="BULK_AUTOMATION_STARTED",
        entity_type="CLAIM",
        description=f"Dispatched scraping automation for {count} claims",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"affected_count": count, "claim_ids": payload.claim_ids},
    )
    await db.commit()

    return BulkActionResponse(success=True, affected_count=count, message=f"Dispatched scraping automation for {count} claims.")


@router.post("/bulk-retry", response_model=BulkActionResponse)
async def bulk_retry_claims(
    payload: BulkActionRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Retry automation on failed claims in bulk, optionally targeting failed portals only."""
    if not payload.claim_ids:
        return BulkActionResponse(success=True, affected_count=0, message="No claim IDs provided.")

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    query = select(ClaimRecord).where(ClaimRecord.id.in_(payload.claim_ids))
    res = await db.execute(query)
    claims = res.scalars().all()
    count = 0
    for c in claims:
        c.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
        c.retry_count += 1
        c.modified_by = modifier_email
        celery_app.send_task(
            "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
            args=[c.id, None, payload.failed_portals_only],
            queue="scrapers",
        )
        count += 1
    await db.commit()

    mode_str = "failed portals only" if payload.failed_portals_only else "all portals"
    ctx = extract_client_context(request)
    await log_audit_event_async(
        session=db,
        action="BULK_PORTALS_RETRIED",
        entity_type="CLAIM",
        description=f"Dispatched bulk retry ({mode_str}) for {count} claims",
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"affected_count": count, "failed_portals_only": payload.failed_portals_only, "claim_ids": payload.claim_ids},
    )
    await db.commit()

    return BulkActionResponse(
        success=True,
        affected_count=count,
        message=f"Dispatched retry ({mode_str}) for {count} claims.",
    )


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim_detail(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full details of a specific claim."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id).options(
        selectinload(ClaimRecord.scraped_cases),
        selectinload(ClaimRecord.match_pairs),
    )
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")
    return _map_claim_to_response(claim)


@router.put("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: str,
    payload: ClaimUpdate,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Update claim record fields."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    ctx = extract_client_context(request)
    modifier_email = payload.modified_by or ctx["user_email"] or "user"
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(claim, field, val)
    claim.modified_by = modifier_email

    await db.commit()
    await db.refresh(claim)
    await log_audit_event_async(
        session=db,
        action="CLAIM_UPDATED",
        entity_type="CLAIM",
        description=f"Updated fields on claim '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"updated_fields": list(update_data.keys()), "changes": update_data},
    )
    await db.commit()

    logger.info(f"Updated claim record {claim.claim_number} (ID: {claim.id})")
    return _map_claim_to_response(claim)


@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete single claim record and all associated scraped court cases and matches."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    c_num = claim.claim_number
    await db.delete(claim)
    await db.commit()

    ctx = extract_client_context(request)
    record_audit_event_background(
        action="CLAIM_DELETED",
        entity_type="CLAIM",
        description=f"Deleted claim record '{c_num}' (ID: {claim_id})",
        entity_id=claim_id,
        claim_number=c_num,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"claim_id": claim_id, "claim_number": c_num},
    )

    logger.info(f"Deleted claim record ID: {claim_id}")
    return {"success": True, "message": f"Claim {c_num} deleted successfully."}


@router.post("/{claim_id}/start")
async def start_single_claim(
    claim_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Manually dispatch court scrapers for a single claim."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    settings = await get_system_settings_async()
    if not settings.automation.anticaptcha_api_key or not settings.automation.anticaptcha_api_key.strip():
        raise HTTPException(
            status_code=422,
            detail="Anti-Captcha API key is not configured in Automation Settings. Cannot start scraper."
        )

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    claim.record_status = RecordStatusEnum.NEW
    claim.retry_count += 1
    claim.modified_by = modifier_email
    await db.commit()

    await log_audit_event_async(
        session=db,
        action="AUTOMATION_STARTED",
        entity_type="CLAIM",
        description=f"Queued court scraping automation for claim '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"retry_count": claim.retry_count},
    )
    await db.commit()

    celery_app.send_task(
        "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
        args=[claim.id],
        queue="scrapers",
    )
    return {"status": "success", "message": f"Scraping queued for claim {claim.claim_number}."}


@router.post("/{claim_id}/stop")
async def stop_single_claim(
    claim_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Stop/cancel a running claim automation."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    claim.record_status = RecordStatusEnum.FAILED
    claim.last_error = "Cancelled by user"
    claim.modified_by = modifier_email
    await db.commit()

    ctx = extract_client_context(request)
    await log_audit_event_async(
        session=db,
        action="AUTOMATION_STOPPED",
        entity_type="CLAIM",
        description=f"Cancelled automation for claim '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="WARNING",
        details={"reason": "Cancelled by operator"},
    )
    await db.commit()

    return {"status": "success", "message": f"Claim {claim.claim_number} marked as cancelled."}


@router.post("/{claim_id}/push-guidewire")
async def push_claim_to_guidewire(
    claim_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Trigger Guidewire API sync for confirmed matches on a claim."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    claim.modified_by = modifier_email
    await log_audit_event_async(
        session=db,
        action="GUIDEWIRE_PUSHED",
        entity_type="CLAIM",
        description=f"Dispatched Guidewire Cloud sync for claim '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
    )
    await db.commit()

    celery_app.send_task(
        "app.tasks.fuzzy_tasks.notify_guidewire_task",
        args=[claim.id],
        queue="notifications",
    )
    return {"status": "success", "message": f"Guidewire dispatch queued for claim {claim.claim_number}."}


@router.post("/{claim_id}/run-bot/{bot_key}")
async def run_single_bot(
    claim_id: str,
    bot_key: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Dispatch an individual county court scraper bot on-demand for a single claim."""
    valid_bots = {
        "all": None,
        "broward": "fl_botstatus_broward",
        "hillsborough": "fl_botstatus_hillsborough",
        "miami": "fl_botstatus_miami",
        "travis": "te_botstatus_travis",
        "dallas": "te_botstatus_dallas",
        "harris_jp": "te_botstatus_harris",
        "harris_cclerk": "te_botstatus_cclerk",
        "harris_district": "te_botstatus_hcdistrict",
    }
    b_key = bot_key.strip().lower()
    if b_key not in valid_bots:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid bot_key '{bot_key}'. Valid choices: {list(valid_bots.keys())}",
        )

    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"

    # Update individual bot status to IN_PROGRESS and mark claim
    from app.models.claim import BotStatusEnum
    if b_key == "all":
        for attr in valid_bots.values():
            if attr:
                setattr(claim, attr, BotStatusEnum.IN_PROGRESS)
    else:
        setattr(claim, valid_bots[b_key], BotStatusEnum.IN_PROGRESS)
    claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
    claim.modified_by = modifier_email
    await db.commit()

    await log_audit_event_async(
        session=db,
        action="SINGLE_BOT_TRIGGERED",
        entity_type="CLAIM",
        description=f"Dispatched bot '{b_key}' scraper for claim '{claim.claim_number}'",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"bot_key": b_key},
    )
    await db.commit()

    celery_app.send_task(
        "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
        args=[claim.id, b_key],
        queue="scrapers",
    )
    return {
        "status": "success",
        "message": f"Bot '{b_key}' scraper dispatched for claim {claim.claim_number}.",
        "bot_key": b_key,
    }


@router.post("/{claim_id}/retry-failed")
async def retry_failed_portals(
    claim_id: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Dispatch scraping automation specifically for failed portals on a single claim."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    portal_status_map = {
        "broward": ("fl_website_broward", "fl_botstatus_broward"),
        "hillsborough": ("fl_website_hillsborough", "fl_botstatus_hillsborough"),
        "miami": ("fl_website_miami", "fl_botstatus_miami"),
        "travis": ("te_website_travis", "te_botstatus_travis"),
        "dallas": ("te_website_dallas", "te_botstatus_dallas"),
        "harris_jp": ("te_website_harris", "te_botstatus_harris"),
        "harris_cclerk": ("te_website_cclerk", "te_botstatus_cclerk"),
        "harris_district": ("te_website_hcdistrict", "te_botstatus_hcdistrict"),
    }

    failed_portals: list[str] = []
    for p_key, (website_flag, status_attr) in portal_status_map.items():
        if getattr(claim, website_flag) == "Yes" and getattr(claim, status_attr) in (
            BotStatusEnum.FAILED,
            BotStatusEnum.IN_PROGRESS,
        ):
            failed_portals.append(p_key)
            setattr(claim, status_attr, BotStatusEnum.IN_PROGRESS)

    if not failed_portals:
        return {
            "status": "info",
            "message": f"No failed portals found for claim {claim.claim_number}.",
            "retried_portals": [],
        }

    ctx = extract_client_context(request)
    modifier_email = ctx["user_email"] or "user"
    claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
    claim.retry_count += 1
    claim.modified_by = modifier_email
    await db.commit()

    await log_audit_event_async(
        session=db,
        action="FAILED_PORTALS_RETRIED",
        entity_type="CLAIM",
        description=f"Retrying {len(failed_portals)} failed portal(s) for claim '{claim.claim_number}': {', '.join(failed_portals)}",
        entity_id=claim.id,
        claim_number=claim.claim_number,
        user_id=ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={"retried_portals": failed_portals, "retry_count": claim.retry_count},
    )
    await db.commit()

    celery_app.send_task(
        "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
        args=[claim.id, None, True],
        queue="scrapers",
    )
    return {
        "status": "success",
        "message": f"Retrying {len(failed_portals)} failed portal(s) for claim {claim.claim_number}: {', '.join(failed_portals)}.",
        "retried_portals": failed_portals,
    }


@router.get("/{claim_id}/audit-logs", response_model=list[AuditLogResponse], summary="Get claim audit history")
async def get_claim_audit_logs(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all chronological audit trail records for a specific claim."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    claim = (await db.execute(query)).scalar_one_or_none()
    if not claim:
        query = select(ClaimRecord).where(ClaimRecord.claim_number == claim_id)
        claim = (await db.execute(query)).scalar_one_or_none()

    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    audit_query = (
        select(AuditLog)
        .where(
            or_(
                AuditLog.entity_id == claim.id,
                AuditLog.claim_number == claim.claim_number,
                AuditLog.entity_id == claim.claim_number,
                AuditLog.claim_number == claim.id,
                AuditLog.entity_id == claim_id,
                AuditLog.claim_number == claim_id,
            )
        )
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
    )
    res = await db.execute(audit_query)
    entries = res.scalars().all()
    return [AuditLogResponse.model_validate(e) for e in entries]


@router.get("/{claim_id}/screenshots", summary="List error screenshots for claim")
async def get_claim_screenshots(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve all error screenshots and failure diagnostics for a claim."""
    query = (
        select(ErrorScreenshot)
        .where(ErrorScreenshot.claim_id == claim_id)
        .order_by(ErrorScreenshot.created_at.desc())
    )
    res = await db.execute(query)
    records = res.scalars().all()
    return [
        {
            "id": r.id,
            "claim_id": r.claim_id,
            "portal_key": r.portal_key,
            "portal_name": r.portal_name,
            "page_url": r.page_url,
            "page_title": r.page_title,
            "exception_message": r.exception_message,
            "attempt_number": r.attempt_number,
            "storage_provider": getattr(r, "storage_provider", "local") or "local",
            "file_path": r.file_path,
            "image_url": f"/api/v1/claims/{claim_id}/screenshots/{r.id}/image",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/{claim_id}/screenshots/{screenshot_id}/image", summary="Stream binary screenshot image")
async def get_claim_screenshot_image(claim_id: str, screenshot_id: str, db: AsyncSession = Depends(get_db)):
    """Stream the raw screenshot PNG image for operator inspection."""
    query = (
        select(ErrorScreenshot)
        .where(ErrorScreenshot.id == screenshot_id, ErrorScreenshot.claim_id == claim_id)
    )
    res = await db.execute(query)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Screenshot record not found")

    file_path = record.file_path
    resolved_path = None
    if file_path and os.path.exists(file_path):
        resolved_path = Path(file_path)
    else:
        # Check hierarchical directory: screenshots/{claim_id}/{portal_key}/{filename}
        if record.claim_id and record.portal_key and file_path:
            hierarchical_path = settings.SCREENSHOTS_DIR / str(record.claim_id) / str(record.portal_key) / Path(file_path).name
            if hierarchical_path.exists():
                resolved_path = hierarchical_path
        if not resolved_path and file_path:
            local_path = settings.SCREENSHOTS_DIR / Path(file_path).name
            if local_path.exists():
                resolved_path = local_path
        if not resolved_path and file_path:
            matches = list(settings.SCREENSHOTS_DIR.glob(f"**/{Path(file_path).name}"))
            if matches:
                resolved_path = matches[0]

    if not resolved_path or not resolved_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot image file not found on disk")

    return FileResponse(
        path=str(resolved_path),
        media_type="image/png",
        filename=resolved_path.name,
    )


@router.get("/{claim_id}/logs/{portal_key}", summary="Get portal execution log for claim")
async def get_claim_portal_log(claim_id: str, portal_key: str):
    """Retrieve execution log for a specific portal run of a claim."""
    log_file = settings.LOGS_DIR / str(claim_id) / str(portal_key) / "execution.log"
    if not log_file.exists():
        return {"claim_id": claim_id, "portal_key": portal_key, "log_text": "", "exists": False}
    try:
        with open(log_file, encoding="utf-8") as f:
            log_text = f.read()
        return {"claim_id": claim_id, "portal_key": portal_key, "log_text": log_text, "exists": True}
    except Exception as e:
        return {"claim_id": claim_id, "portal_key": portal_key, "log_text": f"Error reading log: {e}", "exists": False}


@router.get("/{claim_id}/combined-logs", response_model=ClaimCombinedLogsResponse, summary="Get combined audit, processing, and exception logs for claim")
async def get_claim_combined_logs(
    claim_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve comprehensive unified logs for a claim including:
    - Provenance: created_on, created_by, modified_on, modified_by
    - Audit Trail: full history of user and system events
    - Processing Logs: chronological timeline of automation pipeline stages, Celery tasks, and portal actions
    - Exception Logs: detailed errors with stack traces, failing portal, failing stage, and error screenshots
    - Portal Logs: raw terminal logs per county court portal
    """
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id)
    claim = (await db.execute(query)).scalar_one_or_none()
    if not claim:
        query = select(ClaimRecord).where(ClaimRecord.claim_number == claim_id)
        claim = (await db.execute(query)).scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    # 1. Fetch Audit Logs
    audit_query = (
        select(AuditLog)
        .where(
            or_(
                AuditLog.entity_id == claim.id,
                AuditLog.claim_number == claim.claim_number,
                AuditLog.entity_id == claim.claim_number,
                AuditLog.claim_number == claim.id,
                AuditLog.entity_id == claim_id,
                AuditLog.claim_number == claim_id,
            )
        )
        .order_by(AuditLog.timestamp.asc())
    )
    res_audit = await db.execute(audit_query)
    audit_entries = res_audit.scalars().all()
    audit_responses = [AuditLogResponse.model_validate(e) for e in audit_entries]

    # 2. Fetch Screenshots for visual exception diagnostics
    ss_query = (
        select(ErrorScreenshot)
        .where(ErrorScreenshot.claim_id == claim.id)
        .order_by(ErrorScreenshot.created_at.asc())
    )
    res_ss = await db.execute(ss_query)
    ss_records = res_ss.scalars().all()

    # 3. Build Processing Logs from creation + audit trail + action timings
    processing_logs: list[ProcessingLogEntry] = []

    # Record registration event
    processing_logs.append(
        ProcessingLogEntry(
            timestamp=claim.created_at.isoformat() if claim.created_at else None,
            level="INFO",
            stage="ingest",
            portal_key=None,
            message=f"Claim {claim.claim_number} registered in system by {claim.created_by or 'system'}",
            actor=claim.created_by or "system",
            details={
                "batch_id": claim.batch_id,
                "policy_state": claim.policy_state,
                "loss_location_state": claim.loss_location_state,
            },
        )
    )

    # Process events from AuditLog entries
    for a in audit_entries:
        level = "ERROR" if a.status in ("FAILURE", "FAILED") else ("WARNING" if a.status in ("WARNING", "MANUAL_REVIEW") else "INFO")
        stage = None
        portal_key = None
        if isinstance(a.details, dict):
            portal_key = a.details.get("portal_key") or a.details.get("portal")
            stage = a.details.get("stage")

        if not stage:
            act = a.action.lower()
            if "ingest" in act or "create" in act:
                stage = "ingest"
            elif "scrap" in act or "bot" in act or "browser" in act:
                stage = "scraping"
            elif "fuzzy" in act or "match" in act:
                stage = "fuzzy_matching"
            elif "guidewire" in act:
                stage = "guidewire_trigger"
            else:
                stage = "orchestrator"

        processing_logs.append(
            ProcessingLogEntry(
                timestamp=a.timestamp.isoformat() if a.timestamp else None,
                level=level,
                stage=stage,
                portal_key=portal_key,
                message=a.description,
                actor=a.user_email or a.user_id or "system",
                details=a.details if isinstance(a.details, dict) else None,
            )
        )

    # Add stages from claim.action_timings if available
    if claim.action_timings and isinstance(claim.action_timings, dict):
        stages = claim.action_timings.get("stages", {})
        if isinstance(stages, dict):
            for s_key, s_val in stages.items():
                if isinstance(s_val, dict):
                    processing_logs.append(
                        ProcessingLogEntry(
                            timestamp=s_val.get("start_time"),
                            level="ERROR" if s_val.get("status") == "FAILED" else "INFO",
                            stage=s_key,
                            portal_key=None,
                            message=f"Stage '{s_val.get('name', s_key)}' {s_val.get('status', 'COMPLETED')} ({s_val.get('duration_seconds', 0)}s): {s_val.get('detail', '')}",
                            actor="worker:scrapers",
                            details=s_val,
                        )
                    )

    # 4. Build Exception Logs
    exception_logs: list[ExceptionLogEntry] = []

    # Exceptions from Screenshots
    for ss in ss_records:
        exception_logs.append(
            ExceptionLogEntry(
                id=ss.id,
                timestamp=ss.created_at.isoformat() if ss.created_at else None,
                portal_key=ss.portal_key,
                portal_name=ss.portal_name,
                exception_type="BrowserExecutionError",
                message=ss.exception_message or "Scraper error captured in browser",
                stack_trace=None,
                page_url=ss.page_url,
                screenshot_url=f"/api/v1/claims/{claim.id}/screenshots/{ss.id}/image",
                attempt_number=ss.attempt_number or 1,
            )
        )

    # Exceptions from AuditLog (FAILED / ERROR)
    for a in audit_entries:
        if a.status in ("FAILURE", "FAILED") or "EXCEPTION" in a.action or "FAIL" in a.action:
            stack_trace = None
            portal_key = None
            portal_name = None
            ex_type = a.action
            if isinstance(a.details, dict):
                stack_trace = a.details.get("traceback") or a.details.get("stack_trace")
                portal_key = a.details.get("portal_key")
                portal_name = a.details.get("portal_name")
                ex_type = a.details.get("exception_type", a.action)

            # Avoid exact duplicates if screenshot already captured this
            if not any(el.portal_key == portal_key and el.message == a.description for el in exception_logs):
                exception_logs.append(
                    ExceptionLogEntry(
                        id=f"audit-{a.id}",
                        timestamp=a.timestamp.isoformat() if a.timestamp else None,
                        portal_key=portal_key,
                        portal_name=portal_name,
                        exception_type=ex_type,
                        message=(a.details.get("error_message") if isinstance(a.details, dict) and a.details.get("error_message") else a.description) or "Error logged in audit trail",
                        stack_trace=stack_trace,
                        page_url=None,
                        screenshot_url=None,
                        attempt_number=None,
                    )
                )

    # If claim.last_error exists and no exception captured yet
    if claim.last_error and not exception_logs:
        exception_logs.append(
            ExceptionLogEntry(
                id=f"err-{claim.id}",
                timestamp=claim.updated_at.isoformat() if claim.updated_at else None,
                portal_key=None,
                portal_name=None,
                exception_type="ClaimExecutionError",
                message=claim.last_error,
                stack_trace=None,
                page_url=None,
                screenshot_url=None,
                attempt_number=claim.retry_count,
            )
        )

    # 5. Read all portal terminal logs
    portal_logs: dict[str, str] = {}
    claim_logs_dir = settings.LOGS_DIR / str(claim.id)
    if claim_logs_dir.exists() and claim_logs_dir.is_dir():
        for p_dir in claim_logs_dir.iterdir():
            if p_dir.is_dir():
                log_file = p_dir / "execution.log"
                if log_file.exists():
                    try:
                        with open(log_file, encoding="utf-8", errors="replace") as lf:
                            portal_logs[p_dir.name] = lf.read()
                    except Exception as e:
                        portal_logs[p_dir.name] = f"Error reading log file: {e}"

    return ClaimCombinedLogsResponse(
        claim_id=claim.id,
        claim_number=claim.claim_number,
        created_at=claim.created_at,
        created_on=claim.created_at,
        created_by=claim.created_by or "system",
        updated_at=claim.updated_at,
        modified_on=claim.updated_at,
        modified_by=claim.modified_by or "system",
        total_duration_seconds=claim.total_duration_seconds,
        record_status=claim.record_status,
        fuzzy_match_status=claim.fuzzy_match_status,
        audit_logs=audit_responses,
        processing_logs=processing_logs,
        exception_logs=exception_logs,
        portal_logs=portal_logs,
    )


@router.get("/{claim_id}/export")
async def export_single_claim(
    claim_id: str,
    format: str = Query("xlsx", pattern="^(xlsx|csv|json|pdf)$"),
    db: AsyncSession = Depends(get_db),
):
    """Export single claim record, all scraped court cases, and fuzzy matches in Excel, CSV, JSON, or PDF format."""
    query = select(ClaimRecord).where(ClaimRecord.id == claim_id).options(
        selectinload(ClaimRecord.scraped_cases),
        selectinload(ClaimRecord.match_pairs),
    )
    res = await db.execute(query)
    claim = res.scalar_one_or_none()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    import json
    c_num = claim.claim_number.replace(" ", "_").replace("/", "_")
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # 1. JSON Export
    if format == "json":
        claim_dict = _map_claim_to_response(claim).model_dump()
        json_str = json.dumps(claim_dict, default=str, indent=2)
        return Response(
            content=json_str.encode("utf-8"),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=claim_{c_num}_{timestamp}.json"},
        )

    # 2. CSV Export (Scraped Court Cases with complete claim metadata & lossless JSON parity)
    case_rows = []
    insured = f"{claim.insured_first_name or ''} {claim.insured_last_name or ''}".strip()
    claimant = f"{claim.claimant_first_name or ''} {claim.claimant_last_name or ''}".strip()
    driver = f"{claim.driver_first_name or ''} {claim.driver_last_name or ''}".strip()
    rec_status = claim.record_status.value if hasattr(claim.record_status, "value") else str(claim.record_status)
    fuzzy_status = claim.fuzzy_match_status.value if hasattr(claim.fuzzy_match_status, "value") else str(claim.fuzzy_match_status)
    loss_loc = f"{claim.loss_location_state or ''}".strip(", ")
    gw_pushed = "Yes" if getattr(claim, "guidewire_pushed", False) else "No"
    duration_str = str(claim.total_duration_seconds or "")
    created_at_str = claim.created_at.strftime("%Y-%m-%d %H:%M:%S") if claim.created_at else ""

    bot_broward = str(claim.fl_botstatus_broward.value if hasattr(claim.fl_botstatus_broward, "value") else claim.fl_botstatus_broward)
    bot_hills = str(claim.fl_botstatus_hillsborough.value if hasattr(claim.fl_botstatus_hillsborough, "value") else claim.fl_botstatus_hillsborough)
    bot_miami = str(claim.fl_botstatus_miami.value if hasattr(claim.fl_botstatus_miami, "value") else claim.fl_botstatus_miami)
    bot_travis = str(claim.te_botstatus_travis.value if hasattr(claim.te_botstatus_travis, "value") else claim.te_botstatus_travis)
    bot_dallas = str(claim.te_botstatus_dallas.value if hasattr(claim.te_botstatus_dallas, "value") else claim.te_botstatus_dallas)
    bot_harris = str(claim.te_botstatus_harris.value if hasattr(claim.te_botstatus_harris, "value") else claim.te_botstatus_harris)
    bot_cclerk = str(claim.te_botstatus_cclerk.value if hasattr(claim.te_botstatus_cclerk, "value") else claim.te_botstatus_cclerk)
    bot_hcdistrict = str(getattr(claim, "te_botstatus_hcdistrict", "") or "")

    if claim.scraped_cases:
        for c in claim.scraped_cases:
            f_date = c.filing_date or (
                c.raw_payload.get("FilingDate")
                or c.raw_payload.get("filing_date")
                or c.raw_payload.get("Filing Date")
                or c.raw_payload.get("SuitFiledDate")
                or c.raw_payload.get("suit_filed_date")
                or c.raw_payload.get("DateFiled")
                or c.raw_payload.get("date_filed")
                or c.raw_payload.get("Filed")
                or c.raw_payload.get("filed")
                or c.raw_payload.get("filed_date")
                if isinstance(c.raw_payload, dict)
                else None
            ) or ""
            best_match = next(
                (m for m in (claim.match_pairs or []) if (hasattr(m, "court_case_id") and m.court_case_id == c.id) or (getattr(m, "case_style", "") == c.case_style)),
                None
            )
            raw_json_str = json.dumps(c.raw_payload or {}, default=str)

            case_rows.append({
                "Claim Number": claim.claim_number,
                "Exposure Number": claim.exposure_number or "1",
                "Primary Key": claim.primary_key or "",
                "Date of Loss (DOL)": claim.dol or "",
                "Policy State": claim.policy_state or "",
                "Loss Location": loss_loc,
                "Insured First Name": claim.insured_first_name or "",
                "Insured Last Name": claim.insured_last_name or "",
                "Insured Party": insured or "N/A",
                "Claimant First Name": claim.claimant_first_name or "",
                "Claimant Last Name": claim.claimant_last_name or "",
                "Claimant Party": claimant or "N/A",
                "Driver First Name": claim.driver_first_name or "",
                "Driver Last Name": claim.driver_last_name or "",
                "Driver Party": driver or "N/A",
                "Record Status": rec_status,
                "Fuzzy Match Status": fuzzy_status,
                "Total Duration (Seconds)": duration_str,
                "Guidewire Pushed": gw_pushed,
                "Guidewire Activity ID": claim.activity_id or "None",
                "Case Number": c.case_number,
                "Case Style": c.case_style,
                "County": c.county_name,
                "Website URL": c.county_website,
                "Filing Date": f_date,
                "Case Status": c.case_status or "",
                "Case Type": c.case_type or "",
                "Best Match Party": getattr(best_match, "party_name", "") if best_match else "",
                "Best Match Score": getattr(best_match, "similarity_score", "") if best_match else "",
                "Match Review Status": (best_match.review_status.value if hasattr(best_match.review_status, "value") else str(best_match.review_status)) if best_match else "",
                "Bot Broward": bot_broward,
                "Bot Hillsborough": bot_hills,
                "Bot Miami": bot_miami,
                "Bot Travis": bot_travis,
                "Bot Dallas": bot_dallas,
                "Bot Harris JP": bot_harris,
                "Bot Harris Clerk": bot_cclerk,
                "Bot Harris District": bot_hcdistrict,
                "Created At": created_at_str,
                "Scraped At": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else "",
                "Raw Case Payload (JSON)": raw_json_str,
            })
    else:
        case_rows.append({
            "Claim Number": claim.claim_number,
            "Exposure Number": claim.exposure_number or "1",
            "Primary Key": claim.primary_key or "",
            "Date of Loss (DOL)": claim.dol or "",
            "Policy State": claim.policy_state or "",
            "Loss Location": loss_loc,
            "Insured First Name": claim.insured_first_name or "",
            "Insured Last Name": claim.insured_last_name or "",
            "Insured Party": insured or "N/A",
            "Claimant First Name": claim.claimant_first_name or "",
            "Claimant Last Name": claim.claimant_last_name or "",
            "Claimant Party": claimant or "N/A",
            "Driver First Name": claim.driver_first_name or "",
            "Driver Last Name": claim.driver_last_name or "",
            "Driver Party": driver or "N/A",
            "Record Status": rec_status,
            "Fuzzy Match Status": fuzzy_status,
            "Total Duration (Seconds)": duration_str,
            "Guidewire Pushed": gw_pushed,
            "Guidewire Activity ID": claim.activity_id or "None",
            "Case Number": "NO_CASES_FOUND",
            "Case Style": "",
            "County": "",
            "Website URL": "",
            "Filing Date": "",
            "Case Status": "",
            "Case Type": "",
            "Best Match Party": "",
            "Best Match Score": "",
            "Match Review Status": "",
            "Bot Broward": bot_broward,
            "Bot Hillsborough": bot_hills,
            "Bot Miami": bot_miami,
            "Bot Travis": bot_travis,
            "Bot Dallas": bot_dallas,
            "Bot Harris JP": bot_harris,
            "Bot Harris Clerk": bot_cclerk,
            "Bot Harris District": bot_hcdistrict,
            "Created At": created_at_str,
            "Scraped At": "",
            "Raw Case Payload (JSON)": "{}",
        })

    df_cases = pd.DataFrame(case_rows)

    if format == "csv":
        csv_bytes = df_cases.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=claim_{c_num}_cases_{timestamp}.csv"},
        )

    # 3. XLSX Export (Multi-sheet: Overview, Scraped Cases, Matches, Telemetry, 8 Bots Status, Raw JSON)
    if format == "xlsx":
        out = io.BytesIO()
        claim_dict = _map_claim_to_response(claim).model_dump()
        full_json_str = json.dumps(claim_dict, default=str, indent=2)

        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            # Sheet 1: Claim Overview
            overview_data = [
                {"Field": "Claim Number", "Value": claim.claim_number},
                {"Field": "Primary Key", "Value": claim.primary_key or ""},
                {"Field": "Exposure Number", "Value": claim.exposure_number or "1"},
                {"Field": "Date of Loss (DOL)", "Value": claim.dol or ""},
                {"Field": "Policy State", "Value": claim.policy_state or ""},
                {"Field": "Loss Location", "Value": loss_loc},
                {"Field": "Insured Party", "Value": insured or "N/A"},
                {"Field": "Claimant Party", "Value": claimant or "N/A"},
                {"Field": "Driver (Insured Vehicle)", "Value": driver or "N/A"},
                {"Field": "Record Status", "Value": rec_status},
                {"Field": "Fuzzy Match Status", "Value": fuzzy_status},
                {"Field": "Total Duration (seconds)", "Value": duration_str},
                {"Field": "Guidewire Pushed", "Value": gw_pushed},
                {"Field": "Guidewire Activity ID", "Value": claim.activity_id or "None"},
                {"Field": "Total Cases Scraped", "Value": len(claim.scraped_cases)},
                {"Field": "Created At", "Value": created_at_str},
                {"Field": "Bot Broward", "Value": bot_broward},
                {"Field": "Bot Hillsborough", "Value": bot_hills},
                {"Field": "Bot Miami", "Value": bot_miami},
                {"Field": "Bot Travis", "Value": bot_travis},
                {"Field": "Bot Dallas", "Value": bot_dallas},
                {"Field": "Bot Harris JP", "Value": bot_harris},
                {"Field": "Bot Harris Clerk", "Value": bot_cclerk},
                {"Field": "Bot Harris District", "Value": bot_hcdistrict},
            ]
            pd.DataFrame(overview_data).to_excel(writer, index=False, sheet_name="Claim Overview")

            # Sheet 2: Scraped Cases (All Columns)
            df_cases.to_excel(writer, index=False, sheet_name="Scraped Court Cases")

            # Sheet 3: Matches
            match_rows = []
            for m in claim.match_pairs:
                case_num = (
                    m.court_case.case_number
                    if hasattr(m, "court_case") and m.court_case
                    else "N/A"
                )
                case_style = (
                    m.case_style
                    or (m.court_case.case_style if hasattr(m, "court_case") and m.court_case else "")
                )
                county = (
                    m.court_case.county_name
                    if hasattr(m, "court_case") and m.court_case
                    else ""
                )
                status_val = (
                    m.review_status.value
                    if hasattr(m, "review_status") and hasattr(m.review_status, "value")
                    else str(getattr(m, "review_status", "PENDING_REVIEW"))
                )
                party_type_val = (
                    m.party_type.value
                    if hasattr(m, "party_type") and hasattr(m.party_type, "value")
                    else str(getattr(m, "party_type", ""))
                )
                match_rows.append({
                    "Case Number": case_num,
                    "Case Style": case_style,
                    "County": county,
                    "Party Type": party_type_val,
                    "Party Name": getattr(m, "party_name", ""),
                    "Similarity Score": getattr(m, "similarity_score", 0.0),
                    "Threshold Applied": getattr(m, "threshold_applied", 0.60),
                    "Is Match": "Yes" if getattr(m, "is_match", False) else "No",
                    "Review Status": status_val,
                    "Reviewed By": getattr(m, "reviewed_by", None) or "Automated",
                    "Review Notes": getattr(m, "review_notes", None) or "",
                })
            pd.DataFrame(match_rows or [{"Note": "No match records evaluated yet"}]).to_excel(writer, index=False, sheet_name="Fuzzy Matches")

            # Sheet 4: Execution Telemetry
            stages_data = []
            timings = claim.action_timings or {}
            stages = timings.get("stages", {})
            for sk, sval in stages.items():
                if isinstance(sval, dict):
                    stages_data.append({
                        "Stage Key": sk,
                        "Stage Name": sval.get("name", sk),
                        "Start Time": sval.get("start_time", ""),
                        "End Time": sval.get("end_time", ""),
                        "Duration (s)": sval.get("duration_seconds", ""),
                        "Status": sval.get("status", ""),
                        "Detail": sval.get("detail") or sval.get("url") or sval.get("party") or "",
                    })
            pd.DataFrame(stages_data or [{"Note": "No stage telemetry recorded"}]).to_excel(writer, index=False, sheet_name="Stage Telemetry")

            # Sheet 5: 8 Bots Scraper Status
            bots_list = _build_bot_details(claim)
            bots_data = [
                {
                    "County Portal": b.name,
                    "Website URL": b.website_url,
                    "Target For Policy": b.target,
                    "Execution Status": b.status.value if hasattr(b.status, "value") else str(b.status),
                    "Cases Found": b.cases_found,
                }
                for b in bots_list
            ]
            pd.DataFrame(bots_data).to_excel(writer, index=False, sheet_name="8 Bots Status")

            # Sheet 6: Full Raw JSON
            pd.DataFrame([{"Raw JSON Payload": full_json_str}]).to_excel(writer, index=False, sheet_name="Complete Raw JSON")

        out.seek(0)
        return Response(
            content=out.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=claim_{c_num}_report_{timestamp}.xlsx"},
        )

    # 4. PDF (Full high-fidelity authentic vector PDF rendering)
    if format == "pdf":
        try:
            pdf_bytes = await asyncio.to_thread(_render_claim_pdf_sync, claim_id)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=claim_{c_num}_report_{timestamp}.pdf",
                    "Content-Length": str(len(pdf_bytes)),
                },
            )
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Error generating Playwright PDF export:\n{tb}")
            print(f"[PDF_EXPORT_ERROR]\n{tb}", flush=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate PDF report: {type(e).__name__}: {str(e) or repr(e)}"
            )


def _render_claim_pdf_sync(claim_id: str) -> bytes:
    """Renders authentic vector PDF using synchronous Playwright in a worker thread.
    
    Bypasses Windows asyncio SelectorEventLoop subprocess limitations.
    """
    from playwright.sync_api import sync_playwright

    frontend_url = f"http://localhost:3000/claims/{claim_id}?pdf_export=true"
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            viewport={"width": 1400, "height": 900},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.emulate_media(media="screen")
        page.goto(frontend_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_selector("#claim-detail-container", timeout=20000)
        page.wait_for_timeout(500)
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "6mm", "bottom": "6mm", "left": "6mm", "right": "6mm"},
        )
        browser.close()
        return pdf_bytes
