"""Celery Fuzzy Matching and Guidewire Notification Tasks (Power Automate V4 Parity)."""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.guidewire import FilteredOutCase, GuidewireActivity
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum
from app.services.audit_service import log_audit_event_async
from app.services.fuzzy_engine import (
    clean_party_name,
    evaluate_case_against_parties,
    is_case_eligible,
)
from app.services.guidewire_client import GuidewireClient
from app.services.notification_service import NotificationService
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.tasks.fuzzy")


async def _async_evaluate_fuzzy_matches(claim_id: str):
    """Async helper to evaluate scraped court cases for a claim with RapidFuzz."""
    async with TaskAsyncSessionLocal() as session:
        claim_q = (
            select(ClaimRecord)
            .where(ClaimRecord.id == claim_id)
            .options(selectinload(ClaimRecord.scraped_cases))
        )
        res = await session.execute(claim_q)
        claim = res.scalar_one_or_none()
        if not claim:
            logger.error(f"Claim {claim_id} not found for fuzzy matching")
            return

        runtime_settings = await get_system_settings_async()
        matcher_cfg = runtime_settings.matcher

        start_fuzzy_t = time.perf_counter()
        start_fuzzy_iso = datetime.now().isoformat()

        claimant_name = clean_party_name(
            claim.claimant_first_name,
            claim.claimant_last_name,
            noise_patterns=matcher_cfg.clean_party_name_patterns,
        )
        insured_name = clean_party_name(
            claim.insured_first_name,
            claim.insured_last_name,
            noise_patterns=matcher_cfg.clean_party_name_patterns,
        )
        driver_name = clean_party_name(
            claim.driver_first_name,
            claim.driver_last_name,
            noise_patterns=matcher_cfg.clean_party_name_patterns,
        )

        positive_matches: list[dict[str, Any]] = []
        borderline_matches: list[dict[str, Any]] = []
        seen_positive_case_numbers = set()
        seen_borderline_case_numbers = set()

        for court_case in claim.scraped_cases:
            # Check eligibility: ONLY Minimum Case Filing Date (YYYY-MM-DD) is filtered as final data sent to Guidewire
            if not is_case_eligible(
                court_case.filing_date,
                case_status=None,
                case_type=None,
                min_filing_date=matcher_cfg.min_filing_date,
            ):
                logger.info(f"Skipping ineligible case {court_case.case_number} (Filing Date {court_case.filing_date} < minimum {matcher_cfg.min_filing_date})")
                filtered_case = FilteredOutCase(
                    id=uuid.uuid4(),
                    claim_id=claim.id,
                    case_number=court_case.case_number,
                    case_style=court_case.case_style or "UNKNOWN",
                    case_type=court_case.case_type,
                    case_status=court_case.case_status,
                    fuzzy_score=0.0,
                    exclusion_reasons={
                        "eligible": False,
                        "status": court_case.case_status,
                        "type": court_case.case_type,
                        "filing_date": court_case.filing_date,
                        "min_filing_date": matcher_cfg.min_filing_date,
                        "reason": f"Filing date {court_case.filing_date} is prior to Minimum Case Filing Date {matcher_cfg.min_filing_date}",
                    },
                )
                session.add(filtered_case)
                continue

            case_dict = {
                "CaseNumber": court_case.case_number,
                "CaseStyle": court_case.case_style,
                "CountyWebsite": court_case.county_website,
                "SuitFiledDate": court_case.filing_date,
            }

            evaluations = evaluate_case_against_parties(
                case_dict,
                claimant_name=claimant_name,
                insured_name=insured_name,
                driver_name=driver_name,
                threshold=matcher_cfg.auto_match_threshold,
                borderline_threshold=matcher_cfg.manual_review_threshold,
                scorer_algorithm=matcher_cfg.scorer_algorithm,
                noise_patterns=matcher_cfg.clean_party_name_patterns,
            )

            # Record all evaluated pairs for auditability in MatchPair table
            eval_map = {}
            for ev in evaluations:
                match_pair = MatchPair(
                    claim_id=claim.id,
                    court_case_id=court_case.id,
                    party_type=ev["party_type"],
                    party_name=ev["party_name"],
                    case_style=ev["case_style"],
                    similarity_score=ev["similarity_score"],
                    threshold_applied=ev["threshold_applied"],
                    is_match=ev["is_match"],
                    review_status=ev["review_status"],
                )
                session.add(match_pair)
                eval_map[ev["party_type"]] = ev

            # 3-Tier Sequence Priority mirroring Power Automate:
            # 1. Claimant First + Last against Case Style (threshold 0.6)
            # 2. If no match -> Insured First + Last against Case Style (threshold 0.6)
            # 3. If no match -> Driver First + Last against Case Style (threshold 0.6)
            case_matched = False
            for p_type in [PartyTypeEnum.CLAIMANT, PartyTypeEnum.INSURED, PartyTypeEnum.DRIVER]:
                ev = eval_map.get(p_type)
                if ev and ev.get("is_match"):
                    case_num = case_dict.get("CaseNumber") or ""
                    if case_num and case_num not in seen_positive_case_numbers:
                        seen_positive_case_numbers.add(case_num)
                        positive_matches.append(case_dict)
                    case_matched = True
                    break  # Stop checking other parties for this case!

            # If not a positive match, check for borderline review and persist FilteredOutCase audit
            if not case_matched:
                for p_type in [PartyTypeEnum.CLAIMANT, PartyTypeEnum.INSURED, PartyTypeEnum.DRIVER]:
                    ev = eval_map.get(p_type)
                    if ev and ev.get("review_status") == MatchReviewStatusEnum.PENDING_REVIEW:
                        case_num = case_dict.get("CaseNumber") or ""
                        if case_num and case_num not in seen_borderline_case_numbers:
                            seen_borderline_case_numbers.add(case_num)
                            borderline_matches.append(case_dict)
                        break

                max_score = max((ev["similarity_score"] for ev in evaluations), default=0.0)
                filtered_case = FilteredOutCase(
                    id=uuid.uuid4(),
                    claim_id=claim.id,
                    case_number=court_case.case_number,
                    case_style=court_case.case_style or "UNKNOWN",
                    case_type=court_case.case_type,
                    case_status=court_case.case_status,
                    fuzzy_score=round(float(max_score), 3),
                    exclusion_reasons={
                        "eligible": True,
                        "is_positive_match": False,
                        "reason": "Case did not meet positive match criteria across claimant, insured, or driver cascade",
                        "evaluations": [
                            {"party": str(ev["party_type"].value), "score": ev["similarity_score"]}
                            for ev in evaluations
                        ],
                    },
                )
                session.add(filtered_case)

        fuzzy_duration = round(time.perf_counter() - start_fuzzy_t, 2)
        timings = dict(claim.action_timings or {})
        timings["fuzzy_matching"] = {
            "start_time": start_fuzzy_iso,
            "end_time": datetime.now().isoformat(),
            "duration_seconds": fuzzy_duration,
            "positive_matches_count": len(positive_matches),
            "borderline_matches_count": len(borderline_matches),
            "scorer_algorithm": matcher_cfg.scorer_algorithm,
        }
        stages = timings.setdefault("stages", {})
        stages["fuzzy_matching"] = {
            "name": "RapidFuzz Matching",
            "start_time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "end_time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "duration_seconds": max(fuzzy_duration, 0.001),
            "status": "SUCCESS" if positive_matches else ("MANUAL_REVIEW" if borderline_matches else "NO_MATCH"),
            "positive_matches": len(positive_matches),
            "borderline_matches": len(borderline_matches),
            "detail": f"{len(positive_matches)} matched ({matcher_cfg.scorer_algorithm})",
        }
        claim.action_timings = timings

        # Update Claim Status based on results
        # Update Claim Status based on results
        if positive_matches:
            claim.record_status = RecordStatusEnum.MATCH_FOUND
            claim.fuzzy_match_status = FuzzyMatchStatusEnum.COMPLETED
            claim.final_matched_json = {"CaseItems": positive_matches}
            await session.commit()

            integ_cfg = runtime_settings.integration
            dispatch_mode = getattr(integ_cfg, "notification_dispatch_mode", "both").lower()

            # 1. Direct System Email Dispatch (if mode is 'direct_system' or 'both')
            if dispatch_mode in ("direct_system", "both"):
                try:
                    case_rows = []
                    for c in positive_matches:
                        c_num = c.get("CaseNumber", "N/A")
                        c_style = c.get("CaseStyle", "N/A")
                        c_type = c.get("CaseType", "CIVIL")
                        c_date = c.get("FilingDate", "N/A")
                        c_status = c.get("CaseStatus", "ACTIVE")
                        c_url = c.get("CountyWebsite", "#")
                        link_html = f'<a href="{c_url}" target="_blank" style="color: #0284c7; text-decoration: underline; font-weight: bold;">{c_num}</a>' if c_url != "#" else f'<strong>{c_num}</strong>'
                        case_rows.append(f"""
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                          <td style="padding: 8px; font-family: monospace; font-size: 12px;">{link_html}</td>
                          <td style="padding: 8px; font-size: 12px; color: #1e293b;">{c_style}</td>
                          <td style="padding: 8px; font-size: 11px; color: #64748b;">{c_type}</td>
                          <td style="padding: 8px; font-size: 12px; font-family: monospace;">{c_date}</td>
                          <td style="padding: 8px; font-size: 11px; font-weight: bold; color: #16a34a;">{c_status}</td>
                        </tr>
                        """)
                    cases_table_html = f"""
                    <table style="width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; border: 1px solid #cbd5e1; border-radius: 6px; overflow: hidden;">
                      <thead style="background-color: #f1f5f9; text-align: left; color: #475569; font-size: 11px; text-transform: uppercase;">
                        <tr>
                          <th style="padding: 8px;">Case Number</th>
                          <th style="padding: 8px;">Case Style</th>
                          <th style="padding: 8px;">Case Type</th>
                          <th style="padding: 8px;">Filing Date</th>
                          <th style="padding: 8px;">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {''.join(case_rows)}
                      </tbody>
                    </table>
                    """

                    await NotificationService.emit_event(
                        db=session,
                        event_type="COURT_CASE_MATCHED",
                        context={
                            "claim_number": claim.claim_number,
                            "exposure_number": claim.exposure_number or "001",
                            "insured_name": f"{claim.insured_first_name} {claim.insured_last_name}".strip(),
                            "claimant_name": f"{claim.claimant_first_name} {claim.claimant_last_name}".strip(),
                            "party_name": f"{claim.claimant_first_name} {claim.claimant_last_name}".strip(),
                            "matched_count": len(positive_matches),
                            "county_name": positive_matches[0].get("CountyWebsite", "Florida/Texas Court") if positive_matches else "Court Portal",
                            "matched_cases_table": cases_table_html,
                        },
                        claim_id=claim.id,
                        claim_number=claim.claim_number,
                        idempotency_key=f"COURT_CASE_MATCHED:{claim.id}",
                    )
                    logger.info(f"Claim {claim.claim_number}: Dispatched direct system match notification ({len(positive_matches)} cases).")
                except Exception as notif_err:
                    logger.warning(f"Direct match notification dispatch note: {notif_err}")

            # 2. Guidewire Integration Dispatch (if mode is 'guidewire_activity' or 'both')
            if dispatch_mode in ("guidewire_activity", "both") and integ_cfg.auto_push_on_match:
                logger.info(f"Claim {claim.claim_number}: Dispatching Guidewire notification task.")
                celery_app.send_task(
                    "app.tasks.fuzzy_tasks.notify_guidewire_task",
                    args=[claim.id],
                    queue="notifications",
                )
            else:
                if dispatch_mode == "direct_system":
                    claim.record_status = RecordStatusEnum.COMPLETED
                    await session.commit()
                    logger.info(f"Claim {claim.claim_number}: Match processing completed via direct system notification.")
                else:
                    logger.info(
                        f"Claim {claim.claim_number}: auto_push_on_match disabled or guidewire push bypassed. Advancing queue."
                    )
                from app.tasks.queue_runner import (
                    is_auto_queue_enabled,
                    remove_active_queue_item_id,
                )
                remove_active_queue_item_id(claim.id)
                if is_auto_queue_enabled():
                    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
        elif borderline_matches:
            claim.record_status = RecordStatusEnum.MANUAL_REVIEW
            claim.fuzzy_match_status = FuzzyMatchStatusEnum.PENDING_REVIEW
            total_sec = timings.get("total_scraping_seconds", 0.0) + fuzzy_duration
            claim.total_duration_seconds = round(total_sec, 2)
            await session.commit()
            logger.info(f"Claim {claim.claim_number}: {len(borderline_matches)} borderline matches flagged for manual review.")
        else:
            claim.record_status = RecordStatusEnum.NO_MATCH_FOUND
            claim.fuzzy_match_status = FuzzyMatchStatusEnum.NO_MATCH_FOUND
            total_sec = timings.get("total_scraping_seconds", 0.0) + fuzzy_duration
            claim.total_duration_seconds = round(total_sec, 2)
            await session.commit()
            logger.info(f"Claim {claim.claim_number}: No matching court cases found.")

        try:
            audit_desc = (
                f"RapidFuzz evaluation completed: {len(positive_matches)} positive matches, "
                f"{len(borderline_matches)} borderline matches (status: {claim.record_status.value})."
            )
            await log_audit_event_async(
                session=session,
                action="FUZZY_MATCHING_COMPLETED",
                entity_type="CLAIM",
                description=audit_desc,
                entity_id=claim.id,
                claim_number=claim.claim_number,
                user_id="celery_worker",
                user_email="orchestrator@system.local",
                status="SUCCESS" if positive_matches else ("MANUAL_REVIEW" if borderline_matches else "NO_MATCH"),
                details={
                    "positive_matches_count": len(positive_matches),
                    "borderline_matches_count": len(borderline_matches),
                    "algorithm": matcher_cfg.scorer_algorithm,
                    "duration_seconds": fuzzy_duration,
                },
            )
            await session.commit()
        except Exception as e_audit:
            logger.warning(f"Could not log audit event for fuzzy matching: {e_audit}")

        # Advance automatic queue if no positive matches are awaiting Guidewire dispatch
        if not positive_matches:
            from app.tasks.queue_runner import is_auto_queue_enabled, remove_active_queue_item_id
            remove_active_queue_item_id(claim.id)
            if is_auto_queue_enabled():
                celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")


