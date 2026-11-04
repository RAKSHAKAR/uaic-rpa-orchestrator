---
name: performance-testing
description: >-
  Benchmark endpoint response latency, scraper cycle duration, and batch queue throughput against SLAs.
---

# Performance Testing

## 1. Purpose & Overview
Measures system response times, database query execution durations, and scraper throughput under controlled benchmark conditions, proving SLA compliance.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-release performance validation.
- Benchmarking scraper execution durations across Florida and Texas court portals.
- Evaluating API throughput under concurrent request loads.

### When NOT to Use
- Testing functional correctness on single unit tests.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Benchmarking test harness (`scripts/inspect_timing.py`), target endpoints, and performance SLA thresholds.

### Prerequisites
- Running backend stack with populated test dataset.

---

## 4. Step-by-Step Execution Procedure

### Step 1: API Latency Benchmarking
Execute 100 consecutive requests to core API endpoints (`/api/v1/claims`, `/api/v1/claims/stats`). Record p50, p95, and p99 latency.

### Step 2: Scraper Cycle Duration Benchmarking
Execute automated scraper benchmark across 8 portals using `inspect_timing.py`. Record duration per portal and per party.

### Step 3: Database Query Execution Time
Inspect database execution logs. Identify queries exceeding 100ms threshold.

### Step 4: Fuzzy Matching Cascade Throughput
Benchmark RapidFuzz matching engine against 1,000 cases. Confirm throughput exceeds 10,000 evaluations/second.

### Step 5: Performance Report Synthesis
Publish benchmark findings comparing observed metrics against target SLAs.


---

## 5. Safety Considerations & Guardrails
- Do NOT run performance stress tests against live external court portals (respect court server rate limits).
- Ensure benchmarks run on isolated test databases to avoid corrupting active operational records.

---

## 6. Expected Deliverables & Artifacts
- System Performance Benchmark Report with p50, p95, p99 latency figures.
- Scraper timing telemetry summary in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Core API endpoints respond within p95 < 200ms.
- [ ] Fuzzy matching cascade evaluates 1,000 cases in < 1 second.
- [ ] Observed performance satisfies all client SLA targets.

---

## 8. Error Recovery & Troubleshooting
- If endpoints fail latency targets, invoke `performance-optimization` to profile slow database queries.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/performance-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@performance-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `performance-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `performance-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run performance-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt performance-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `performance-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/scripts/inspect_timing.py`
- `backend/app/services/fuzzy_engine.py`
