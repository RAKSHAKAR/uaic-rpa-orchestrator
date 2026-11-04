import asyncio
import logging
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.services.audit_service import log_audit_event_async
from sqlalchemy import select

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retrigger_failed_claims")

PORTAL_FIELDS = [
    "fl_botstatus_broward",
    "fl_botstatus_hillsborough",
    "fl_botstatus_miami",
    "te_botstatus_travis",
    "te_botstatus_dallas",
    "te_botstatus_harris",
    "te_botstatus_cclerk",
    "te_botstatus_hcdistrict",
]

async def main(target_mode: str = "all"):
    """
    Resets failed claims so they become eligible for fresh automated execution.
    target_mode: 'production' (only real customer claims) or 'all' (all 71 failed claims).
    """
    async with TaskAsyncSessionLocal() as session:
        claims = (await session.execute(select(ClaimRecord))).scalars().all()
        failed_claims = [c for c in claims if c.record_status == RecordStatusEnum.FAILED]
                
        logger.info(f"Discovered {len(failed_claims)} failed claims in database.")
        if not failed_claims:
            logger.info("No failed claims found to reset.")
            return

        retriggered_count = 0
        skipped_count = 0
        claim_numbers_retriggered = []

        for claim in failed_claims:
            # If target_mode is production, skip synthetic test claims
            is_synthetic_test = any(claim.claim_number.startswith(pfx) for pfx in ("FST-", "EXT-", "HIL-TEST", "FLEET-", "TEST-"))
            if target_mode == "production" and is_synthetic_test:
                skipped_count += 1
                continue

            # Reset state
            claim.record_status = RecordStatusEnum.NEW
            claim.retry_count = 0
            claim.last_error = None
            claim.modified_by = "script:retrigger_failed_claims"

            # Reset individual portal bot statuses if they failed or were blocked
            for field in PORTAL_FIELDS:
                current_st = getattr(claim, field, None)
                if current_st in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED, BotStatusEnum.IN_PROGRESS):
                    setattr(claim, field, BotStatusEnum.NOT_TRIGGERED)

            retriggered_count += 1
            claim_numbers_retriggered.append(claim.claim_number)

            await log_audit_event_async(
                session=session,
                action="CLAIM_RETRIGGERED",
                entity_type="CLAIM",
                description=f"Claim {claim.claim_number} reset from FAILED to NEW with retry_count=0 for fresh automated execution.",
                entity_id=claim.id,
                claim_number=claim.claim_number,
                user_id="operator_retrigger",
                user_email="system:recovery",
                status="SUCCESS",
                details={"previous_status": "FAILED", "new_status": "NEW"},
            )

        await session.commit()

        logger.info("\n=======================================================")
        logger.info(" RECOVERY SUMMARY:")
        logger.info(f"   Mode:                {target_mode.upper()}")
        logger.info(f"   Successfully Reset:  {retriggered_count} claims")
        logger.info(f"   Skipped (Test):      {skipped_count} claims")
        logger.info("   New Record Status:   NEW (Ready for queue processing)")
        logger.info("=======================================================")
        if claim_numbers_retriggered[:10]:
            logger.info(f"Sample reset claims: {', '.join(claim_numbers_retriggered[:10])}...")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    asyncio.run(main(mode))
