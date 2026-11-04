---
name: performance-optimization
description: >-
  Measure and optimize database query latency, API response times, scraper cycle duration, and frontend rendering.
---

# Performance Optimization

## 1. Purpose & Overview
Identifies system bottlenecks and applies targeted algorithmic, database, caching, and concurrency optimizations backed by before-and-after benchmark evidence.

---

## 2. When to Use & When NOT to Use

### When to Use
- API endpoints exceeding response latency thresholds (> 500ms).
- Slow database queries causing lock contention or connection pool exhaustion.
- Scraper cycle durations exceeding client SLA requirements.

### When NOT to Use
- Premature optimization on cold paths that execute infrequently.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Profiling telemetry, slow query logs, scraper execution timestamps, and baseline metrics.

### Prerequisites
- Established, reproducible performance baseline before making code changes.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Baseline Profiling & Metric Capture
Measure baseline execution duration, CPU usage, memory allocations, and query counts. Record exact baseline numbers.

### Step 2: Bottleneck Root Cause Analysis
Identify primary bottleneck: N+1 ORM queries, unindexed filtering, synchronous blocking calls in async loops, or excessive React re-renders.

### Step 3: Targeted Optimization Application
Apply specific optimization: eager loading (`selectinload`), database composite index, Redis caching, or React memoization.

### Step 4: Benchmark Re-measurement
Rerun the exact baseline benchmark under identical conditions. Calculate percentage latency reduction and throughput gain.

### Step 5: Regression Verification
Execute full unit and integration test suites to confirm zero functional regressions.

### Step 6: Performance Report Synthesis
Document before-and-after metrics, optimization techniques, and verification evidence.


---

## 5. Safety Considerations & Guardrails
- Never apply optimizations that compromise code readability or data integrity without significant measurable gain.
- Avoid aggressive concurrency that triggers court portal rate-limiting or IP bans.

---

## 6. Expected Deliverables & Artifacts
- Optimized source code files.
- Performance Benchmark Report with before-and-after comparison charts.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Measurable latency reduction (e.g. $\ge 30\%$) achieved on the target path.
- [ ] Zero functional regressions; 100% of test assertions pass.
- [ ] Memory overhead remains stable under sustained load.

---

## 8. Error Recovery & Troubleshooting
- If an optimization causes race conditions or intermittent failures, revert and profile with finer granularity.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/performance-optimization`. | `CUSTOM SKILL` |
| **Cursor** | Select `@performance-optimization` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `performance-optimization`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `performance-optimization` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run performance-optimization`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt performance-optimization`. | `PROMPT FILE` |
| **Windsurf** | Activate `performance-optimization` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/services/fuzzy_engine.py` - RapidFuzz High-Performance Matching
- `backend/app/core/database.py`
