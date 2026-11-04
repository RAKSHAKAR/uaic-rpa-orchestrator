# UAIC Architecture Context

> **Purpose:** Pure architectural reference — no governance prose. For AI agents and developers who need structural understanding fast.
> **Last Updated:** 2026-11-03 (`IMP-2026-1103-002`)

---

## 1. High-Level Component Diagram

```mermaid
flowchart TD
    subgraph Frontend["Frontend (Next.js 14, Port 3000)"]
        UI["10 App Router Pages\n(Claims, Monitor, Health,\nAudit, Settings, Upload,\nExceptions, Branding,\nNotifications, Claim Detail)"]
        Comp["19 Shared Components\n(Navbar, Sidebar, StatCard,\nStatusBadge, CommandPalette,\nThemeProvider, etc.)"]
        ApiClient["lib/api.ts\n(Axios, typed endpoints)"]
    end

    subgraph Backend["Backend (FastAPI, Port 8000)"]
        API["REST API v1\n8 endpoint modules"]
        Services["Services Layer\n(fuzzy_engine, guidewire_client,\nexcel_parser, settings_service,\nnotification_service, etc.)"]
        Models["SQLAlchemy Models\n(Claim, CourtCase, MatchResult,\nAuditLog, Notification, etc.)"]
        DB["SQLite WAL\norchestrator.db"]
    end

    subgraph Workers["Celery Workers (Redis broker)"]
        ScraperTasks["scraper_tasks.py\n8 portal dispatch"]
        FuzzyTasks["fuzzy_tasks.py\nRapidFuzz cascade"]
        IngestTasks["ingest_tasks.py\nExcel/CSV parsing"]
        ExportTasks["export_tasks.py\nAsync streaming"]
        NotifTasks["notification_tasks.py\nEmail dispatch"]
        RetryTasks["retry_tasks.py\nFailed claim retry"]
        QueueRunner["queue_runner.py\nAuto-sequential"]
    end

    subgraph Automation["Browser Automation (Playwright)"]
        SessionRunner["session_runner.py\nMulti-tab orchestrator"]
        BrowserMgr["browser_manager.py\n(ChromeSession, TabManager)"]
        FL["Florida Scrapers\n(broward, hillsborough, miami)"]
        TX["Texas Scrapers\n(dallas, travis, harris_jp,\nharris_district, harris_cclerk)"]
        BaseScaper["BaseCourtScraper\n(CAPTCHA, WAF, session handling)"]
    end

    subgraph External["External Systems"]
        Guidewire["Guidewire Insurance Cloud\n(REST API)"]
        Courts["8 County Court Portals\n(FL + TX)"]
        AntiCaptcha["AntiCaptcha MV3\n(Chrome Extension)"]
        Redis["Redis 7.2\n(Port 6379)"]
        SMTP["SMTP / MailDev\n(Port 1025/1080)"]
    end

    UI --> ApiClient
    ApiClient -->|HTTP| API
    API --> Services
    Services --> Models
    Models --> DB
    API -->|dispatch| Workers
    Workers -->|trigger| SessionRunner
    SessionRunner --> BrowserMgr
    BrowserMgr --> FL
    BrowserMgr --> TX
    FL --> BaseScaper
    TX --> BaseScaper
    BaseScaper -->|browser| Courts
    BaseScaper -->|CAPTCHA| AntiCaptcha
    Workers -->|store results| DB
    Services -->|push| Guidewire
    Workers -->|broker| Redis
    Workers -->|email| SMTP
```

---

## 2. State Routing Decision Tree

```mermaid
flowchart TD
    A["Claim Received\npolicy_state + loss_location_state"] --> B{policy_state == loss_location_state?}
    B -->|YES| C{Which state?}
    B -->|NO| H["Cross-State Mode\nRun ALL 8 portals"]
    C -->|FL| D["Florida Only\n• Broward County\n• Hillsborough County\n• Miami-Dade OCS"]
    C -->|TX| E["Texas Only\n• Harris Clerk\n• Dallas County\n• Harris JP\n• Harris District\n• Travis County"]
    H --> F["• Broward\n• Hillsborough\n• Miami-Dade\n• Harris Clerk\n• Dallas\n• Harris JP\n• Harris District\n• Travis"]
```

---

## 3. Scraper Lifecycle (37-Step)

```mermaid
flowchart TD
    S1["1. Browser init\n(Chrome + AntiCaptcha ext)"] --> S2["2. URL navigation"]
    S2 --> S3["3. WAF/bot detection check"]
    S3 --> S4["4. Session timeout popup check"]
    S4 --> S5["5. Form field fill\n(name, DOL date)"]
    S5 --> S6["6. CAPTCHA detection"]
    S6 --> S7{CAPTCHA present?}
    S7 -->|YES| S8["7. Wait for AntiCaptcha\ntoken injection"]
    S8 --> S9["8. Verify DOM token\n(g-recaptcha-response)"]
    S9 --> S10["9. Submit search form"]
    S7 -->|NO| S10
    S10 --> S11["10. Wait for AJAX response"]
    S11 --> S12{Results found?}
    S12 -->|NO RESULTS| S13["Record: no matches\nProceed to next name"]
    S12 -->|YES| S14["11. Extract result rows\n(4 or 5 fields per row)"]
    S14 --> S15["12. Pagination check"]
    S15 --> S16{More pages?}
    S16 -->|YES| S17["Navigate to next page"]
    S17 --> S14
    S16 -->|NO| S18["13. RapidFuzz cascade\n(Claimant → Insured → Driver)"]
    S18 --> S19["14. Build Guidewire payload\n(CaseItems array)"]
    S19 --> S20["15. Persist to DB\n(portal JSON body key)"]
    S20 --> S21["16. Update claim stage\n+ audit log"]
```

