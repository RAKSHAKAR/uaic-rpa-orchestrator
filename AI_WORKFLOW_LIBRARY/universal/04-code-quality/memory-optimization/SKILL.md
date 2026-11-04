---
name: memory-optimization
description: >-
  Find and resolve memory leaks, unclosed browser contexts, unbounded caches, and task bloat in long-running services.
---

# Memory Optimization

## 1. Purpose & Overview
Diagnoses memory growth in long-running Celery workers, Playwright browser instances, and Next.js servers, preventing Out-Of-Memory (OOM) crashes.

---

## 2. When to Use & When NOT to Use

### When to Use
- Celery workers exhibiting unbounded memory consumption over time.
- Zombie Chromium processes remaining after scraper completion.
- Large file exports (Excel/PDF) exhausting server RAM.

### When NOT to Use
- Short-lived CLI scripts that terminate within seconds.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Process memory logs (`check_python_procs.ps1`), worker PID monitoring, and heap profiling dumps.

### Prerequisites
- Access to process monitoring tools on Windows/Linux.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Process Memory Monitoring
Track memory growth over multiple task iterations using `scripts/check_python_procs.ps1` or `tracemalloc`.

### Step 2: Leak Source Isolation
Identify leak vectors: unclosed Playwright browser contexts, lingering event listeners, uncollected SQLAlchemy session caches, or unbounded global dicts.

### Step 3: Resource Lifecycle Cleanup
Enforce deterministic cleanup using context managers (`with` / `async with`), explicit `browser.close()`, and `gc.collect()`.

### Step 4: Streaming & Chunking Implementation
Replace in-memory buffering with chunked streaming (e.g. streaming large CSV/Excel exports directly to disk).

### Step 5: Worker Recycling Configuration
Configure Celery `max_tasks_per_child` to periodically recycle worker processes safely.

### Step 6: Sustained Load Verification
Run 100-iteration stress test and verify memory stabilizes within expected bounds.


---

## 5. Safety Considerations & Guardrails
- Ensure browser termination logic does not kill other active attended sessions running for different tasks.
- Never disable garbage collection globally.

---

## 6. Expected Deliverables & Artifacts
- Memory-optimized service and worker code.
- Memory Stability Report with process RAM curves before and after fix.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero zombie Chrome or Python processes remain following task completion.
- [ ] Worker memory footprint stabilizes under sustained task execution.
- [ ] File exports stream without loading full datasets into RAM.

---

## 8. Error Recovery & Troubleshooting
- If Playwright crashes during context teardown, wrap in try/finally blocks with fallback process cleanup.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/memory-optimization`. | `CUSTOM SKILL` |
| **Cursor** | Select `@memory-optimization` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `memory-optimization`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `memory-optimization` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run memory-optimization`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt memory-optimization`. | `PROMPT FILE` |
| **Windsurf** | Activate `memory-optimization` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/automation/browser_manager.py`
- `scripts/clean_stale_workers.py`
