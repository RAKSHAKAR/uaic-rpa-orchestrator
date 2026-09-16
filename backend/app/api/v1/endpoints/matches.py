"""Fuzzy Match Review and Exception Handling Endpoints."""

import io
import json
import time
from datetime import UTC, datetime
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from rapidfuzz import fuzz
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import get_db
from app.models.claim import ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum
from app.schemas.match import (
    DirectFuzzyMatchRequest,
    DirectFuzzyMatchResponse,
    ExtractNamesResponse,
    FuzzyMatchItem,
    FuzzyMatchScore,
    FuzzySearchRequest,
    FuzzySearchResponse,
    MatchPairResponse,
    MatchReviewRequest,
    UniqueNameItem,
    UniqueNamesRequest,
    UniqueNamesResponse,
)
from app.services.audit_service import extract_client_context, log_audit_event_async
from app.services.fuzzy_engine import (
    generate_unique_names_for_claim,
    is_case_eligible,
)

router = APIRouter()


@router.get("/pending", response_model=list[MatchPairResponse])
async def list_pending_match_reviews(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all match candidate pairs currently flagged for manual review."""
    query = (
        select(MatchPair)
        .where(MatchPair.review_status == MatchReviewStatusEnum.PENDING_REVIEW)
        .options(selectinload(MatchPair.court_case))
        .order_by(desc(MatchPair.similarity_score))
        .limit(limit)
    )
    res = await db.execute(query)
    match_pairs = res.scalars().all()

    output = []
    for mp in match_pairs:
        output.append(
            MatchPairResponse(
                id=mp.id,
                claim_id=mp.claim_id,
                court_case_id=mp.court_case_id,
                party_type=mp.party_type,
                party_name=mp.party_name,
                case_style=mp.case_style,
                county_name=mp.court_case.county_name if mp.court_case else "Unknown",
                case_number=mp.court_case.case_number if mp.court_case else "Unknown",
                filing_date=mp.court_case.filing_date if mp.court_case else None,
                county_website=mp.court_case.county_website if mp.court_case else None,
                similarity_score=mp.similarity_score,
                threshold_applied=mp.threshold_applied,
                is_match=mp.is_match,
                review_status=mp.review_status,
                reviewed_by=mp.reviewed_by,
                reviewed_at=mp.reviewed_at,
                review_notes=mp.review_notes,
                created_at=mp.created_at,
            )
        )
    return output


@router.post("/{match_pair_id}/review")
async def review_match_pair(
    match_pair_id: str,
    payload: MatchReviewRequest,
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Manually approve or reject a borderline fuzzy match pair."""
    query = select(MatchPair).where(MatchPair.id == match_pair_id).options(selectinload(MatchPair.court_case))
    res = await db.execute(query)
    match_pair = res.scalar_one_or_none()
    
    if not match_pair:
        raise HTTPException(status_code=404, detail="Match pair not found")

    match_pair.review_status = payload.decision
    match_pair.reviewed_by = payload.reviewed_by
    match_pair.reviewed_at = datetime.now(UTC)
    match_pair.review_notes = payload.review_notes

    # Update associated claim status if approved
    claim_q = select(ClaimRecord).where(ClaimRecord.id == match_pair.claim_id)
    claim_res = await db.execute(claim_q)
    claim = claim_res.scalar_one_or_none()

    if claim:
        if payload.decision == MatchReviewStatusEnum.APPROVED:
            claim.record_status = RecordStatusEnum.MATCH_FOUND
            # If approved, dispatch Guidewire activity creation task
            matched_payload = {
                "CaseNumber": match_pair.court_case.case_number if match_pair.court_case else "",
                "CaseStyle": match_pair.case_style,
                "CountyWebsite": match_pair.court_case.county_website if match_pair.court_case else "",
                "SuitFiledDate": match_pair.court_case.filing_date if match_pair.court_case else "",
            }
            claim.final_matched_json = {"CaseItems": [matched_payload]}
            
            celery_app.send_task(
                "app.tasks.fuzzy_tasks.notify_guidewire_task",
                args=[claim.id],
                queue="notifications",
            )
        elif payload.decision == MatchReviewStatusEnum.REJECTED:
            # Check if there are other pending reviews for this claim
            other_q = (
                select(MatchPair)
                .where(MatchPair.claim_id == claim.id)
                .where(MatchPair.id != match_pair.id)
                .where(MatchPair.review_status == MatchReviewStatusEnum.PENDING_REVIEW)
            )
            other_res = await db.execute(other_q)
            if not other_res.scalars().first():
                claim.record_status = RecordStatusEnum.NO_MATCH_FOUND

    ctx = extract_client_context(request)
    await log_audit_event_async(
        session=db,
        action="MATCH_REVIEWED",
        entity_type="MATCH",
        description=f"Match review {payload.decision.value} for {match_pair.party_name} ({match_pair.case_style})",
        entity_id=match_pair_id,
        claim_number=claim.claim_number if claim else None,
        user_id=payload.reviewed_by or ctx["user_id"],
        user_email=ctx["user_email"],
        ip_address=ctx["ip_address"],
        user_agent=ctx["user_agent"],
        status="SUCCESS",
        details={
            "decision": payload.decision.value,
            "similarity_score": match_pair.similarity_score,
            "party_type": match_pair.party_type.value if hasattr(match_pair.party_type, "value") else str(match_pair.party_type),
            "review_notes": payload.review_notes,
        },
    )

    await db.commit()
    return {"message": f"Match pair successfully updated to {payload.decision.value}", "id": match_pair_id}


@router.get("/extract-names", response_model=ExtractNamesResponse)
async def extract_unique_party_names(
    party_type: str = Query(
        "all",
        description="Which party type to return: all | insured | driver | claimant",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract unique full names from Insured, Driver, and Claimant fields across all claim records.
    Used by the frontend fuzzy match workflow to populate name-picker dropdowns.
    """
    result = await db.execute(
        select(
            ClaimRecord.insured_first_name,
            ClaimRecord.insured_last_name,
            ClaimRecord.driver_first_name,
            ClaimRecord.driver_last_name,
            ClaimRecord.claimant_first_name,
            ClaimRecord.claimant_last_name,
        )
    )
    rows = result.all()

    insured_names: set[str] = set()
    driver_names: set[str] = set()
    claimant_names: set[str] = set()

    for row in rows:
        ins_f, ins_l, drv_f, drv_l, clm_f, clm_l = row
        ins = " ".join(filter(None, [ins_f, ins_l])).strip()
        drv = " ".join(filter(None, [drv_f, drv_l])).strip()
        clm = " ".join(filter(None, [clm_f, clm_l])).strip()
        if ins:
            insured_names.add(ins)
        if drv:
            driver_names.add(drv)
        if clm:
            claimant_names.add(clm)

    insured_sorted = sorted(insured_names)
    driver_sorted = sorted(driver_names)
    claimant_sorted = sorted(claimant_names)

    if party_type == "insured":
        return ExtractNamesResponse(insured=insured_sorted, driver=[], claimant=[], total=len(insured_sorted))
    if party_type == "driver":
        return ExtractNamesResponse(insured=[], driver=driver_sorted, claimant=[], total=len(driver_sorted))
    if party_type == "claimant":
        return ExtractNamesResponse(insured=[], driver=[], claimant=claimant_sorted, total=len(claimant_sorted))

    total = len(insured_sorted) + len(driver_sorted) + len(claimant_sorted)
    return ExtractNamesResponse(
        insured=insured_sorted,
        driver=driver_sorted,
        claimant=claimant_sorted,
        total=total,
    )


@router.post("/fuzzy-search", response_model=FuzzySearchResponse)
async def legacy_fuzzy_search(
    payload: FuzzySearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Legacy Power Automate fuzzy match search.
    Searches a given name against all ScrapedCourtCase.case_style fields using
    RapidFuzz partial_ratio (threshold >= payload.threshold, default 0.60).
    Preserves the PA cascade logic: partial_ratio score mapped to [0,1].
    """
    t0 = time.perf_counter()

    search_name = payload.search_name.strip()
    if not search_name:
        raise HTTPException(status_code=422, detail="search_name must not be empty")

    threshold_score = payload.threshold  # [0.0 - 1.0]
    # Convert to rapidfuzz 0-100 scale internally
    rf_threshold = threshold_score * 100.0

    # Load all court cases (with optional year filter)
    q = select(ScrapedCourtCase)
    if payload.min_filing_year and payload.min_filing_year > 0:
        # Filter by filing date if stored; cases without dates are included by default
        pass  # Apply in Python layer since filing_date format varies

    res = await db.execute(q)
    cases = res.scalars().all()

    matches: list[FuzzyMatchItem] = []
    for case in cases:
        if not case.case_style:
            continue
        # Apply RapidFuzz partial_ratio (Power Automate legacy algorithm)
        score = fuzz.partial_ratio(search_name.lower(), case.case_style.lower())
        if score >= rf_threshold:
            # Filter by min filing year if applicable
            if payload.min_filing_year and case.filing_date:
                try:
                    year = int(case.filing_date[:4]) if len(case.filing_date) >= 4 else 0
                    if year > 0 and year < payload.min_filing_year:
                        continue
                except (ValueError, IndexError):
                    pass  # Include if date unparseable

            matches.append(
                FuzzyMatchItem(
                    court_case_id=case.id,
                    case_number=case.case_number,
                    case_style=case.case_style,
                    county_name=case.county_name,
                    county_website=case.county_website,
                    filing_date=case.filing_date,
                    case_status=case.case_status,
                    case_type=case.case_type,
                    similarity_score=round(score / 100.0, 4),
                    claim_id=case.claim_id,
                )
            )

    # Sort by similarity descending, then limit
    matches.sort(key=lambda m: m.similarity_score, reverse=True)
    limited = matches[: payload.limit]

    duration_ms = (time.perf_counter() - t0) * 1000.0

    return FuzzySearchResponse(
        matches=limited,
        total=len(limited),
        threshold_applied=threshold_score,
        search_name=search_name,
        duration_ms=round(duration_ms, 2),
    )


@router.get("/export")
async def export_match_reviews(
    format: str = Query("xlsx", pattern="^(xlsx|csv|json)$"),
    status: str | None = Query(None),
    limit: int = Query(5000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """
    Export fuzzy match exception candidate records to Excel (.xlsx), CSV, or JSON.
    Includes claim context, party information, court case details, and similarity score.
    """
    query = (
        select(MatchPair)
        .options(selectinload(MatchPair.court_case))
        .order_by(desc(MatchPair.similarity_score), desc(MatchPair.created_at))
        .limit(limit)
    )
    if status and status.upper() != "ALL":
        try:
            review_status_enum = MatchReviewStatusEnum(status.upper())
            query = query.where(MatchPair.review_status == review_status_enum)
        except ValueError:
            pass

    res = await db.execute(query)
    match_pairs = res.scalars().all()

    # Preload claim numbers if claim_ids exist
    claim_ids = [mp.claim_id for mp in match_pairs if mp.claim_id]
    claims_map: dict[str, str] = {}
    if claim_ids:
        c_res = await db.execute(
            select(ClaimRecord.id, ClaimRecord.claim_number).where(ClaimRecord.id.in_(claim_ids))
        )
        for c_id, c_num in c_res.all():
            claims_map[c_id] = c_num

    export_rows = []
    for mp in match_pairs:
        court = mp.court_case
        score_pct = round(mp.similarity_score * 100, 1) if mp.similarity_score is not None else 0.0
        review_stat = mp.review_status.value if hasattr(mp.review_status, "value") else str(mp.review_status)
        party_tp = mp.party_type.value if hasattr(mp.party_type, "value") else str(mp.party_type)

        export_rows.append({
            "Match ID": mp.id,
            "Claim Number": claims_map.get(mp.claim_id, ""),
            "Party Type": party_tp,
            "Party Name": mp.party_name or "",
            "Court Case Number": court.case_number if court else "Unknown",
            "County Name": court.county_name if court else "Unknown",
            "Case Style": mp.case_style or (court.case_style if court else ""),
            "Similarity Score (%)": score_pct,
            "Filing Date": court.filing_date if court and court.filing_date else "",
            "Case Status": court.case_status if court and court.case_status else "",
            "Case Type": court.case_type if court and court.case_type else "",
            "Review Status": review_stat,
            "Reviewed By": mp.reviewed_by or "",
            "Reviewed At": mp.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if mp.reviewed_at else "",
            "Review Notes": mp.review_notes or "",
            "County Website": court.county_website if court and court.county_website else "",
            "Created At": mp.created_at.strftime("%Y-%m-%d %H:%M:%S") if mp.created_at else "",
        })

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if format == "json":
        return Response(
            content=json.dumps(export_rows, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=exceptions_export_{timestamp}.json"},
        )

    df = pd.DataFrame(export_rows)

    if format == "csv":
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=exceptions_export_{timestamp}.csv"},
        )
    else:
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Fuzzy Exceptions")
            ws = writer.sheets["Fuzzy Exceptions"]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)
        out.seek(0)
        return Response(
            content=out.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=exceptions_export_{timestamp}.xlsx"},
        )


@router.post("/fuzzymatchapi", response_model=DirectFuzzyMatchResponse)
def fuzzy_match_direct(payload: DirectFuzzyMatchRequest) -> DirectFuzzyMatchResponse:
    """
    Direct legacy Power Automate Desktop fuzzy match endpoint parity (PowerAutomateSolutions/fuzzy-match-api).
    Supports:
    1. Canonical text1 vs text2 with RapidFuzz partial_ratio scoring and threshold comparison.
    2. Optional Minimum Case Filing Date filtering (filing_date vs min_filing_date) for Guidewire eligibility.
    3. Court cases batch evaluation (cases array) filtered strictly by Minimum Case Filing Date.
    4. Array target_strings evaluation (backward compatibility).
    """
    thresh = float(payload.threshold if payload.threshold is not None else 0.60)
    threshold_scaled = thresh * 100.0 if thresh <= 1.0 else thresh
    min_date_str = payload.min_filing_date or "2010-01-01"

    # Case 1: Backward compatibility with array evaluator (target_strings)
    if payload.target_strings is not None and len(payload.target_strings) > 0:
        norm_ref = (payload.reference_string or payload.text1 or "").strip().lower()
        matches = []
        for target in payload.target_strings:
            norm_target = target.strip().lower()
            score = float(fuzz.partial_ratio(norm_ref, norm_target))
            result = "Match Found" if score >= threshold_scaled else "No Match Found"
            matches.append(
                FuzzyMatchScore(
                    target_string=target,
                    result=result,
                    score=score,
                    guidewire_eligible=(result == "Match Found"),
                )
            )
        return DirectFuzzyMatchResponse(
            result="Match Found" if any(m.result == "Match Found" for m in matches) else "No Match Found",
            score=max((m.score for m in matches), default=0.0),
            reference_string=payload.reference_string or payload.text1,
            text1=payload.text1 or payload.reference_string,
            threshold_applied=threshold_scaled,
            matches=matches,
        )

    # Case 2: Batch court cases evaluation (cases array)
    if payload.cases is not None and len(payload.cases) > 0:
        t1 = (payload.text1 or payload.reference_string or "").strip()
        cases_results = []
        best_score = 0.0
        best_match_found = False

        for c in payload.cases:
            c_style = str(c.get("CaseStyle") or c.get("case_style") or c.get("text2") or "").strip()
            c_num = str(c.get("CaseNumber") or c.get("case_number") or "").strip()
            c_date = str(c.get("FilingDate") or c.get("filing_date") or "").strip()

            date_eligible = True
            filter_reason = None
            if c_date:
                date_eligible = is_case_eligible(c_date, case_status=None, case_type=None, min_filing_date=min_date_str)
                if not date_eligible:
                    filter_reason = f"Filing date '{c_date}' is prior to Minimum Case Filing Date '{min_date_str}'"

            case_score = float(fuzz.partial_ratio(t1.lower(), c_style.lower())) if t1 and c_style else 0.0
            text_matched = case_score >= threshold_scaled

            if not date_eligible:
                c_result = f"Filtered Out (Filing Date < {min_date_str})"
                gw_eligible = False
            elif text_matched:
                c_result = "Match Found"
                gw_eligible = True
                best_match_found = True
            else:
                c_result = "No Match Found"
                gw_eligible = False

            if case_score > best_score and date_eligible:
                best_score = case_score

            cases_results.append({
                "case_number": c_num,
                "case_style": c_style,
                "filing_date": c_date,
                "score": case_score,
                "result": c_result,
                "guidewire_eligible": gw_eligible,
                "filter_reason": filter_reason,
            })

        overall_result = "Match Found" if best_match_found else "No Match Found"
        eligible_count = sum(1 for c in cases_results if c.get("guidewire_eligible"))
        return DirectFuzzyMatchResponse(
            result=overall_result,
            score=best_score,
            text1=t1,
            threshold_applied=threshold_scaled,
            min_filing_date=min_date_str,
            guidewire_eligible=best_match_found,
            cases=cases_results,
            cases_results=cases_results,
            cases_evaluated=len(cases_results),
            eligible_for_guidewire=eligible_count,
        )

    # Case 3: Canonical text1 vs text2 parity (exact PowerAutomateSolutions/fuzzy-match-api)
    t1 = (payload.text1 or payload.reference_string or "").strip()
    t2 = (payload.text2 or "").strip()
    score = float(fuzz.partial_ratio(t1.lower(), t2.lower())) if t1 and t2 else 0.0
    text_matched = score >= threshold_scaled
    result = "Match Found" if text_matched else "No Match Found"
    guidewire_eligible = text_matched
    filter_reason = None

    # Apply Minimum Case Filing Date filter if filing_date is provided
    if payload.filing_date:
        date_eligible = is_case_eligible(payload.filing_date, case_status=None, case_type=None, min_filing_date=min_date_str)
        if not date_eligible:
            guidewire_eligible = False
            result = f"Filtered Out (Filing Date < {min_date_str})"
            filter_reason = f"Filing date '{payload.filing_date}' is prior to Minimum Case Filing Date '{min_date_str}'"

    return DirectFuzzyMatchResponse(
        result=result,
        score=score,
        text1=t1,
        text2=t2,
        threshold_applied=threshold_scaled,
        filing_date=payload.filing_date,
        min_filing_date=min_date_str,
        guidewire_eligible=guidewire_eligible,
        filter_reason=filter_reason,
    )


def _extract_party_name(party_input: Any) -> tuple[str, str]:
    """Extracts (first_name, last_name) from string or dictionary."""
    if not party_input:
        return "", ""
    if isinstance(party_input, str):
        parts = party_input.strip().split()
        if not parts:
            return "", ""
        if len(parts) == 1:
            return parts[0], parts[0]
        return parts[0], " ".join(parts[1:])
    if isinstance(party_input, dict):
        fn = (
            party_input.get("FirstName")
            or party_input.get("first_name")
            or party_input.get("fn")
            or party_input.get("First")
            or ""
        )
        ln = (
            party_input.get("LastName")
            or party_input.get("last_name")
            or party_input.get("ln")
            or party_input.get("Last")
            or ""
        )
        if not fn and not ln and party_input.get("name"):
            return _extract_party_name(party_input["name"])
        return str(fn).strip(), str(ln).strip()
    return "", ""


@router.post("/unique-names", response_model=UniqueNamesResponse)
async def generate_claim_unique_names(
    payload: UniqueNamesRequest,
    db: AsyncSession = Depends(get_db),
) -> UniqueNamesResponse:
    """
    Generates the deduplicated list of unique search names (Insured, Driver, Claimant)
    to be searched sequentially across all open county court portals.
    Supports either passing a claim_id (queries DB), 3-array JSON, or flat party names.
    """
    claim_record = None
    if payload.claim_id:
        res = await db.execute(select(ClaimRecord).where(ClaimRecord.id == payload.claim_id))
        claim_record = res.scalar_one_or_none()
        if not claim_record:
            raise HTTPException(status_code=404, detail=f"Claim record '{payload.claim_id}' not found")
        source_data = claim_record
    else:
        ins_f = payload.insured_first_name or ""
        ins_l = payload.insured_last_name or ""
        drv_f = payload.driver_first_name or ""
        drv_l = payload.driver_last_name or ""
        clm_f = payload.claimant_first_name or ""
        clm_l = payload.claimant_last_name or ""

        # Check array formats (Claimants, Insureds, Drivers)
        insureds_list = payload.Insureds or payload.insureds or []
        drivers_list = payload.Drivers or payload.drivers or []
        claimants_list = payload.Claimants or payload.claimants or []

        if not ins_l and insureds_list:
            ins_f, ins_l = _extract_party_name(insureds_list[0])
        if not drv_l and drivers_list:
            drv_f, drv_l = _extract_party_name(drivers_list[0])
        if not clm_l and claimants_list:
            clm_f, clm_l = _extract_party_name(claimants_list[0])

        # If driver was not specified at all, driver defaults to insured
        if not drv_l and ins_l:
            drv_f, drv_l = ins_f, ins_l

        source_data = {
            "insured_first_name": ins_f,
            "insured_last_name": ins_l,
            "driver_first_name": drv_f,
            "driver_last_name": drv_l,
            "claimant_first_name": clm_f,
            "claimant_last_name": clm_l,
        }

    unique_list = generate_unique_names_for_claim(
        source_data,
        fuzzy_threshold=payload.threshold,
        noise_patterns=payload.noise_patterns,
    )

    items = [
        UniqueNameItem(
            party_type=p["party_type"],
            first_name=p.get("first_name"),
            last_name=p.get("last_name"),
            full_name=p["full_name"],
            name=p.get("name") or p["full_name"],
            search_order=p["search_order"],
            target_number=p.get("target_number") or p["search_order"],
        )
        for p in unique_list
    ]

    return UniqueNamesResponse(
        unique_names=items,
        total_unique_names=len(items),
        count=len(items),
    )


@router.get("/claims/{claim_id}/unique-names", response_model=UniqueNamesResponse)
async def get_claim_unique_names_get(
    claim_id: str,
    threshold: float = Query(0.60, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
) -> UniqueNamesResponse:
    """Convenience GET endpoint to extract unique search names for a specific claim record."""
    req = UniqueNamesRequest(claim_id=claim_id, threshold=threshold)
    return await generate_claim_unique_names(req, db=db)


