# IMP-2026-0921-001 — Implementation Record
## UAIC: Fleet Concurrency Gate + AntiCaptcha Full-Config Fix

**Implementation ID:** IMP-2026-0921-001  
**Date:** 2026-09-21  
**Status:** Complete — AI Verification: Complete (100% Automated Testing Suite)

## Summary

Two critical production bugs fixed:

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| A — Fleet Concurrency | API endpoints dispatched all tasks before in-task Redis semaphore could gate | Gate added at API dispatch layer in claims.py + queue.py |
| B — AntiCaptcha Inactive | SingleSessionBrowserRunner injected 3 keys, missing `enable: true` | Ported full 20-key ChromeSession injection + popup init |

## Files Changed
- backend/app/api/v1/endpoints/claims.py — bulk_start_claims concurrency gate
- backend/app/api/v1/endpoints/queue.py — run_selected_claims concurrency gate
- backend/app/tasks/scraper_tasks.py — fail-closed semaphore + get_running_loop()
- backend/app/automation/session_runner.py — full 20-key CDP injection + popup init + toolbar pin

## Verification Results
- pytest --tb=short -q: 453/453 passed, exit 0
- ruff check app/: 0 errors
- npx tsc --noEmit: 0 errors

**AI Verification:** Complete (100% Automated Testing Suite)
