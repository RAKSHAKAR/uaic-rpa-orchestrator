"""Celery Ingestion Tasks for file parsing and batch creation."""

import asyncio
import logging

import pandas as pd
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, IngestionBatch, RecordStatusEnum
from app.services.excel_parser import (
    resolve_county_bot_targets,
    validate_and_normalize_claim_data,
)

logger = logging.getLogger("uaic_orchestrator.tasks.ingest")


async def _async_parse_and_ingest(
    batch_id: str,
    file_path: str,
    column_mapping: dict | None = None,
    duplicate_strategy: str = "SKIP",
):
    """Async helper to parse Excel/CSV file and populate database records with column mapping and duplicate rules."""
    async with TaskAsyncSessionLocal() as session:
        batch_q = select(IngestionBatch).where(IngestionBatch.id == batch_id)
        res = await session.execute(batch_q)
        batch = res.scalar_one_or_none()
        if not batch:
            logger.error(f"Ingestion batch {batch_id} not found")
            return

        try:
            # Query existing claim numbers for duplicate checks
            existing_res = await session.execute(select(ClaimRecord.claim_number))
            existing_claims = {str(c) for c in existing_res.scalars().all() if c}

            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path)

            norm_result = validate_and_normalize_claim_data(
                df=df,
                column_mapping=column_mapping,
                existing_claims=existing_claims,
                duplicate_strategy=duplicate_strategy,
            )

            batch.total_records = norm_result["total_rows"]
            batch.duplicate_records = norm_result["duplicate_rows"]
            batch.invalid_records = norm_result["invalid_rows"]
            batch.failed_rows_data = norm_result["failed_rows_list"]
            if column_mapping:
                batch.mapping_config = column_mapping

            created_claims = []
            for row in norm_result["records_to_insert"]:
                targets = resolve_county_bot_targets(
                    row.get("Policy State") or row.get("policy_state"),
                    row.get("Loss Location State") or row.get("loss_location_state"),
                )

                claim = ClaimRecord(
                    batch_id=batch_id,
                    claim_number=row.get("Claim Number") or row.get("claim_number"),
                    exposure_number=row.get("Exposure Number") or row.get("exposure_number"),
                    primary_key=row.get("Primary Key") or row.get("primary_key"),
                    dol=row.get("DOL") or row.get("dol"),
                    insured_first_name=row.get("Insured First Name") or row.get("insured_first_name"),
                    insured_last_name=row.get("Insured Last Name") or row.get("insured_last_name"),
                    claimant_first_name=row.get("Claimant First Name") or row.get("claimant_first_name"),
                    claimant_last_name=row.get("Claimant Last Name") or row.get("claimant_last_name"),
                    driver_first_name=row.get("Driver First Name (Insured Vehicle)") or row.get("driver_first_name"),
                    driver_last_name=row.get("Driver Last Name (Insured Vehicle)") or row.get("driver_last_name"),
                    loss_location_state=row.get("Loss Location State") or row.get("loss_location_state"),
                    policy_state=row.get("Policy State") or row.get("policy_state"),
                    record_status=RecordStatusEnum.NEW,
                    
                    # Target flags
                    fl_website_broward=targets["fl_broward"],
                    fl_website_hillsborough=targets["fl_hillsborough"],
                    fl_website_miami=targets["fl_miami"],
                    te_website_travis=targets["te_travis"],
                    te_website_dallas=targets["te_dallas"],
                    te_website_harris=targets["te_harris"],
                    te_website_cclerk=targets["te_cclerk"],
                    te_website_hcdistrict=targets["te_hcdistrict"],
                )
                session.add(claim)
                created_claims.append(claim)

            # Handle overwrite updates
            updated_claims = []
            for row in norm_result.get("records_to_update", []):
                claim_num = row.get("Claim Number") or row.get("claim_number")
                existing_claim_q = select(ClaimRecord).where(ClaimRecord.claim_number == claim_num)
                claim_res = await session.execute(existing_claim_q)
                target_claim = claim_res.scalars().first()
                if target_claim:
                    targets = resolve_county_bot_targets(
                        row.get("Policy State") or row.get("policy_state"),
                        row.get("Loss Location State") or row.get("loss_location_state"),
                    )
                    target_claim.batch_id = batch_id
                    target_claim.insured_first_name = row.get("Insured First Name") or row.get("insured_first_name")
                    target_claim.insured_last_name = row.get("Insured Last Name") or row.get("insured_last_name")
                    target_claim.claimant_first_name = row.get("Claimant First Name") or row.get("claimant_first_name")
                    target_claim.claimant_last_name = row.get("Claimant Last Name") or row.get("claimant_last_name")
                    target_claim.driver_first_name = row.get("Driver First Name (Insured Vehicle)") or row.get("driver_first_name")
                    target_claim.driver_last_name = row.get("Driver Last Name (Insured Vehicle)") or row.get("driver_last_name")
                    target_claim.loss_location_state = row.get("Loss Location State") or row.get("loss_location_state")
                    target_claim.policy_state = row.get("Policy State") or row.get("policy_state")
                    target_claim.record_status = RecordStatusEnum.NEW
                    target_claim.fl_website_broward = targets["fl_broward"]
                    target_claim.fl_website_hillsborough = targets["fl_hillsborough"]
                    target_claim.fl_website_miami = targets["fl_miami"]
                    target_claim.te_website_travis = targets["te_travis"]
                    target_claim.te_website_dallas = targets["te_dallas"]
                    target_claim.te_website_harris = targets["te_harris"]
                    target_claim.te_website_cclerk = targets["te_cclerk"]
                    target_claim.te_website_hcdistrict = targets["te_hcdistrict"]
                    updated_claims.append(target_claim)

            await session.commit()

            all_active_claims = created_claims + updated_claims
            for claim in all_active_claims:
                await session.refresh(claim)
                celery_app.send_task(
                    "app.tasks.scraper_tasks.orchestrate_court_scrapers_task",
                    args=[claim.id],
                    queue="scrapers",
                )

            batch.status = "COMPLETED"
            batch.processed_records = len(all_active_claims)
            batch.failed_records = norm_result["invalid_rows"] + (norm_result["duplicate_rows"] if duplicate_strategy == "SKIP" else 0)
            await session.commit()
            logger.info(
                f"Batch {batch_id} ingestion completed: {len(created_claims)} created, "
                f"{len(updated_claims)} updated, {norm_result['duplicate_rows']} duplicates, "
                f"{norm_result['invalid_rows']} invalid."
            )

        except Exception as e:
            await session.rollback()
            batch.status = "FAILED"
            batch.error_message = str(e)
            await session.commit()
            logger.error(f"Batch {batch_id} failed: {e}", exc_info=True)


@celery_app.task(name="app.tasks.ingest_tasks.parse_and_ingest_file_task", bind=True, max_retries=3)
def parse_and_ingest_file_task(
    self,
    batch_id: str,
    file_path: str,
    column_mapping: dict | None = None,
    duplicate_strategy: str = "SKIP",
):
    """Celery task entrypoint for background parsing with custom column mapping."""
    logger.info(f"Starting parsing task for batch {batch_id} from {file_path} (Strategy: {duplicate_strategy})")
    asyncio.run(_async_parse_and_ingest(batch_id, file_path, column_mapping, duplicate_strategy))

