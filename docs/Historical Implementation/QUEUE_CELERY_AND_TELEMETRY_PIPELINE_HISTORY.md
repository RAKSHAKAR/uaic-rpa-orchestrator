# Historical Implementation: Task Queue, Celery & Telemetry Pipeline

> **Subsystem:** Celery Asynchronous Workers, Task Routing & Telemetry  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. Celery Architecture & Isolated Queues

The platform distributes background processing across Redis over 4 isolated Celery queues:
- `ingest`: High-volume Excel/CSV file parsing, date conversion, and schema validation.
- `scrapers`: Browser automation tasks (`run_claim_portals`, `run_single_portal_task`).
- `matcher`: Fuzzy matching cascade and Guidewire Cloud delivery tasks.
- `notifications`: SMTP dispatch and email alert generation.

---

## 2. Key Remediations & Technical Milestones

### 2.1 Auto-Queue Sequential Runner
- Built an intelligent queue daemon (`queue_runner.py`) that monitors pending claims and triggers automation sequentially.
- Enforced worker concurrency prefetch (`worker_prefetch_multiplier = 1`) to prevent a single worker from starving other tasks.

### 2.2 Failure Recovery & Re-triggering
- Implemented `POST /api/v1/queue/retrigger` and `POST /api/v1/claims/bulk-retry` to reset failed claims to `PENDING` and re-enqueue them without data loss.
- Added automatic retry task (`retry_stuck_claims_task`) that detects claims stuck in `IN_PROGRESS` for longer than 30 minutes and recovers them gracefully.

### 2.3 Asynchronous Multi-Format Streaming Exports
- Implemented streaming exports supporting large datasets (10,000+ claims) without worker memory bloat:
  - 3-Sheet Excel Workbook (Claims, Court Cases, Execution Telemetry).
  - High-speed CSV exports (summary, telemetry, case items).
  - Single-claim PDF and JSON dossier exports.

