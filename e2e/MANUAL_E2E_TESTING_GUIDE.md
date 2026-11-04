# UAIC Claim & RPA Orchestrator — Manual End-to-End Testing & Verification Guide

> **Document Type:** Manual E2E Testing & Operational Verification Guide  
> **Implementation ID:** `IMP-2026-1031-002`  
> **Target Audience:** QA Engineers, System Operators, DevOps, and Audit Engineers  
> **Environment Parity:** Windows Local (`setup_local.ps1`) & Containerized Docker (`docker-compose.yml`)

---

## 1. Introduction & E2E Testing Philosophy

The **UAIC Claim & RPA Orchestrator** is an enterprise court-case discovery and robotic process automation platform automating legal research across 8 county court portals in Florida and Texas, performing RapidFuzz deduplication cascade, and delivering validated structured claim records to Guidewire Insurance Cloud.

This guide provides an authoritative, step-by-step manual test protocol. It covers attended GUI verification, unattended headless processing, Anti-Captcha MV3 extension configuration, multi-tab single-session browser orchestration, unique names deduplication, fuzzy confidence scoring, Guidewire delivery, and failure recovery.

### Testing Principles
1. **Zero Fabrication**: All test scenarios must be executed against genuine endpoints or verified test harness fixtures.
2. **Behavioral Fidelity (V4 Flow)**: Automation behaviors strictly adhere to the Power Automate V4 Robin desktop flow specification.
3. **Environment Parity**: Every workflow executed in local development must execute identically inside the containerized Docker stack via Xvfb/noVNC (`http://localhost:6080/vnc.html`).
4. **Resilience & Graceful Degradation**: Portals that encounter transient errors, rate limits, or CAPTCHA challenges must degrade cleanly to `HUMAN_INTERVENTION_REQUIRED` without terminating the multi-tab session or corrupting other portals.

---

## 2. Environment Prerequisites (Local vs Docker)

### 2.1 Local Environment (Windows 10/11 x64)
- **Runtime Dependencies**:
  - Python 3.14.7 (Virtual environment located at `backend/.venv`)
  - Node.js v18.17+ / v20+ and npm v9+
  - Google Chrome (stable, installed at `%ProgramFiles%\Google\Chrome\Application\chrome.exe` or `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`)
  - Redis Server running on `localhost:6379`
- **Port Allocations**:
  - `http://localhost:3000`: Next.js 14 Frontend Application
  - `http://localhost:8000`: FastAPI Backend API (`/docs`, `/redoc`, `/api/v1`)
  - `localhost:6379`: Redis Celery Broker & Result Backend
  - `http://localhost:1080`: MailDev SMTP & Web Mail Viewer (optional)

### 2.2 Docker Environment (Linux Containers)
- **Containers**:
  - `uaic-backend`: FastAPI + Celery Worker + Xvfb + x11vnc + noVNC + fluxbox
  - `uaic-frontend`: Next.js 14 Web Application
  - `uaic-redis`: Redis 7 Alpine
  - `uaic-maildev`: MailDev Mock SMTP
- **Port Allocations**:
  - `http://localhost:3000`: Frontend Web UI
  - `http://localhost:8000`: FastAPI Backend
  - `http://localhost:6080/vnc.html`: noVNC Web Browser for Attended GUI Inspection
  - `localhost:5900`: Standard VNC Port

---

## 3. Attended (Visible GUI) Setup & Verification

Attended mode launches a visible Google Chrome window on the operator desktop (or inside Xvfb on display `:99` streamed to noVNC in Docker).

### Verification Steps
1. Navigate to **Robot Settings** at `http://localhost:3000/settings`.
2. Locate the **Execution Mode** toggle card:
   - Select **Attended (Visible GUI)**.
   - Verify that **Headless Mode** toggle automatically switches to `OFF`.
   - Click **Save Settings**.
3. Verify backend configuration sync:
   ```powershell
   curl http://localhost:8000/api/v1/settings | jq '{headless_mode, human_interaction_mode}'
   ```
   *Expected output*: `{"headless_mode": false, "human_interaction_mode": "attended"}`.
4. Click **Test Browser Launch** on the Settings page.
   - *Expected outcome*: A visible Google Chrome window appears on the desktop (or in noVNC at `http://localhost:6080/vnc.html`), displays the diagnostic page, and closes cleanly after 3 seconds.
   - *Status Banner*: Displays "Browser launch successful (Attended GUI Mode)".

---

## 4. Unattended (Headless) Setup & Verification

