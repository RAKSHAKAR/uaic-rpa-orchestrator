---
name: load-testing
description: >-
  Simulate concurrent Celery worker loads, high-volume claim uploads, and database connection pool contention.
---

# Load Testing

## 1. Purpose & Overview
Tests system stability, worker queue processing, and database connection pooling under sustained concurrent load, identifying breaking points and deadlocks.

---

## 2. When to Use & When NOT to Use

### When to Use
- Validating system capacity for high-volume batch claim processing (e.g. 500+ claims/day).
- Testing Celery worker auto-scaling and Redis queue saturation.

### When NOT to Use
- Local unit testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Load testing scripts, simulated batch spreadsheets (`ProdRecords8Bots.xlsx`), and Redis connection.

### Prerequisites
- Local or staging environment with Redis and multi-worker Celery configuration.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Batch Load Generation
Queue a batch of 50 simulated claims simultaneously using `scripts/run_100_claim_captcha_test.py`.

### Step 2: Worker Concurrency & Queue Depth Monitoring
Monitor Celery worker concurrency, prefetch buffers, and Redis queue depth (`scripts/check_celery_workers.py`).

### Step 3: Database Connection Pool Monitoring
Monitor active and overflow database connections in SQLAlchemy pool during concurrent execution.

### Step 4: Error & Timeout Rate Tracking
Track failure rates, database lock timeouts (`OperationalError: database is locked`), and retry triggers.

### Step 5: Throughput & Recovery Audit
Verify queue drains to 0 cleanly and workers return to idle state without memory leaks.

### Step 6: Load Testing Summary
Document maximum sustainable concurrency and bottleneck thresholds.


---

## 5. Safety Considerations & Guardrails
- Never execute load tests against external third-party production APIs (Guidewire, court clerks).
- Monitor CPU and memory to prevent complete host system freeze.

---

## 6. Expected Deliverables & Artifacts
- Load & Concurrency Test Report.
- Queue throughput curves and connection pool metrics.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] System processes concurrent batch without database corruption or unhandled crashes.
- [ ] Queue drains completely with all claims reaching valid terminal states.
- [ ] Connection pool recovers cleanly without orphan connections.

---

## 8. Error Recovery & Troubleshooting
- If SQLite database locks occur under high concurrency, recommend migration to PostgreSQL via `sync_sqlite_to_postgres.py`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/load-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@load-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `load-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `load-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run load-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt load-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `load-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `scripts/run_100_claim_captcha_test.py`
- `scripts/check_celery_workers.py`
