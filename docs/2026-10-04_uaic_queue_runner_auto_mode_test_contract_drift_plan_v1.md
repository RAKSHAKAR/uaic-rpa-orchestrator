# Implementation Plan: Fix Queue Runner Auto-Mode Test Contract Drift

**Implementation ID:** `IMP-2026-1004-001`  
**Date:** 2026-10-04  
**Status:** Complete  
**AI Verification:** Complete (100% Automated Testing Suite)  
**Human Verification:** Awaiting Human Verification  
**Target:** `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py` & `backend/app/tasks/queue_runner.py`

---

## 1. Problem Statement & Root Cause Diagnosis

### Symptom
Running the full backend test suite (`pytest`) reports 545 passed, 10 skipped (environment-dependent), and exactly **1 failure**:
```
FAILED backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py::test_p4_005_auto_queue_enabled_by_default
AssertionError: expected call not found.
Expected: set('uaic:queue:auto_mode', 'true')
  Actual: not called.
```

### Root Cause Analysis
1. `test_p4_005_auto_queue_enabled_by_default(mocker)` was written to verify that when Redis is uninitialized (`AUTO_MODE_KEY` returns `None`), `is_auto_queue_enabled()` defaults to `True` and writes `"true"` back to Redis:
   ```python
   def test_p4_005_auto_queue_enabled_by_default(mocker):
       """Verify Auto Queue is enabled by default (True) when Redis uninitialized."""
       mock_redis = mocker.MagicMock()
       mock_redis.get.return_value = None
       mocker.patch("app.tasks.queue_runner.get_redis_client", return_value=mock_redis)
       assert is_auto_queue_enabled() is True
       mock_redis.set.assert_called_with("uaic:queue:auto_mode", "true")
   ```
2. In subsequent hardening for environments without Redis, `queue_runner.py` introduced `_can_try_redis()`:
   ```python
   def _can_try_redis() -> bool:
       import time
       global _REDIS_OFFLINE_UNTIL
       if getattr(settings, "SEMAPHORE_BYPASS", False):
           return False
       return time.monotonic() > _REDIS_OFFLINE_UNTIL

   def is_auto_queue_enabled() -> bool:
       global _IN_MEMORY_AUTO_MODE
       if not _can_try_redis():
           return _IN_MEMORY_AUTO_MODE
       ...
   ```
3. In `backend/tests/conftest.py` (line 15), `os.environ["SEMAPHORE_BYPASS"] = "true"` is set so tests don't stall on unreachable Redis sockets.
4. Because `SEMAPHORE_BYPASS` is active during pytest execution, `_can_try_redis()` returns `False`.
5. Therefore, `is_auto_queue_enabled()` immediately returns the in-memory fallback state (`_IN_MEMORY_AUTO_MODE`, which is `True`) without ever invoking `get_redis_client()` or interacting with the mock Redis instance.
6. Consequently, `mock_redis.set` is never called, causing the assertion failure.

---

## 2. Proposed Changes & Implementation Strategy

### A. Test Contract Alignment (`test_prompt04_scraping_compliance_and_qa_fixes.py`)
In `test_p4_005_auto_queue_enabled_by_default`:
- Patch `_can_try_redis` to return `True` (or patch `settings.SEMAPHORE_BYPASS` to `False` and reset `_REDIS_OFFLINE_UNTIL = 0`) specifically within this test to explicitly exercise the Redis codepath under test.
- Also verify both paths:
  1. **Uninitialized state (`None`):** Returns `True` and writes `"true"` to Redis.
  2. **Explicit disabled state (`b"false"` / `"false"`):** Returns `False`.
  3. **Explicit enabled state (`b"true"` / `"true"`):** Returns `True`.

### B. Production Code Inspection (`queue_runner.py`)
- Confirm `queue_runner.py` implementation remains clean, safe, and robust:
  - If Redis is available, reads from and writes to Redis.
  - If `SEMAPHORE_BYPASS` is active or Redis fails, cleanly falls back to in-memory state without crashing or blocking.

---

## 3. Verification Plan

1. **Focused Test Run:**
   Execute `backend/tests/test_prompt04_scraping_compliance_and_qa_fixes.py` with pytest:
   - Expected: 8 passed (100% pass for all Prompt 04 compliance tests).
2. **Full Test Suite Run:**
   Execute full backend test suite `pytest backend/tests`:
   - Expected: 546 passed, 0 failed, 10 skipped (only environment-dependent skips).
3. **Static Analysis & Linting:**
   - Run `ruff check app tests` (must remain 0 errors).
   - Run `tsc --noEmit` on frontend (must remain 0 errors).
   - Run `scripts/check_ps1_syntax.ps1` (must remain 0 errors).
4. **Documentation & Verified Record:**
   - Record test output in a verified record document under `docs/`.