Unattended mode executes background browser instances without a GUI window, ideal for scheduled batch processing and CI/CD pipelines.

### Verification Steps
1. In `http://localhost:3000/settings`, select **Unattended (Headless)**.
2. Confirm the **Headless Mode** toggle switches to `ON`.
3. Click **Save Settings**.
4. Verify backend configuration sync:
   ```powershell
   curl http://localhost:8000/api/v1/settings | jq '{headless_mode, human_interaction_mode}'
   ```
   *Expected output*: `{"headless_mode": true, "human_interaction_mode": "unattended"}`.
5. Click **Test Browser Launch**:
   - *Expected outcome*: No desktop window pops up. The browser runs in headless mode in the background and reports "Browser launch successful (Headless Mode)" within 2 seconds.

---

## 5. AntiCaptcha MV3 Extension Manual Verification

The Anti-Captcha Chrome extension (`anticaptcha-plugin_v0.83`) automatically solves reCAPTCHA v2/v3 and Cloudflare Turnstile challenges.

### Verification Steps
1. Verify the extension folder exists at `d:\scratch\Bot_UAIC\anticaptcha-plugin_v0.83` with a valid `manifest.json`.
2. Inspect `anticaptcha-plugin_v0.83/js/config_ac_api_key.js`:
   - Ensure the `antiCapthaPredefinedApiKey` matches the configured key in Settings.
3. On the **Robot Settings** page, click **Configure Anti-Captcha Extension**:
   - The backend launches Chrome with `--load-extension` and `--disable-extensions-except`.
   - The extension popup loads, injects the API key, and pins the extension to the toolbar.
4. Verify the test API key status:
   - Account balance or connection status displays in the UI banner.

---

## 6. Portal 1: Broward County Clerk Verification

- **Portal Name**: Broward County Clerk of Courts
- **URL**: `https://www.browardclerk.org/Web2`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Launch claim search for Broward:
   - Input Claimant: `JOHN SMITH`, Insured: `MARY SMITH`, Driver: `JOHN SMITH`.
2. Trigger search:
   - Observe Chrome navigate to Broward Clerk portal.
   - Observe human-like typing delay (50ms–150ms per character).
   - Verify reCAPTCHA resolution via AntiCaptcha extension.
   - Verify results table parsing.
3. Check database record:
   - Query `fl_jsonbody_broward` in `claims` table.
   - Verify all 5 schema fields are populated without null values.

---

## 7. Portal 2: Hillsborough County Clerk (HOVER) Verification

- **Portal Name**: Hillsborough County Clerk — HOVER
- **URL**: `https://hover.hillsclerk.com/`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Launch single-portal test for Hillsborough.
2. Observe navigation to the HOVER portal search tab.
3. Verify party name input and date range filter (`>= 2010-01-01`).
4. Validate extraction of results grid, including party styles and case status.
5. Verify JSON stored in `fl_jsonbody_hillsborough`.

---

## 8. Portal 3: Miami-Dade County Clerk (OCS) Verification

- **Portal Name**: Miami-Dade County Clerk — Online Court Services (OCS)
- **URL**: `https://www2.miamidadeclerk.gov/ocs/`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Trigger Miami-Dade scraper from the Claim Detail page.
2. Confirm handling of modal disclaimers / terms-of-service acceptance click.
3. Observe submission of 3 distinct name variations.
4. Confirm multi-page pagination traversal up to configured max pages.
5. Verify JSON stored in `fl_jsonbody_miami`.

---

## 9. Portal 4: Travis County Odyssey Portal Verification

- **Portal Name**: Travis County District & County Courts (Odyssey)
- **URL**: `https://odysseyweb.traviscountytx.gov/Portal/`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Trigger Travis County bot.
2. Verify selection of "Smart Search" option.
3. Verify handling of Smart Search captcha if triggered.
4. Confirm case number links extraction and case style details.
5. Verify JSON stored in `te_jsonbody_travis`.

---

## 10. Portal 5: Dallas County Courts Verification

- **Portal Name**: Dallas County Courts Portal
- **URL**: `https://courtsportal.dallascounty.org/DALLASPROD/`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Trigger Dallas County bot.
2. Verify selection of Civil/Family case records search.
3. Verify input of party name and date filter.
4. Verify extraction of CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType.
5. Verify JSON stored in `te_jsonbody_dallas`.

---

## 11. Portal 6: Harris County Justice of the Peace Verification

- **Portal Name**: Harris County Justice of the Peace Courts
- **URL**: `https://jpwebsite.harriscountytx.gov/`
- **Output Schema (EXACT)**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO CaseType**)