@celery_app.task(name="app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task", bind=True, max_retries=3)
def evaluate_fuzzy_matches_task(self, claim_id: str):
    """Celery task entrypoint for RapidFuzz evaluation."""
    logger.info(f"Evaluating fuzzy matches for Claim {claim_id}")
    asyncio.run(_async_evaluate_fuzzy_matches(claim_id))


async def _async_notify_guidewire(claim_id: str):
    """Async helper to post match payload to Guidewire."""
    async with TaskAsyncSessionLocal() as session:
        claim_q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(claim_q)
        claim = res.scalar_one_or_none()
        if not claim or not claim.final_matched_json:
            logger.error(f"Cannot notify Guidewire: Claim {claim_id} has no matched payload")
            return

        runtime_settings = await get_system_settings_async()
        integ = runtime_settings.integration

        client = GuidewireClient(
            api_url=integ.guidewire_api_url,
            auth_type=integ.guidewire_auth_type,
            api_key=integ.guidewire_api_key,
            client_id=integ.guidewire_client_id,
            client_secret=integ.guidewire_client_secret,
            timeout=float(integ.guidewire_timeout_seconds),
            mock_mode=integ.guidewire_mock_mode,
        )
        matched_cases = claim.final_matched_json.get("CaseItems", [])
        start_gw_t = time.perf_counter()
        start_gw_iso = datetime.now().isoformat()
        gw_res = await client.send_case_update(
            claim_number=claim.claim_number,
            exposure_number=claim.exposure_number,
            matched_cases=matched_cases,
        )
        gw_duration = round(time.perf_counter() - start_gw_t, 2)

        timings = dict(claim.action_timings or {})
        timings["guidewire_dispatch"] = {
            "start_time": start_gw_iso,
            "end_time": datetime.now().isoformat(),
            "duration_seconds": gw_duration,
            "status": "SUCCESS" if gw_res.get("success") else "FAILED",
            "error": gw_res.get("error") if not gw_res.get("success") else None,
        }

        stages = timings.setdefault("stages", {})
        stages["guidewire_trigger"] = {
            "name": "Guidewire Trigger",
            "start_time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "end_time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "duration_seconds": max(gw_duration, 0.001),
            "status": "SUCCESS" if gw_res.get("success") else "FAILED",
            "detail": "Dispatched to Guidewire API" if gw_res.get("success") else str(gw_res.get("error")),
        }

        if gw_res.get("success"):
            claim.record_status = RecordStatusEnum.COMPLETED
            resp = gw_res.get("response", {})
            claim.activity_id = str(resp.get("ActivityID") or resp.get("activityId") or resp.get("activity_id") or "GW-AUTO-CREATED")
            timings["guidewire_dispatch"]["activity_id"] = claim.activity_id
            stages["guidewire_trigger"]["detail"] = f"Activity ID: {claim.activity_id}"

            # Async notification dispatch (isolated so email failure never affects Guidewire status)
            try:
                await NotificationService.emit_event(
                    db=session,
                    event_type="GUIDEWIRE_ACTIVITY_CREATED",
                    context={
                        "claim_number": claim.claim_number,
                        "exposure_number": claim.exposure_number or "001",
                        "activity_id": claim.activity_id,
                        "party_name": f"{claim.claimant_first_name} {claim.claimant_last_name}".strip(),
                        "matched_count": len(matched_cases),
                    },
                    claim_id=claim.id,
                    claim_number=claim.claim_number,
                    idempotency_key=f"GUIDEWIRE_ACTIVITY_CREATED:{claim.id}:{claim.activity_id}",
                )
            except Exception as notif_err:
                logger.warning(f"Notification dispatch note on Guidewire activity success: {notif_err}")
        else:
            claim.last_error = f"Guidewire notification error: {gw_res.get('error')}"
            timings["guidewire_dispatch"]["alert_recipient"] = integ.notification_email
            logger.warning(
                f"Guidewire push failed for Claim {claim.claim_number}: {gw_res.get('error')}. "
                f"Alert recipient: {integ.notification_email}"
            )

            # Async notification dispatch on failure
            try:
                await NotificationService.emit_event(
                    db=session,
                    event_type="GUIDEWIRE_ACTIVITY_FAILED",
                    context={
                        "claim_number": claim.claim_number,
                        "error_message": str(gw_res.get("error")),
                        "http_status": str(gw_res.get("status_code", "Unknown")),
                    },
                    claim_id=claim.id,
                    claim_number=claim.claim_number,
                    idempotency_key=f"GUIDEWIRE_ACTIVITY_FAILED:{claim.id}:{int(time.time())}",
                )
            except Exception as notif_err:
                logger.warning(f"Notification dispatch note on Guidewire activity failure: {notif_err}")

        try:
            gw_ok = bool(gw_res.get("success"))
            await log_audit_event_async(
                session=session,
                action="GUIDEWIRE_PUSH_SUCCESS" if gw_ok else "GUIDEWIRE_PUSH_FAILED",
                entity_type="CLAIM",
                description=f"Guidewire dispatch {'succeeded with activity ID ' + str(claim.activity_id) if gw_ok else 'failed: ' + str(gw_res.get('error'))}",
                entity_id=claim.id,
                claim_number=claim.claim_number,
                user_id="celery_worker",
                user_email="orchestrator@system.local",
                status="SUCCESS" if gw_ok else "FAILED",
                details={
                    "activity_id": claim.activity_id if gw_ok else None,
                    "exposure_number": claim.exposure_number,
                    "duration_seconds": gw_duration,
                    "error": gw_res.get("error") if not gw_ok else None,
                },
            )
        except Exception as e_audit:
            logger.warning(f"Could not log audit event for Guidewire push: {e_audit}")

        # Persist GuidewireActivity entity for downstream compliance & payload audit
        try:
            gw_ok = bool(gw_res.get("success"))
            activity_record = GuidewireActivity(
                id=uuid.uuid4(),
                claim_id=claim.id,
                transaction_id=uuid.uuid4(),
                claim_number=claim.claim_number,
                exposure_number=claim.exposure_number or "001",
                request_payload=gw_res.get("payload_sent") or {},
                response_payload=gw_res.get("response") or {"error": str(gw_res.get("error"))},
                http_status=gw_res.get("status_code", 200 if gw_ok else 500),
                status="SUCCESS" if gw_ok else "FAILED",
                guidewire_claim_id=claim.claim_number,
                guidewire_activity_id=claim.activity_id if gw_ok else None,
                error_details=str(gw_res.get("error")) if not gw_ok else None,
            )
            session.add(activity_record)
        except Exception as gw_act_err:
            logger.warning(f"Could not persist GuidewireActivity audit entity: {gw_act_err}")

        total_sec = (
            timings.get("total_scraping_seconds", 0.0) +
            timings.get("fuzzy_matching", {}).get("duration_seconds", 0.0) +
            gw_duration
        )
        claim.total_duration_seconds = round(total_sec, 2)
        claim.action_timings = timings

        await session.commit()

        # Advance automatic sequential queue runner
        from app.tasks.queue_runner import is_auto_queue_enabled, remove_active_queue_item_id
        remove_active_queue_item_id(claim.id)
        if is_auto_queue_enabled():
            celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")


@celery_app.task(
    name="app.tasks.fuzzy_tasks.notify_guidewire_task",
    bind=True,
    max_retries=5,
    default_retry_delay=30,
)
def notify_guidewire_task(self, claim_id: str):
    """Celery task for sending final activity payload to Guidewire with exponential backoff."""
    logger.info(f"Triggering Guidewire notification for Claim {claim_id}")
    try:
        asyncio.run(_async_notify_guidewire(claim_id))
    except Exception as exc:
        logger.error(f"Failed to notify Guidewire for claim {claim_id}: {exc}, retrying...")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 10)
