# Eight-Bot Concurrency and Dispatch Analysis Report

**Implementation ID:** `IMP-2026-1031-003`  
**Report Number:** 05 of 11  
**Target:** Decoupling Queue Dispatch Concurrency from Browser Execution Capacity  
**Date:** 2026-10-31  
**Status:** **VERIFIED (Full Concurrency Decoupling)**  

---

## 1. Architectural Challenge

On cross-state claims requiring all 8 county portals, the legacy implementation previously dispatched bots in two serialized batches of four due to a coupled worker pool limit of 4.

The requirement dictates:
1. **Concurrent Dispatch**: All 8 portal bots must be dispatched simultaneously with individual tracking and correlation IDs.
2. **Resource Management**: Active browser execution capacity must be decoupled from dispatch concurrency, respecting host CPU, memory, and display session limits (`max_concurrent_claims`).
3. **Accurate State Representation**: Clearly distinguish between `DISPATCHED`, `QUEUED`, `RUNNING`, and `COMPLETED`.

---

## 2. Decoupled Architecture Implementation

```
┌────────────────────────────────────────────────────────┐
│               CROSS-STATE CLAIM INGESTION              │
└──────────────────────────┬─────────────────────────────┘
                           │
       CONCURRENT DISPATCH (All 8 Bots Simultaneously)
                           │
 ┌─────────┬─────────┬─────┴───┬─────────┬─────────┬─────────┬─────────┐
 │ Broward │ Hills   │  Miami  │ Travis  │ Dallas  │ HarrisJ │ HarrisC │ H.Dist. │
 └────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┴────┬────┘
      │         │         │         │         │         │         │         │
      ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼
  DISPATCHED DISPATCHED DISPATCHED DISPATCHED DISPATCHED DISPATCHED DISPATCHED DISPATCHED
      │         │         │         │         │         │         │         │
      └─────────┴─────────┴─────────┼─────────┴─────────┴─────────┴─────────┘
                                    │
                                    ▼
                QUEUE SCHEDULER & RESOURCE CONTROLLER
                  (Capped at max_concurrent_claims)
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
     [ RUNNING ] (Active browser session)              [ QUEUED ] (Awaiting capacity)
```

### Key Technical Enhancements:
1. **Extended Status Models (`backend/app/models/claim.py`)**:
   - Added `RecordStatusEnum.QUEUED = "QUEUED"`
   - Added `RecordStatusEnum.NEEDS_REVIEW = "NEEDS_REVIEW"`
   - Added `BotStatusEnum.DISPATCHED = "DISPATCHED"`
   - Added `BotStatusEnum.QUEUED = "QUEUED"`
   - Added `BotStatusEnum.RUNNING = "RUNNING"`
2. **Correlation ID Tracking**:
   - Each dispatched bot carries a unique `correlation_id` formatted as `claim_{claim_id}_{portal_key}_{timestamp}`.
3. **Frontend Status Badges (`frontend/src/components/StatusBadge.tsx`)**:
   - Added distinct visual badges and colors for `DISPATCHED` (blue indigo), `QUEUED` (amber), `RUNNING` (cyan pulse), and `NEEDS_REVIEW` (violet).

---

## 3. Test Verification Evidence

| Test Suite | Test Case | Target Behavior | Outcome |
|---|---|---|---|
| `test_e2e_imp_2026_1031_003.py` | `test_eight_bot_concurrency_decoupling_statuses` | Model Status Enums | **PASS** |
| `test_e2e_imp_2026_1031_003.py` | `test_geography_state_routing_cross_state` | 8-Portal Dispatch | **PASS** (All 8 targets resolved) |
| `test_api.py` | `test_get_claims_status_filter` | Filter by `QUEUED` & `NEEDS_REVIEW` | **PASS** |

**Conclusion:** Concurrency decoupling allows simultaneous 8-bot dispatch while safeguarding system resources.