> [!CRITICAL]
> **Schema Rule**: Do NOT add `CaseType` to Harris JP output schema. It must contain exactly 4 fields.

### Manual Test Protocol
1. Trigger Harris JP bot.
2. Verify search across all 16 JP precincts or central search.
3. Verify extraction of the exact 4-field schema.
4. Verify JSON stored in `te_jsonbody_harris`.

---

## 12. Portal 7: Harris County Clerk (EDOCS) Verification

- **Portal Name**: Harris County Clerk WebSearch / EDOCS
- **URL**: `https://www.cclerk.hctx.net/`
- **Output Schema (EXACT)**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus` (**NO CaseType**)

> [!CRITICAL]
> **Schema Rule**: Do NOT add `CaseType` to Harris County Clerk output schema. It must contain exactly 4 fields.

### Manual Test Protocol
1. Trigger Harris County Clerk bot.
2. Verify civil records search selection.
3. Verify extraction of 4-field records schema.
4. Verify JSON stored in `te_jsonbody_cclerk`.

---

## 13. Portal 8: Harris County District Clerk Verification

- **Portal Name**: Harris County District Clerk
- **URL**: `https://www.hcdistrictclerk.com/`
- **Output Schema**: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`

### Manual Test Protocol
1. Trigger Harris District Clerk bot.
2. Verify login bypass or authenticated session reuse.
3. Verify search execution for 3 party names.
4. Verify 5-field schema stored in `te_jsonbody_hcdistrict`.

---

## 14. Combined Multi-Tab 8-Portal Orchestration Verification

The combined scenario executes all 8 court scrapers concurrently inside a single persistent Google Chrome browser session using managed browser tabs.

### Manual Test Protocol
1. Create or select a cross-state claim (e.g., Policy State: `FL`, Loss State: `TX`).
2. Click **Start Automation (All 8 Portals)**.
3. Observe Chrome browser session:
   - Single Chrome window opens with initial tab.
   - Up to 4 tabs open concurrently (respecting configured concurrency limit).
   - Tabs navigate to FL portals and TX portals in parallel.
   - Resource throttling keeps CPU below 80% and RAM below 3GB.
   - As each portal completes, its tab closes and the next queued portal launches.
4. Confirm completion:
   - All 8 storage keys in `claims` table are populated:
     `fl_jsonbody_broward`, `fl_jsonbody_hillsborough`, `fl_jsonbody_miami`, `te_jsonbody_cclerk`, `te_jsonbody_dallas`, `te_jsonbody_harris`, `te_jsonbody_hcdistrict`, `te_jsonbody_travis`.
   - Claim status transitions to `COMPLETED` (or `MATCH_FOUND` / `PENDING_REVIEW`).

---

## 15. Unique Names Deduplication Verification

Before searches are submitted to court portals, party names must be normalized and deduplicated across the 3 roles: Claimant, Insured, and Driver.

### Verification Steps
1. Navigate to `/exceptions` or test via API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/matches/unique-names \
     -H "Content-Type: application/json" \
     -d '{"claimant": "Johnathan Smith", "insured": "John Smith", "driver": "Robert Doe"}'
   ```
2. Verify RapidFuzz partial ratio deduplication:
   - "Johnathan Smith" vs "John Smith" exceeds the 60% similarity threshold and is collapsed into a single search target.
   - Output contains 2 unique search targets: "Johnathan Smith" and "Robert Doe".
   - Total searches executed on portals = 2 instead of 3.

---

## 16. RapidFuzz Cascade & Confidence Scoring Verification

The fuzzy matching engine matches extracted court case styles against claim parties using a strict 3-tier cascade:
1. **Tier 1**: Claimant (first + last) → CaseStyle
2. **Tier 2**: Insured (first + last) → CaseStyle (if no Claimant match)
3. **Tier 3**: Driver (first + last) → CaseStyle (if no Insured match)

### Verification Steps
1. Import test claim with Case Style: `"STATE FARM VS JOHN SMITH ET AL"`.
2. Run matching task.
3. Check `match_results` table:
   - `match_tier` = `"Claimant"`
   - `confidence_score` >= `0.60`
   - Status = `AUTO_APPROVED` (if >= 0.85) or `PENDING_REVIEW` (if 0.60–0.84).
4. Verify threshold configuration:
   - Adjust threshold in `/settings` to `0.75`.
   - Re-evaluate: cases with score 0.65 move to `NO_MATCH`.