---

## 4. Fuzzy Match Cascade

```mermaid
flowchart TD
    A["Court case extracted\nCaseStyle: 'Smith v. Johnson'"] --> B["Try: Claimant\n(first + last) → CaseStyle\nRapidFuzz partial_ratio"]
    B --> C{score >= 0.60?}
    C -->|YES| D["Match found!\nMark: MATCHED\nSave MatchResult"]
    C -->|NO| E["Try: Insured\n(first + last) → CaseStyle"]
    E --> F{score >= 0.60?}
    F -->|YES| D
    F -->|NO| G["Try: Driver\n(first + last) → CaseStyle"]
    G --> H{score >= 0.60?}
    H -->|YES| D
    H -->|NO| I["No match\nMark: NO_MATCH\nFor review if confidence > 0"]
```

---

## 5. Celery Queue Topology

| Queue | Workers | Tasks |
|---|---|---|
| `default` | 10 threads | `scraper_tasks`, `fuzzy_tasks`, `ingest_tasks`, `export_tasks` |
| `notifications` | 2 threads | `notification_tasks` |
| `retries` | 2 threads | `retry_tasks` |
| Broker | Redis 7.2 (Port 6379) | All queues |
| Monitor | Flower (Port 5555) | Real-time task visibility |

**Task execution order for a single claim:**
```
ingest_tasks.parse_file
    → scraper_tasks.run_portal_scraper (×1 to ×8 portals)
        → fuzzy_tasks.run_fuzzy_match
            → fuzzy_tasks.push_to_guidewire
                → notification_tasks.send_completion_alert
```

---

## 6. Database Schema Overview

| Table | Key Columns | Purpose |
|---|---|---|
| `claims` | id, claim_number, policy_state, loss_location_state, claimant_*, insured_*, driver_*, dol, stage, status | Core claim records |
| `court_cases` | id, claim_id, portal_key, case_number, case_style, filing_date, case_status, case_type | Extracted court case data |
| `match_results` | id, claim_id, court_case_id, match_type, score, is_confirmed | Fuzzy match outcomes |
| `audit_logs` | id, claim_id, event_type, message, created_at | Immutable audit trail |
| `error_screenshots` | id, claim_id, portal_key, screenshot_path, error_message | Browser error captures |
| `notifications` | id, event_type, recipient, subject, status, sent_at | Email delivery history |
| `system_settings` | key, value | DB-persisted configuration |
| `guidewire_submissions` | id, claim_id, payload, response, status | Guidewire push history |

---

## 7. Portal Output Schema Matrix

| Portal | CaseNumber | CaseStyle | FilingDate | CaseStatus | CaseType |
|---|---|---|---|---|---|
| Broward County | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hillsborough County | ✅ | ✅ | ✅ | ✅ | ✅ |
| Miami-Dade OCS | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dallas County | ✅ | ✅ | ✅ | ✅ | ✅ |
| Travis County | ✅ | ✅ | ✅ | ✅ | ✅ |
| Harris District | ✅ | ✅ | ✅ | ✅ | ✅ |
| Harris JP | ✅ | ✅ | ✅ | ✅ | ❌ **NO CaseType** |
| Harris County Clerk | ✅ | ✅ | ✅ | ✅ | ❌ **NO CaseType** |

> [!CAUTION]
> **NEVER add CaseType to Harris JP or Harris County Clerk.** This is a non-negotiable business rule matching Power Automate V4 Robin flows.

---

## 8. CAPTCHA Handling by Portal

| Portal | CAPTCHA Type | Cooldown | Recovery |
|---|---|---|---|
| Broward County | Google reCAPTCHA v2 + Turnstile | 120s token expiry | Auto re-solve |
| Miami-Dade OCS | reCAPTCHA v3 badge + challenge | Session-based | AntiCaptcha extension |
| Travis County | reCAPTCHA v2 Smart Search | 600s WAF cooldown | Auto re-dispatch |
| Dallas County | Cloudflare Turnstile | Token renegotiation | `CaptchaResolutionError` → `AWAITING_HUMAN` |
| Hillsborough | PerimeterX (no traditional CAPTCHA) | 300s bot check cooldown | HumanInteractionEngine |
| Harris JP | None | — | — |
| Harris Clerk | None | — | — |
| Harris District | None | — | — |

---

## 9. Key File Locations

| Purpose | File |
|---|---|
| FastAPI app entry | `backend/app/main.py` |
| Config / env | `backend/app/core/config.py` |
| DB session | `backend/app/core/database.py` |
| Celery app | `backend/app/core/celery_app.py` |
| Base scraper | `backend/app/automation/base.py` |
| Session runner | `backend/app/automation/session_runner.py` |
| Fuzzy engine | `backend/app/services/fuzzy_engine.py` |
| Guidewire client | `backend/app/services/guidewire_client.py` |
| Settings service | `backend/app/services/settings_service.py` |
| Excel parser | `backend/app/services/excel_parser.py` |
| Error classifier | `backend/app/services/error_classifier.py` |
| Human engine | `backend/app/automation/human_engine.py` |
| API router | `backend/app/api/v1/api.py` |
| Test conftest | `backend/tests/conftest.py` |
| Frontend entry | `frontend/src/app/layout.tsx` |
| API client | `frontend/src/lib/api.ts` |
| TypeScript types | `frontend/src/types/index.ts` |
| Theme tokens | `frontend/src/app/globals.css` |
| Theme provider | `frontend/src/components/ThemeProvider.tsx` |
| Branding page | `frontend/src/app/branding/page.tsx` |

