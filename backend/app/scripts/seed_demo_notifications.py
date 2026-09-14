import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal
from app.models.notification import Notification


async def seed():
    async with AsyncSessionLocal() as session:
        # Clear existing demo notifications
        from sqlalchemy import delete
        await session.execute(delete(Notification))
        await session.commit()

        now = datetime.now(UTC)
        samples = [
            Notification(
                id="a1122334-5566-7788-99aa-bbccddeeff01",
                event_type="GUIDEWIRE_ACTIVITY_CREATED",
                claim_id="clm-001-fl",
                claim_number="0123456789",
                recipient="claims-ops@damcogroup.com",
                cc="supervisor@damcogroup.com",
                subject="Guidewire Activity Created - Claim 0123456789 (Exposure 001)",
                body_html="<p>Guidewire activity created successfully.</p>",
                provider="smtp",
                status="SENT",
                retry_count=0,
                created_at=now - timedelta(minutes=15),
                sent_at=now - timedelta(minutes=14, seconds=45),
                delivery_receipt={
                    "message_id": "<202609121330.a1122334@smtp.damcogroup.com>",
                    "smtp_relay": "smtp.damcogroup.com:587",
                    "tls_version": "TLSv1.3",
                    "cipher": "TLS_AES_256_GCM_SHA384",
                    "latency_ms": 142.8,
                    "gateway_status": "250 2.0.0 OK 1789200205 d8e7cef8-accepted",
                    "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                },
                details={
                    "claim_number": "0123456789",
                    "exposure_number": "001",
                    "activity_id": "ACT-99281-GW",
                    "party_name": "JOHNATHAN DOE",
                    "matched_count": 2,
                    "county": "Broward County",
                }
            ),
            Notification(
                id="b2233445-6677-8899-aabb-ccddeeff0012",
                event_type="COURT_CASE_MATCHED",
                claim_id="clm-002-tx",
                claim_number="0987654321",
                recipient="litigation-alerts@damcogroup.com",
                subject="Court Docket Match Discovered - Claim 0987654321 (2 Case(s))",
                body_html="<p>High confidence court docket match found.</p>",
                provider="graph_api",
                status="SENT",
                retry_count=0,
                created_at=now - timedelta(minutes=32),
                sent_at=now - timedelta(minutes=31, seconds=50),
                delivery_receipt={
                    "message_id": "<AAMkAGI2TX...microsoft.graph@damcogroup.com>",
                    "graph_endpoint": "https://graph.microsoft.com/v1.0/users/claims-ops@damcogroup.com/sendMail",
                    "latency_ms": 312.4,
                    "status_code": 202,
                    "gateway_status": "202 Accepted via Microsoft Graph API"
                },
                details={
                    "claim_number": "0987654321",
                    "matched_count": 2,
                    "county": "Harris County District",
                    "claimant_name": "JANE SMITH"
                }
            ),
            Notification(
                id="c3344556-7788-99aa-bbcc-ddeeff001122",
                event_type="GUIDEWIRE_ACTIVITY_FAILED",
                claim_id="clm-003-fl",
                claim_number="0445566778",
                recipient="claims-escalations@damcogroup.com",
                subject="Guidewire Activity Creation Failed - Claim 0445566778",
                body_html="<p>Guidewire API returned HTTP 503 Service Unavailable.</p>",
                provider="amazon_ses",
                status="FAILED",
                retry_count=3,
                error_message="Guidewire API endpoint timeout (HTTP 504 Gateway Timeout after 3 retries)",
                created_at=now - timedelta(hours=1, minutes=10),
                failed_at=now - timedelta(hours=1, minutes=5),
                delivery_receipt={
                    "ses_message_id": "0100018f-abcd-1234-ses@email.us-east-1.amazonaws.com",
                    "http_status": 200,
                    "destination": "claims-escalations@damcogroup.com",
                    "latency_ms": 198.5
                },
                details={
                    "claim_number": "0445566778",
                    "error": "HTTP 504 Gateway Timeout",
                    "retry_count": 3
                }
            ),
            Notification(
                id="d4455667-8899-aabb-ccdd-eeff00112233",
                event_type="TEST_EMAIL",
                recipient="priyer@test.com",
                subject="UAIC Orchestrator — Live Test Notification",
                body_html="<p>Interactive live test notification.</p>",
                provider="local_mock",
                status="SENT",
                retry_count=0,
                created_at=now - timedelta(hours=2),
                sent_at=now - timedelta(hours=2),
                delivery_receipt={
                    "provider": "local_mock",
                    "status": "DELIVERED_TO_MEMORY",
                    "latency_ms": 1.2
                },
                details={"test": True}
            )
        ]

        for s in samples:
            session.add(s)
        await session.commit()
        print(f"Successfully seeded {len(samples)} notification entries.")


if __name__ == "__main__":
    asyncio.run(seed())