---

## 17. Guidewire Insurance Cloud Integration Verification

Guidewire integration sends structured matches to the Guidewire ClaimCenter API.

### Contract Rules
- **ClaimNumber**: If 9 digits, MUST be prefixed with `"0"` to make 10 digits.
- **ExposureNumber**: Defaults to `"001"`.
- **CaseItems**: Array of `{CaseNumber, CaseStyle, CountyWebsite, SuitFiledDate}`.

### Verification Steps
1. Test via Settings test endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/settings/test-guidewire \
     -H "Content-Type: application/json" \
     -d '{"auth_type": "Bearer", "api_url": "https://httpbin.org/post", "api_token": "test-token"}'
   ```
2. Inspect payload on test push:
   - Claim `123456789` -> `"0123456789"`.
   - Verify `CaseItems` matches schema.
   - Verify audit log entry in `/audit` recording the request, response code, and latency.

---

## 18. Queue Management & Celery Worker Telemetry Verification

### Verification Steps
1. Navigate to **Queue Monitor** at `http://localhost:3000/monitor`.
2. Inspect real-time telemetry:
   - Active worker count
   - Queue depth (Pending, Processing, Completed, Failed)
   - CPU and Memory consumption gauges
3. Click **Pause Queue**:
   - Verify pending claims do not start processing.
4. Click **Resume Queue**:
   - Verify worker immediately resumes processing pending claims.
5. Click **Retrigger Failed**:
   - Verify claims in `FAILED` status transition to `PENDING` and are re-enqueued.

---

## 19. Error Scenarios & Graceful Degradation Testing

| Scenario | Injected Condition | Expected Behavior | Verification Check |
|---|---|---|---|
| **Anti-Captcha Failure** | Clear API key in Settings | Portal pauses, flags CAPTCHA challenge | Claim status -> `HUMAN_INTERVENTION_REQUIRED`, screenshot saved in `docs/frames/` |
| **Portal Network Timeout** | Block portal domain via hosts file | Scraper retries 3 times with exponential backoff | Scraper records timeout, moves to next portal; claim status -> `PARTIALLY_COMPLETED` |
| **Zero Search Results** | Search for non-existent party `"XYZNOTFOUND12345"` | Portal reports 0 records | Storage key stored as empty JSON array `[]`; status -> `COMPLETED` |
| **Guidewire 500 Error** | Point Guidewire URL to 500 responder | Guidewire client retries 3 times | Task logs error, preserves claim data, sets status -> `GUIDEWIRE_FAILED` |
| **Browser Crash** | Kill Chrome process mid-search | Celery detects disconnected DevTools | Worker cleans up orphaned session, logs error screenshot, marks portal failed |

---

## 20. Automated E2E Test Suite Runner (`run_all_e2e_tests.ps1`)

In addition to manual step-by-step verification, the platform includes a unified PowerShell E2E test harness that executes automated test suites and generates interactive HTML and JSON reports.

### Script Location
`e2e/run_all_e2e_tests.ps1`

### Execution Syntax & Parameters

```powershell
# Run backend E2E suites and automatically open the HTML report in your browser
powershell -ExecutionPolicy Bypass -File e2e\run_all_e2e_tests.ps1 -Suite Backend -OpenReport

# Run all test suites in Attended GUI mode
powershell -ExecutionPolicy Bypass -File e2e\run_all_e2e_tests.ps1 -Suite All -Mode Attended

# Run specifically against Docker container environment
powershell -ExecutionPolicy Bypass -File e2e\run_all_e2e_tests.ps1 -Environment Docker -Suite All

# Run single portal tests
powershell -ExecutionPolicy Bypass -File e2e\run_all_e2e_tests.ps1 -Suite Portal -Portal broward
```

### Parameter Reference
| Parameter | Type | Allowed Values | Default | Purpose |
|---|---|---|---|---|
| `-Environment` | String | `Local`, `Docker` | `Local` | Target execution environment |
| `-Suite` | String | `All`, `Backend`, `Frontend`, `Integration`, `Portal` | `All` | Test scope to execute |
| `-Mode` | String | `Attended`, `Unattended` | `Attended` | RPA browser display mode |
| `-Portal` | String | e.g. `broward`, `dallas` | `""` | Single county portal filter |
| `-Headless` | Switch | Flag | `$false` | Forces headless browser |
| `-OpenReport` | Switch | Flag | `$false` | Opens HTML report upon completion |

### Test Artifacts & Report Output
- **Interactive HTML Report**: `e2e/reports/e2e_test_report.html` (Full visual breakdown of passed, failed, and skipped tests with execution duration and logs)
- **JSON Telemetry Summary**: `e2e/results/summary.json` (Machine-readable CI/CD report with exact metrics)
- **Detailed Suite Logs**: `e2e/logs/*.log` (Individual stdout/stderr captures for every test suite)

---

## 21. Acceptance Criteria & Pre-Deployment Checklist

Before approving any release for staging or production, verify all criteria:

- [ ] All 15 PowerShell scripts pass syntax validation (`scripts/check_ps1_syntax.ps1`).
- [ ] Backend test suite passes 100% of non-skipped unit/integration tests (`pytest`).
- [ ] Ruff Python linter reports 0 errors (`ruff check app tests`).
- [ ] Next.js TypeScript compiler passes with 0 errors (`npx tsc --noEmit`).
- [ ] Frontend ESLint reports 0 errors and 0 warnings (`npm run lint`).
- [ ] Automated E2E Runner passes 100% (`e2e/run_all_e2e_tests.ps1 -Suite Backend`).
- [ ] All 9 execution recordings exist in canonical `docs/recordings/`.
- [ ] All 8 county portal schemas match exact contract definitions.
- [ ] Guidewire 9-digit '0' prefix is verified.
- [ ] RapidFuzz cascade (Claimant -> Insured -> Driver) is verified.
- [ ] Both Attended (Visible GUI) and Unattended (Headless) modes function in local and Docker.
- [ ] No temporary files or loose screenshots exist outside canonical directories.
- [x] IDE Problems panel reports 0 diagnostics and 0 spelling errors.

---

## 22. Additional Master Requirements Verification Protocol (IMP-2026-1031-003)

### 22.1 Persistent Visualizations Verification
1. Navigate to `http://localhost:3000/claims/1` (Claim 360 view).
2. Observe the 9-stage Process Stepper, Timeline Gantt chart, and Waterfall Bar.
3. Keep the browser open for 30+ seconds while background auto-polling executes every 3 seconds.
4. **Pass Criteria:** Components remain permanently visible. There is zero DOM unmounting, zero flicker, and no full-page loading spinner during background polling.
5. Navigate to Dashboard (`/`) with 0 claims.
6. **Pass Criteria:** Donut chart renders neutral standby ring without layout collapse.

### 22.2 Tri-Browser Execution Verification
1. Navigate to `/settings` $\implies$ Automation & Robot Configuration.
2. Select **Google Chrome**, then click **Test Browser Connection**.
3. **Pass Criteria:** Displays detected version and executable path for Google Chrome.
4. Select **Microsoft Edge**, then click **Test Browser Connection**.
5. **Pass Criteria:** Displays detected version and executable path for Microsoft Edge.
6. Select **Chromium**, then click **Test Browser Connection**.
7. **Pass Criteria:** Displays bundled Playwright Chromium executable path. Zero silent Chrome substitution.

### 22.3 Anti-Captcha Failure Escalation Protocol
1. Launch automation with blocked unpacked extension permissions.
2. **Pass Criteria:** Automation halts cleanly with `BlockedExtensionInitializationError`.
3. Task is marked `FAILED` with failure stage `BLOCKED_EXTENSION_INITIALIZATION`.
4. IT Support alert notification is emitted requesting review of browser group policies.

### 22.4 Execution Settings Defaults Verification
1. Click **Reset to Defaults** in `/settings`.
2. **Pass Criteria:**
   - Keystroke delay: `50 ms`
   - Typing speed mode: `balanced`
   - Action pacing: `250 ms`
   - Navigation timeout: `180 seconds`
   - Stealth clicks / mouse jitter: `Enabled`
   - Reload backoff: `5 seconds`
   - Execution mode: `Headless (Background)`
   - Screen recording: `False (Disabled)`
   - CAPTCHA wait: `120 seconds`

### 22.5 Decoupled Eight-Bot Concurrency & State Routing
1. Ingest cross-state claim (e.g. Policy: `FL`, Loss: `TX`).
2. Trigger automation.
3. **Pass Criteria:** All 8 portal bots are dispatched concurrently with `DISPATCHED` status and unique correlation IDs. Active browser workers transition to `RUNNING` up to `max_concurrent_claims`, with remaining bots held safely in `QUEUED`.
4. Ingest missing policy state claim.
5. **Pass Criteria:** Automatically marked `RecordStatusEnum.NEEDS_REVIEW` and routed to Exceptions review.


