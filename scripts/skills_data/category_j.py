"""
Category J: Project-Specific UAIC Workflow Pack
Contains 17 comprehensive skills tailored specifically to the UAIC Claim & RPA Orchestrator,
including the 8 county court scrapers, CAPTCHA handling, fuzzy deduplication, and Guidewire integration.
"""

SKILLS_J = [
    {
        "name": "uaic-orchestrator-context",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Load the approved UAIC Claim & RPA Orchestrator context, architectural constraints, business rules, and test commands.",
        "purpose": "Provides the essential mental model and architectural invariants for working in the UAIC repository, detailing the 8 Florida/Texas court scrapers, RapidFuzz deduplication cascade, Guidewire integration, and strict directory layout rules.",
        "when_to_use": [
            "Before making ANY code or architectural change to the UAIC Orchestrator repository.",
            "Understanding business rules (state routing, DOL 1899-12-30 base date, 9-digit ClaimNumber '0' prefix)."
        ],
        "when_not_to_use": [
            "Generic non-UAIC repositories."
        ],
        "required_inputs": [
            "`AGENTS.md` and `README.md` master booklet."
        ],
        "prerequisites": [
            "Repository access."
        ],
        "procedure": [
            ("Core Architecture Inspection", "Review stack: Next.js 14 App Router, Python 3.14.7 FastAPI, Celery 5.4, Redis, SQLAlchemy 2.0 async, Playwright Chromium, RapidFuzz."),
            ("Critical Business Rules Ingestion", "Memorize non-negotiable rules: FL/TX state routing logic, DOL date conversion (1899-12-30 base, strict MM/dd/yyyy), 9-digit ClaimNumber gets '0' prefix, RapidFuzz partial_ratio cascade (Claimant -> Insured -> Driver, threshold=0.60), and exact portal output schemas."),
            ("Protected Directories Audit", "Verify protected directories (`anticaptcha-plugin_v0.83`, `.agents`) remain untouched."),
            ("Pre-Change Verification Baseline", "Run `pytest -q`, `ruff check app tests`, `tsc --noEmit`, and `check_ps1_syntax.ps1`."),
            ("Context Archival", "Apply context to all upcoming implementation planning.")
        ],
        "safety": [
            "CRITICAL: Never alter business rules (state routing, DOL base date, 9-digit prefix, fuzzy cascade threshold).",
            "Never create stray files in root; utility scripts must go to `scripts/`."
        ],
        "deliverables": [
            "Verified operational context.",
            "Baseline health check report."
        ],
        "acceptance_criteria": [
            "Agent demonstrates complete understanding of business rules and repository layout.",
            "Protected directories remain intact.",
            "Pre-flight tests pass cleanly."
        ],
        "error_recovery": [
            "If in doubt on any architectural convention, consult `AGENTS.md` as the authoritative source."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-orchestrator-context` or load `.agents/skills/uaic-context/SKILL.md`.",
            "cursor": "Select `@uaic-orchestrator-context` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-orchestrator-context`.",
            "codex": "Discovered via `AGENTS.md` in OpenAI Codex.",
            "gemini": "Invoke via `gemini run uaic-orchestrator-context`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-orchestrator-context`.",
            "windsurf": "Activate `uaic-orchestrator-context` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 1-4 (Project Identity & Rules)",
            "`.agents/skills/uaic-context/SKILL.md`"
        ]
    },
    {
        "name": "uaic-project-analysis",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Analyse the existing UAIC codebase, Celery task queues, database models, and preserve working court automation.",
        "purpose": "Conducts deep codebase analysis specifically across the UAIC subsystem implementations (scrapers, browser manager, session runner, matcher, queue runner), mapping execution paths and preventing regressions.",
        "when_to_use": [
            "Prior to modifying court scrapers or queue scheduling logic.",
            "Auditing scraper session lifecycle and browser tab recycling."
        ],
        "when_not_to_use": [
            "Generic web application tasks."
        ],
        "required_inputs": [
            "`backend/app/automation/`, `backend/app/tasks/`, `backend/app/models/`."
        ],
        "prerequisites": [
            "Completed `uaic-orchestrator-context`."
        ],
        "procedure": [
            ("Scraper Architecture Traversal", "Inspect `BasePortalScraper` in `backend/app/automation/base.py`. Analyze CAPTCHA wait loop, token checking, and navigation state resets."),
            ("Browser & Tab Manager Inspection", "Inspect `ChromeSession`, `TabManager`, and `ExtensionManager` in `browser_manager.py`. Verify single-session multi-tab recycling patterns."),
            ("State Routing & Party Deduction", "Inspect `generate_unique_names_for_claim()` and DualSearch/TripleSearch matrix in `fuzzy_engine.py`."),
            ("Celery Task Pipeline Mapping", "Trace task dispatch: `ingest_tasks` -> `queue_runner` -> `scraper_tasks` -> `fuzzy_tasks` -> `guidewire` -> `export_tasks`."),
            ("Database Storage Verification", "Inspect `fl_jsonbody_*` and `te_jsonbody_*` column mappings in `ClaimRecord`."),
            ("Analysis Summary Synthesis", "Document UAIC subsystem dependencies and critical invariants.")
        ],
        "safety": [
            "Never hold DB transactions open during browser automation.",
            "Preserve synchronous Playwright browser automation for AntiCaptcha MV3 extension stability."
        ],
        "deliverables": [
            "UAIC Subsystem Deep Analysis Report.",
            "Scraper and queue pipeline flow diagram."
        ],
        "acceptance_criteria": [
            "All 8 scraper implementations and queue bindings are mapped with code references.",
            "Browser session recycling lifecycle is verified.",
            "Zero project files modified during analysis."
        ],
        "error_recovery": [
            "If scraper logic is unclear, cross-reference Robin subflows in `v4_subflows/`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-project-analysis`.",
            "cursor": "Select `@uaic-project-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-project-analysis`.",
            "codex": "Reference `uaic-project-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-project-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-project-analysis`.",
            "windsurf": "Activate `uaic-project-analysis` in Windsurf."
        },
        "references": [
            "`backend/app/automation/session_runner.py`",
            "`backend/app/services/fuzzy_engine.py`"
        ]
    },
    {
        "name": "uaic-requirement-validation",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Trace UAIC implementation features against approved business requirements and Power Automate V4 behavioral flows.",
        "purpose": "Validates that the modern Python/Next.js orchestrator achieves 100% functional and behavioral parity with the client's legacy Power Automate Desktop V4 robotic process automation bots.",
        "when_to_use": [
            "Pre-release qualification of court scrapers or deduplication logic.",
            "Verifying state routing, DOL dates, or Guidewire payload structures."
        ],
        "when_not_to_use": [
            "Non-UAIC requirements."
        ],
        "required_inputs": [
            "Power Automate V4 Robin flows (`v4_subflows/`), `AGENTS.md` Section 3, and implementation test suites."
        ],
        "prerequisites": [
            "Access to annotated V4 subflow documentation (`docs/v4_all_8_subflows_annotated.txt`)."
        ],
        "procedure": [
            ("State Routing Parity Audit", "Verify policy_state == loss_location_state rules: FL runs 3 portals (Broward, Hillsborough, Miami); TX runs 5 portals (Harris Clerk, Dallas, Harris JP, Harris District, Travis); cross-state runs all 8."),
            ("Party Matrix Parity Audit", "Verify unique name generation matrix: All same (1/1), Insured=Driver Claimant!= (1/3), Insured=Claimant Driver!= (2/1), Driver=Claimant Insured!= (2/1), All different (2/3)."),
            ("DOL Date Conversion Parity Audit", "Verify Excel serial date conversion base 1899-12-30 produces exact MM/dd/yyyy strings without timezone shifts."),
            ("Guidewire 9-Digit Rule Audit", "Verify 9-digit ClaimNumber receives leading '0' prefix in Guidewire payload."),
            ("Portal Output Schema Parity Audit", "Verify 5 fields for 6 portals; strictly 4 fields (NO CaseType) for Harris JP and Harris County Clerk."),
            ("Parity Matrix Synthesis", "Publish the UAIC Requirements & V4 Parity Matrix in `docs/`.")
        ],
        "safety": [
            "CRITICAL: Never add CaseType to Harris JP or Harris County Clerk scrapers.",
            "Never introduce timezone offsets into Date of Loss conversion."
        ],
        "deliverables": [
            "UAIC Requirements Traceability & V4 Parity Report in `docs/`.",
            "Automated parity test suite pass log."
        ],
        "acceptance_criteria": [
            "All 5 core business rules verified with 100% compliance.",
            "`backend/tests/test_v4_parity.py` passes all assertions.",
            "Guidewire payload matches exact client contract."
        ],
        "error_recovery": [
            "If parity discrepancies are found, update code to match Power Automate V4 behavior (V4 is authoritative)."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-requirement-validation`.",
            "cursor": "Select `@uaic-requirement-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-requirement-validation`.",
            "codex": "Reference `uaic-requirement-validation` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-requirement-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-requirement-validation`.",
            "windsurf": "Activate `uaic-requirement-validation` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Critical Business Rules)",
            "`backend/tests/test_v4_parity.py`"
        ]
    },
    {
        "name": "uaic-bot-orchestration",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Coordinate execution of the 8 county court scrapers across single-session multi-tab Chrome browser runners.",
        "purpose": "Orchestrates court portal scraping across Florida and Texas counties using a high-performance single-session browser runner (`SingleSessionBrowserRunner`), recycling tabs and maintaining anti-detection posture.",
        "when_to_use": [
            "Executing or modifying the multi-portal automation sequence.",
            "Optimizing portal execution throughput or tab recycling."
        ],
        "when_not_to_use": [
            "Single-portal isolated unit testing."
        ],
        "required_inputs": [
            "Target claim record with policy state and loss location state.",
            "Configured `SingleSessionBrowserRunner`."
        ],
        "prerequisites": [
            "Installed Google Chrome with AntiCaptcha extension."
        ],
        "procedure": [
            ("Portal Target Resolution", "Resolve target portals using `resolve_county_bot_targets()` based on policy and loss states."),
            ("Browser Session Initialization", "Initialize genuine Chrome browser session with unpacked AntiCaptcha MV3 extension."),
            ("Sequential / Multi-Tab Execution", "Iterate through target portals. Open portal tab, navigate to search page, enter party names, wait for CAPTCHA, submit search, and extract results."),
            ("Tab State Reset", "Call `return_to_search_state(page)` to reset form for the next party search without reloading the browser."),
            ("Result Persistence & Task Handoff", "Persist extracted cases to database, populate `fl_jsonbody_*` / `te_jsonbody_*`, and dispatch `evaluate_fuzzy_matches_task` to matcher queue."),
            ("Clean Session Teardown", "Close browser tabs cleanly and update claim status to `SCRAPED`.")
        ],
        "safety": [
            "Avoid aggressive Chrome process termination between portals (preserve session stability).",
            "Ensure failures on one portal do not abort execution of remaining target portals."
        ],
        "deliverables": [
            "Executed court case discovery across all target portals.",
            "Extracted cases persisted in database and linked to claim."
        ],
        "acceptance_criteria": [
            "All resolved target portals are searched for each unique party name.",
            "Cases are parsed into exact schemas and saved to database.",
            "Claim transitions cleanly from `QUEUED` to `SCRAPED`."
        ],
        "error_recovery": [
            "If a portal times out or encounters CAPTCHA failure, record error screenshot, mark portal as FAILED, and continue with remaining portals."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-bot-orchestration`.",
            "cursor": "Select `@uaic-bot-orchestration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-bot-orchestration`.",
            "codex": "Reference `uaic-bot-orchestration` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-bot-orchestration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-bot-orchestration`.",
            "windsurf": "Activate `uaic-bot-orchestration` in Windsurf."
        },
        "references": [
            "`backend/app/automation/session_runner.py`",
            "`backend/app/tasks/scraper_tasks.py`"
        ]
    },
    {
        "name": "uaic-browser-automation",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Develop and maintain Playwright Chromium scrapers with anti-detection flags, shadow DOM traversal, and extension integration.",
        "purpose": "Governs the development of robust web scrapers using Playwright Python, configuring anti-bot evasion arguments, handling dynamic shadow DOM elements, and managing browser contexts.",
        "when_to_use": [
            "Writing a new portal scraper or updating existing portal locators.",
            "Debugging AntiCaptcha extension toolbar integration or Chrome options."
        ],
        "when_not_to_use": [
            "Headless direct HTTP API clients."
        ],
        "required_inputs": [
            "Target portal URL, search form DOM structure, and Playwright Chromium driver."
        ],
        "prerequisites": [
            "Synchronous Playwright API in Python 3.14.7."
        ],
        "procedure": [
            ("Anti-Detection Flag Configuration", "Configure Chrome launch arguments: `--disable-blink-features=AutomationControlled`, `--load-extension`, `--disable-infobars`, `--no-sandbox`."),
            ("Extension Integration", "Load unpacked `anticaptcha-plugin_v0.83/`. Inject API key into extension preferences and pin toolbar."),
            ("Robust Locator Strategy", "Use resilient CSS and text locators (`#PersonSearchResults`, `a:has-text('Party Name')`). Avoid fragile full XPath."),
            ("Explicit Waiting & DOM Polling", "Wait for network idle or selector presence (`page.wait_for_selector()`) with explicit timeouts. Avoid arbitrary sleep calls."),
            ("Table Parsing & Pagination", "Parse table rows (`tbody tr`), clean whitespace, normalize dates, and iterate through pagination controls (`a.next`)."),
            ("Exception Capture & Screenshots", "Wrap critical interactions in try/except blocks; capture full-page screenshot on error to `backend/screenshots/`.")
        ],
        "safety": [
            "CRITICAL: Keep browser automation strictly synchronous for AntiCaptcha extension stability.",
            "Never bypass or disable CAPTCHA wait loops."
        ],
        "deliverables": [
            "Robust Playwright scraper class inheriting from `BasePortalScraper`.",
            "Automated scraper unit and integration tests."
        ],
        "acceptance_criteria": [
            "Scraper navigates, searches, and extracts cases deterministically.",
            "AntiCaptcha extension resolves challenges seamlessly.",
            "Errors capture diagnostic full-page screenshots."
        ],
        "error_recovery": [
            "If locator breaks due to portal redesign, inspect live DOM snapshot and update selector."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-browser-automation`.",
            "cursor": "Select `@uaic-browser-automation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-browser-automation`.",
            "codex": "Reference `uaic-browser-automation` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-browser-automation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-browser-automation`.",
            "windsurf": "Activate `uaic-browser-automation` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py`",
            "`backend/app/automation/browser_manager.py`"
        ]
    },
    {
        "name": "uaic-attended-mode",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Run visible, attended browser execution with genuine Google Chrome window, human pacing, and video evidence capture.",
        "purpose": "Executes court portal automation in visible GUI mode (`headless=False`), allowing human operators to watch browser interactions, intervene if necessary, and record video evidence.",
        "when_to_use": [
            "Running live client demonstrations or operator walkthroughs.",
            "Debugging complex portal interactions or CAPTCHA challenges.",
            "Generating video recordings (`.webp`) for documentation."
        ],
        "when_not_to_use": [
            "Headless CI/CD test runners."
        ],
        "required_inputs": [
            "Windows desktop environment with display server, Google Chrome, and test claims."
        ],
        "prerequisites": [
            "Settings configured with `headless=False`."
        ],
        "procedure": [
            ("Attended Settings Activation", "Set `headless: false` in `SystemSettings` or pass `--attended` flag to launcher scripts."),
            ("Visible Window Launch", "Launch Chrome with visible viewport (1280x800). Position window prominently on desktop."),
            ("Human Pacing Injection", "Apply deliberate human pacing delays (500ms - 1500ms) between typing and click actions to emulate human behavior."),
            ("Video & Screen Recording", "Initialize Playwright video recording or frame capture script (`record_all_8bots_attended.py`)."),
            ("Interactive Operator Observation", "Allow operator to observe portal navigation, CAPTCHA resolution, and table extraction in real time."),
            ("Recording Compression & Archival", "Convert recorded frames into compressed WebP video and archive in `docs/`.")
        ],
        "safety": [
            "Never minimize or close the attended Chrome window while scraping is active.",
            "Ensure attended mode respects rate limits and human pacing."
        ],
        "deliverables": [
            "Visible, attended scraper execution.",
            "Compressed demonstration video recording (.webp) in `docs/`."
        ],
        "acceptance_criteria": [
            "Chrome window opens visibly and displays full automation sequence.",
            "Pacing is smooth and human-like without abrupt robotic jumps.",
            "Video recording is captured and committed to `docs/`."
        ],
        "error_recovery": [
            "If attended window loses focus or crashes, restart session cleanly via `Launch_Attended_Browser.bat`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-attended-mode` or run `scripts/record_all_8bots_attended.py`.",
            "cursor": "Select `@uaic-attended-mode` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-attended-mode`.",
            "codex": "Reference `uaic-attended-mode` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-attended-mode`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-attended-mode`.",
            "windsurf": "Activate `uaic-attended-mode` in Windsurf."
        },
        "references": [
            "`Launch_Attended_Browser.bat`",
            "`scripts/record_all_8bots_attended.py`"
        ]
    },
    {
        "name": "uaic-unattended-mode",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Run background headless browser automation with robust timeout handling, headless Chrome, and error screenshots.",
        "purpose": "Executes high-throughput, unattended court portal scraping in the background (`headless=True` or xvfb), handling unexpected dialogs and capturing error screenshots upon failure.",
        "when_to_use": [
            "Production batch queue processing of high-volume claims.",
            "Automated overnight queue runs."
        ],
        "when_not_to_use": [
            "Visual client demonstrations."
        ],
        "required_inputs": [
            "`headless=True` in `SystemSettings`, Celery worker daemon, and background display."
        ],
        "prerequisites": [
            "Running Celery worker on `scrapers` queue."
        ],
        "procedure": [
            ("Headless Browser Launch", "Launch Playwright with `--headless=new` and anti-detection arguments."),
            ("Background Extension Execution", "Verify AntiCaptcha extension operates headless with injected API key."),
            ("Strict Timeout Enforcement", "Enforce explicit page navigation timeouts (30s) and CAPTCHA resolution timeouts (60s) to prevent hanging workers."),
            ("Error Screenshot & Trace Capture", "Upon any navigation or extraction failure, capture full-page screenshot to `backend/screenshots/` and log traceback."),
            ("Automatic Worker Recycling", "Recycle browser context after task completion to maintain zero memory leakage."),
            ("Status Update & Queue Drain", "Update claim record in database and pull next available claim from Celery queue.")
        ],
        "safety": [
            "Never allow an unattended scraper to hang indefinitely; enforce hard timeouts.",
            "Capture screenshots on all failures for post-mortem operator review."
        ],
        "deliverables": [
            "Unattended batch claim processing.",
            "Diagnostic error screenshots in `backend/screenshots/` for any failed portal."
        ],
        "acceptance_criteria": [
            "Scrapers run headless in background without desktop popups.",
            "Timeout limits terminate hanging pages cleanly.",
            "Claim status transitions reliably to `SCRAPED` or `FAILED`."
        ],
        "error_recovery": [
            "If headless mode triggers Cloudflare bot blocks, switch to attended mode or enable residential proxy rotation."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-unattended-mode`.",
            "cursor": "Select `@uaic-unattended-mode` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-unattended-mode`.",
            "codex": "Reference `uaic-unattended-mode` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-unattended-mode`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-unattended-mode`.",
            "windsurf": "Activate `uaic-unattended-mode` in Windsurf."
        },
        "references": [
            "`backend/tests/e2e/test_e2e_unattended_scraping.py`",
            "`backend/app/tasks/scraper_tasks.py`"
        ]
    },
    {
        "name": "uaic-captcha-handling",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Safe CAPTCHA resolution with AntiCaptcha MV3 extension, Turnstile/reCAPTCHA token inspection, and timeout limits.",
        "purpose": "Governs the detection, automated resolution, and verification of Google reCAPTCHA v2/v3 and Cloudflare Turnstile challenges across court portals, strictly blocking speculative form submits when challenges remain unsolved.",
        "when_to_use": [
            "Navigating portals with active CAPTCHA challenges (Broward, Travis, Hillsborough).",
            "Configuring AntiCaptcha API key and solving timeouts."
        ],
        "when_not_to_use": [
            "Portals without CAPTCHA protections (Dallas, Harris JP)."
        ],
        "required_inputs": [
            "Playwright Page instance, AntiCaptcha extension, and configured `captcha_wait_seconds`."
        ],
        "prerequisites": [
            "AntiCaptcha API key configured in `SystemSettings`."
        ],
        "procedure": [
            ("CAPTCHA Challenge Detection", "Inspect DOM for challenge indicators: `iframe[src*='recaptcha']`, `iframe[src*='turnstile']`, `#cf-turnstile`, or `div.g-recaptcha`."),
            ("Extension Solving Wait Loop", "Wait up to `captcha_wait_seconds` (default 25-45s) for AntiCaptcha extension to solve the challenge."),
            ("Token & Solution Verification", "Inspect DOM for solve tokens: `g-recaptcha-response` value length > 25, `cf-turnstile-response` length > 20, or extension `.solved_flag`."),
            ("Active Challenge Safety Gate", "If unsolved after timeout, call `has_active_captcha_challenge(page)`. If active challenge remains, raise `CaptchaResolutionError`. Strictly block speculative search submission."),
            ("Token Injection Fallback", "If solved, ensure response token is populated in hidden form inputs before triggering search click."),
            ("Screenshot on Failure", "If resolution fails, capture error screenshot and record failed CAPTCHA event in audit log.")
        ],
        "safety": [
            "CRITICAL: NEVER click search button speculatively when an active, unsolved CAPTCHA challenge is present (prevents portal IP bans).",
            "Never bypass CAPTCHA wait loops."
        ],
        "deliverables": [
            "Verified CAPTCHA resolution with valid response tokens.",
            "Safe `CaptchaResolutionError` handling on timeout."
        ],
        "acceptance_criteria": [
            "CAPTCHA tokens are validated before form submission.",
            "Unsolved challenges raise `CaptchaResolutionError` and capture screenshots.",
            "Zero speculative submits occur during active challenges."
        ],
        "error_recovery": [
            "If AntiCaptcha account balance is exhausted, trigger operator notification email via `NotificationRule`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-captcha-handling`.",
            "cursor": "Select `@uaic-captcha-handling` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-captcha-handling`.",
            "codex": "Reference `uaic-captcha-handling` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-captcha-handling`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-captcha-handling`.",
            "windsurf": "Activate `uaic-captcha-handling` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py` - `has_active_captcha_challenge`",
            "`backend/scripts/test_broward_turnstile_box.py`"
        ]
    },
    {
        "name": "uaic-fuzzy-matching",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Verify RapidFuzz partial_ratio matching cascade (Claimant -> Insured -> Driver) and 0.60 threshold.",
        "purpose": "Governs the deduplication and fuzzy match engine (`fuzzy_engine.py`), executing the strict 3-tier cascade and filtering cases by minimum filing date (>= 2010-01-01).",
        "when_to_use": [
            "Executing or verifying the fuzzy matching deduplication cascade.",
            "Reviewing fuzzy match candidate scores on `/exceptions` page."
        ],
        "when_not_to_use": [
            "Raw scraper DOM automation."
        ],
        "required_inputs": [
            "Extracted court cases and claim party names (Claimant, Insured, Driver)."
        ],
        "prerequisites": [
            "RapidFuzz library installed in `backend/.venv`."
        ],
        "procedure": [
            ("Case Style Cleaning & Normalization", "Strip noise words ('ET AL', 'VS', 'A MINOR', 'INDIVIDUALLY') using `clean_case_style()`."),
            ("Filing Date Filtering", "Filter out cases filed before minimum filing date (default `>= 2010-01-01`)."),
            ("Tier 1: Claimant Cascade Evaluation", "Evaluate Claimant (first + last) against CaseStyle using `fuzz.partial_ratio()`. If score $\\ge 0.60$, match confirmed as CLAIMANT."),
            ("Tier 2: Insured Cascade Fallback", "If Claimant score < 0.60, evaluate Insured against CaseStyle. If score $\\ge 0.60$, match confirmed as INSURED."),
            ("Tier 3: Driver Cascade Fallback", "If Insured score < 0.60, evaluate Driver against CaseStyle. If score $\\ge 0.60$, match confirmed as DRIVER."),
            ("Match Result Persistence", "Save match result to `MatchResult` table with score, matched party type, and matched party name. Populate `/exceptions` review list.")
        ],
        "safety": [
            "CRITICAL: Never alter the cascade order: Claimant MUST be evaluated before Insured, and Insured before Driver.",
            "Never lower threshold below 0.60 without explicit user authorization."
        ],
        "deliverables": [
            "Matched court cases linked to claim with confidence scores.",
            "Populated `/exceptions` human review list."
        ],
        "acceptance_criteria": [
            "Cascade strictly evaluates Claimant -> Insured -> Driver.",
            "Scores $\\ge 0.60$ generate valid `MatchResult` records.",
            "Cases filed before 2010-01-01 are filtered out."
        ],
        "error_recovery": [
            "If ambiguous matches occur, route claim to `REVIEW_PENDING` status for human operator approval."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-fuzzy-matching`.",
            "cursor": "Select `@uaic-fuzzy-matching` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-fuzzy-matching`.",
            "codex": "Reference `uaic-fuzzy-matching` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-fuzzy-matching`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-fuzzy-matching`.",
            "windsurf": "Activate `uaic-fuzzy-matching` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Fuzzy Match Cascade)",
            "`backend/app/services/fuzzy_engine.py`"
        ]
    },
    {
        "name": "uaic-guidewire-integration",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Validate Guidewire Insurance Cloud payload construction, 9-digit '0' prefix, CaseItems array, and delivery retry logic.",
        "purpose": "Manages outbound integration with Guidewire Insurance Cloud, formatting approved match results into the exact JSON payload contract and managing retry delivery with exponential backoff.",
        "when_to_use": [
            "Pushing matched court cases to Guidewire (`/api/v1/claims/{id}/push-guidewire`).",
            "Testing Guidewire API connection and payload formatting."
        ],
        "when_not_to_use": [
            "Internal database querying."
        ],
        "required_inputs": [
            "Matched claim record, approved court cases, and Guidewire API credentials."
        ],
        "prerequisites": [
            "`GuidewireClient` configured in `app/services/guidewire_client.py`."
        ],
        "procedure": [
            ("Claim Number Formatting", "Format claim number using `format_claim_number(claim_number)`: if length is 9 digits, prefix with '0' (e.g. `123456789` -> `0123456789`)."),
            ("Exposure Number & Case Items Construction", "Construct `CaseItems` array with objects: `CaseNumber`, `CaseStyle`, `CountyWebsite`, `SuitFiledDate` (normalized MM/DD/YYYY). Set `ExposureNumber: '001'`."),
            ("Payload Serialization", "Serialize payload matching contract: `{\"ClaimNumber\": \"...\", \"ExposureNumber\": \"001\", \"CaseItems\": [...]}`."),
            ("Outbound HTTP Delivery", "Dispatch POST request via `GuidewireClient` with configured authentication (Bearer, ApiKey, Basic, or OAuth2)."),
            ("Delivery Response & Audit Logging", "Record HTTP status and response body in `GuidewireActivity` table. Update claim status to `PUSH_SUCCEEDED`."),
            ("Retry on Transient Failure", "If Guidewire returns 5xx or timeout, queue task for retry with exponential backoff; update status to `PUSH_FAILED`.")
        ],
        "safety": [
            "CRITICAL: 9-digit ClaimNumber '0' prefix must ONLY be applied in Guidewire payload; never alter original ClaimNumber in database.",
            "Mask Guidewire API tokens in audit logs."
        ],
        "deliverables": [
            "Formatted Guidewire payload delivery.",
            "Recorded `GuidewireActivity` audit log."
        ],
        "acceptance_criteria": [
            "Payload strictly adheres to Guidewire JSON contract.",
            "9-digit claim numbers have leading '0' prefix.",
            "Successful delivery transitions claim to `PUSH_SUCCEEDED`."
        ],
        "error_recovery": [
            "If Guidewire rejects payload due to schema mismatch, inspect `GuidewireActivity` log and correct serializer."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-guidewire-integration`.",
            "cursor": "Select `@uaic-guidewire-integration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-guidewire-integration`.",
            "codex": "Reference `uaic-guidewire-integration` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-guidewire-integration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-guidewire-integration`.",
            "windsurf": "Activate `uaic-guidewire-integration` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 11 (Guidewire Payload Contract)",
            "`backend/app/services/guidewire_client.py`"
        ]
    },
    {
        "name": "uaic-data-validation",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Validate extracted court case schemas, column boundaries, date normalizations, and noise word filtering.",
        "purpose": "Ensures all court records scraped from Florida and Texas portals strictly conform to the exact 5-field schema (or 4-field for Harris JP/Clerk) and contain zero corrupted rows or static glossary prefixes.",
        "when_to_use": [
            "Validating extracted cases before persisting to `ScrapedCourtCase` table.",
            "Testing Excel and CSV import data mapping."
        ],
        "when_not_to_use": [
            "Frontend UI rendering."
        ],
        "required_inputs": [
            "Extracted raw case dictionaries and source portal key."
        ],
        "prerequisites": [
            "Knowledge of portal output schemas in `AGENTS.md` Section 3."
        ],
        "procedure": [
            ("Field Presence Validation", "For Broward, Hillsborough, Miami, Dallas, Travis, Harris District: confirm exactly 5 fields (`CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`). For Harris JP & Harris Clerk: confirm exactly 4 fields (strictly NO `CaseType`)."),
            ("Static Glossary Filtering", "Reject static glossary prefix rows (e.g. `CACE`, `COCE`, `CC`, `DC`) that contain no digits."),
            ("Filing Date Normalization", "Normalize filing date string to strict `MM/DD/YYYY` format. Filter out invalid dates."),
            ("Case Style Trimming", "Strip leading/trailing whitespace and normalize internal spaces in `CaseStyle`."),
            ("Schema Integrity Assertion", "Assert dictionary keys match expected portal schema exactly before database insert.")
        ],
        "safety": [
            "CRITICAL: NEVER add `CaseType` to Harris JP or Harris County Clerk records.",
            "Do NOT persist duplicate case numbers for the same claim and portal."
        ],
        "deliverables": [
            "Validated, sanitized court case records.",
            "Data validation audit log."
        ],
        "acceptance_criteria": [
            "All persisted cases conform strictly to target portal schema.",
            "Zero static glossary rows exist in database.",
            "All filing dates are normalized to `MM/DD/YYYY`."
        ],
        "error_recovery": [
            "If a portal scraper emits missing keys, fix the extraction parsing loop in the respective scraper module."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-data-validation`.",
            "cursor": "Select `@uaic-data-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-data-validation`.",
            "codex": "Reference `uaic-data-validation` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-data-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-data-validation`.",
            "windsurf": "Activate `uaic-data-validation` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Portal Output Schema)",
            "`backend/app/models/court_case.py`"
        ]
    },
    {
        "name": "uaic-queue-management",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Manage and validate Celery queues, worker prefetch, task states, automatic auto-queue runner, and retries.",
        "purpose": "Manages asynchronous Celery task execution across all 7 queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`), ensuring smooth sequential processing and auto-queue recovery.",
        "when_to_use": [
            "Starting, pausing, or retriggering the queue via API (`/api/v1/queue/*`).",
            "Configuring Celery worker concurrency, prefetch multipliers, and task timeouts.",
            "Toggling auto-queue mode (`/api/v1/queue/auto-mode`)."
        ],
        "when_not_to_use": [
            "Synchronous local script execution."
        ],
        "required_inputs": [
            "Celery application instance (`backend/app/core/celery_app.py`) and Redis broker connection."
        ],
        "prerequisites": [
            "Active Redis server on port 6379."
        ],
        "procedure": [
            ("Queue Status Inspection", "Query `/api/v1/queue/status` or run `scripts/check_celery_workers.py`. Inspect active tasks, queue lengths, and worker PIDs."),
            ("Auto-Queue Loop Operation", "Verify auto-queue runner (`queue_runner.py`) polls for claims in `READY` or `NEW` status, triggers automation sequentially, and throttles concurrency."),
            ("Worker Restart Reconciliation", "Run `reconcile_worker_restart_claims_sync()` upon worker restart to detect orphan claims stuck in `RUNNING` and reset to `READY`."),
            ("Queue Pause & Drain", "Test queue pause endpoint (`POST /api/v1/queue/pause`). Confirm in-flight tasks finish while pending tasks wait."),
            ("Failed Claim Retriggering", "Trigger retrigger endpoint (`POST /api/v1/queue/retrigger`). Verify failed claims reset to `READY` with incremented retry count.")
        ],
        "safety": [
            "Ensure worker reconciliation runs on every worker restart to prevent permanently orphaned claims.",
            "Do not allow prefetch multiplier > 1 on scraper queues to prevent worker hoarding."
        ],
        "deliverables": [
            "Healthy, active Celery queue pipeline.",
            "Queue telemetry and worker reconciliation logs."
        ],
        "acceptance_criteria": [
            "All 7 queues actively process tasks without stalling.",
            "Worker restart cleanly reconciles orphaned claims.",
            "Queue pause and retrigger endpoints operate reliably."
        ],
        "error_recovery": [
            "If Celery workers desynchronize from Redis, restart workers using `scripts/restart_celery.ps1`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-queue-management`.",
            "cursor": "Select `@uaic-queue-management` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-queue-management`.",
            "codex": "Reference `uaic-queue-management` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-queue-management`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-queue-management`.",
            "windsurf": "Activate `uaic-queue-management` in Windsurf."
        },
        "references": [
            "`docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`",
            "`backend/app/tasks/queue_runner.py`"
        ]
    },
    {
        "name": "uaic-settings-validation",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Prove that Settings page configuration (headless mode, timeouts, thresholds, credentials) is strictly respected at runtime.",
        "purpose": "Verifies that all automation settings configured by operators via the `/settings` UI are persisted in database `SystemSettings` and loaded dynamically by scrapers and workers at runtime.",
        "when_to_use": [
            "Modifying or adding new settings to `/settings` page.",
            "Verifying runtime adherence to operator-configured timeouts or headless toggles."
        ],
        "when_not_to_use": [
            "Hardcoding runtime settings in scraper classes."
        ],
        "required_inputs": [
            "`SystemSettings` schema (`app/schemas/settings.py`) and `settings_service.py`."
        ],
        "prerequisites": [
            "Running backend with settings endpoints."
        ],
        "procedure": [
            ("Settings Schema Inspection", "Review `SystemSettings` schema. Verify fields: `headless`, `captcha_wait_seconds`, `match_threshold`, `min_filing_date`, `auto_queue_enabled`, `proxy_enabled`."),
            ("Database Persistence Verification", "Update setting via `POST /api/v1/settings`. Verify changes persist in `system_settings` table."),
            ("Worker Runtime Propagation Audit", "Verify that scraper tasks invoke `get_system_settings_async()` to fetch active settings before launching Chrome."),
            ("Headless Toggle Verification", "Toggle `headless: true/false`. Verify Chrome launches in corresponding headless or GUI mode."),
            ("Timeout Adherence Verification", "Set `captcha_wait_seconds: 15`. Verify scraper CAPTCHA loop terminates at exactly 15 seconds."),
            ("Settings Test Suite Pass", "Run `pytest tests/test_automation_runtime_settings.py -q`.")
        ],
        "safety": [
            "CRITICAL: Workers MUST read dynamic settings via `get_system_settings_async()`; never rely solely on static `.env` defaults.",
            "Mask all credentials (AntiCaptcha key, SMTP password, Guidewire token) in settings API responses."
        ],
        "deliverables": [
            "Verified settings persistence and runtime propagation.",
            "Automated test report confirming settings adherence."
        ],
        "acceptance_criteria": [
            "Settings persist across backend restarts.",
            "Scrapers and workers dynamically adapt to updated settings.",
            "Sensitive credentials remain masked."
        ],
        "error_recovery": [
            "If settings fail to propagate to workers, verify workers are querying `get_system_settings_async()` on each task execution."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-settings-validation`.",
            "cursor": "Select `@uaic-settings-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-settings-validation`.",
            "codex": "Reference `uaic-settings-validation` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-settings-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-settings-validation`.",
            "windsurf": "Activate `uaic-settings-validation` in Windsurf."
        },
        "references": [
            "`backend/app/schemas/settings.py`",
            "`backend/app/services/settings_service.py`"
        ]
    },
    {
        "name": "uaic-eight-portal-validation",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Run portal-specific and cross-portal automated test harnesses exercising all 8 Florida and Texas scrapers.",
        "purpose": "Executes automated portal validation suites across Broward, Hillsborough, Miami, Dallas, Travis, Harris JP, Harris District, and Harris County Clerk, proving navigation, search, and extraction fidelity.",
        "when_to_use": [
            "Testing court scraper modifications or portal DOM fixes.",
            "Pre-release qualification of court automation fleet."
        ],
        "when_not_to_use": [
            "Frontend UI testing."
        ],
        "required_inputs": [
            "Portal scrapers in `backend/app/automation/` and portal test suites in `backend/tests/`."
        ],
        "prerequisites": [
            "Network connectivity to court portals or mock portal server."
        ],
        "procedure": [
            ("Florida Suite Execution", "Run tests for Florida portals: `pytest tests/test_broward_portal.py tests/test_hillsborough_portal.py tests/test_miami_portal.py -q`."),
            ("Texas Suite Execution", "Run tests for Texas portals: `pytest tests/test_dallas_portal.py tests/test_travis_portal.py tests/test_harris_jp_portal.py tests/test_harris_district_portal.py tests/test_harris_clerk_portal.py -q`."),
            ("Schema Compliance Audit", "Assert that all 8 portal test runs emit cases matching their exact required field schema."),
            ("Cross-State Routing Verification", "Test cross-state claim (FL policy, TX loss) and confirm all 8 scrapers are scheduled."),
            ("Validation Report Synthesis", "Compile results into an 8-Portal Automation Health Matrix.")
        ],
        "safety": [
            "Do NOT run high-frequency automated loops against live court portals (respect court servers).",
            "Use mocked HTML fixtures for high-volume automated CI runs."
        ],
        "deliverables": [
            "8-Portal Validation Test Report in `docs/`.",
            "Automated test execution logs confirming 100% pass rate."
        ],
        "acceptance_criteria": [
            "All 8 portal scrapers pass their unit and workflow test suites.",
            "Harris JP and Harris Clerk emit strictly 4 fields (no CaseType).",
            "Remaining 6 portals emit exactly 5 fields."
        ],
        "error_recovery": [
            "If any single portal fails, isolate the test and inspect portal-specific locators."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-eight-portal-validation`.",
            "cursor": "Select `@uaic-eight-portal-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-eight-portal-validation`.",
            "codex": "Reference `uaic-eight-portal-validation` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-eight-portal-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-eight-portal-validation`.",
            "windsurf": "Activate `uaic-eight-portal-validation` in Windsurf."
        },
        "references": [
            "`docs/COURT_PORTALS_GUIDE.md`",
            "`backend/tests/test_broward_portal.py`"
        ]
    },
    {
        "name": "uaic-recording-management",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Organize, deduplicate, and convert Playwright browser recordings (.webp) and visual screenshots (.png) into docs/.",
        "purpose": "Manages visual evidence assets (video recordings, screenshots, walk-through captures), ensuring all browser subagent recordings are converted, organized, and permanently stored in `docs/` rather than transient IDE directories.",
        "when_to_use": [
            "Following attended browser execution or client demonstration recordings.",
            "Organizing and deduplicating visual artifacts in `docs/recordings/` and `docs/images/`."
        ],
        "when_not_to_use": [
            "Code refactoring."
        ],
        "required_inputs": [
            "Recorded video frames (.png) or Playwright webm videos in temporary directories."
        ],
        "prerequisites": [
            "Image conversion tools (Pillow, ffmpeg)."
        ],
        "procedure": [
            ("Recording Asset Discovery", "Identify new video frames or recordings in transient directories or `backend/screenshots/`."),
            ("Compression & WebP Encoding", "Encode recorded frames into high-efficiency WebP animations using `scripts/patch_recording_engine.py`."),
            ("Destination Archival in docs/", "Move finalized recordings to `docs/` or `docs/recordings/`. Ensure descriptive filenames (e.g. `broward_attended_execution.webp`)."),
            ("Transient Frame Cleanup", "Purge individual raw frame PNGs (`frame_*.png`, `master_frame_*.png`) from root and `docs/` after successful video compilation."),
            ("Walkthrough Linkage", "Update `docs/WALKTHROUGH.md` with markdown image links pointing to the archived recordings.")
        ],
        "safety": [
            "CRITICAL: Never leave visual verification recordings exclusively in the transient IDE brain directory.",
            "Save all recordings permanently in `docs/`."
        ],
        "deliverables": [
            "Compressed demonstration recordings in `docs/`.",
            "Updated `docs/WALKTHROUGH.md` referencing visual assets."
        ],
        "acceptance_criteria": [
            "Recordings are stored permanently in `docs/`.",
            "Raw frame clutter is purged from repository.",
            "`docs/WALKTHROUGH.md` links render valid images."
        ],
        "error_recovery": [
            "If WebP encoding fails, retain raw frames in `docs/recordings/` and log compression error."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/uaic-recording-management`.",
            "cursor": "Select `@uaic-recording-management` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `uaic-recording-management`.",
            "codex": "Reference `uaic-recording-management` in Codex context.",
            "gemini": "Invoke via `gemini run uaic-recording-management`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt uaic-recording-management`.",
            "windsurf": "Activate `uaic-recording-management` in Windsurf."
        },
        "references": [
            "`docs/WALKTHROUGH.md`",
            "`scripts/patch_recording_engine.py`"
        ]
    },
    {
        "name": "fl-broward-workflow",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Complete operational specification and runbook for the Broward County Clerk of Courts scraper, CAPTCHA verification, and Guidewire push.",
        "purpose": "Provides the complete, authoritative runbook for automating case search and discovery on the Broward County Clerk of Courts portal (`https://www.browardclerk.org/Web2`).",
        "when_to_use": [
            "Operating, testing, or updating the Broward County court scraper (`BrowardScraper`).",
            "Debugging Turnstile/reCAPTCHA resolution on Broward County."
        ],
        "when_not_to_use": [
            "Texas court portals."
        ],
        "required_inputs": [
            "Claim record with Florida policy/loss, unique names list, and Broward portal URL."
        ],
        "prerequisites": [
            "AntiCaptcha extension active and Broward portal reachability."
        ],
        "procedure": [
            ("Portal Navigation", "Navigate to `https://www.browardclerk.org/Web2`. Click Case Search, activate 'Party Name' tab."),
            ("Data Entry", "Fill Last Name, First Name, and DOL normalized to `MM/dd/yyyy` format."),
            ("CAPTCHA Verification", "Inspect for reCAPTCHA/Turnstile. Verify solve tokens (`g-recaptcha-response > 25`, `cf-turnstile-response > 20`). If unsolved, check `has_active_captcha_challenge`. Block submit if active challenge remains."),
            ("Search Submission", "Click `#PersonSearchResults` directly."),
            ("Result Table Extraction", "Parse table rows (`table.table tbody tr`). Filter out glossary rows (`CACE`, `COCE`). Extract 5 fields: `CaseNumber`, `CaseStyle`, `FilingDate`, `CaseStatus`, `CaseType`. Handle pagination."),
            ("Tab Reset & Downstream Push", "Call `return_to_search_state(page)`. Save cases to database and dispatch fuzzy matching cascade.")
        ],
        "safety": [
            "Strictly filter out static prefix glossary rows; real cases must contain digits.",
            "Block speculative search submits when active CAPTCHA is present."
        ],
        "deliverables": [
            "Extracted Broward County cases adhering to 5-field schema.",
            "Verified Broward scraper test pass."
        ],
        "acceptance_criteria": [
            "Broward scraper extracts valid cases with digits in CaseNumber.",
            "Filing dates normalized to MM/DD/YYYY.",
            "5-field schema verified."
        ],
        "error_recovery": [
            "If Broward portal returns Cloudflare Turnstile box, wait for extension resolution or apply proxy rotation."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/fl-broward-workflow` or follow `.agents/skills/fl-broward-workflow/SKILL.md`.",
            "cursor": "Select `@fl-broward-workflow` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `fl-broward-workflow`.",
            "codex": "Reference `fl-broward-workflow` in Codex context.",
            "gemini": "Invoke via `gemini run fl-broward-workflow`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt fl-broward-workflow`.",
            "windsurf": "Activate `fl-broward-workflow` in Windsurf."
        },
        "references": [
            "`.agents/skills/fl-broward-workflow/SKILL.md`",
            "`backend/app/automation/florida/broward.py`"
        ]
    },
    {
        "name": "managing-python-dependencies",
        "category_code": "J",
        "category_name": "Project-Specific UAIC Pack",
        "description": "Enforce Python 3.14.7 virtual environment isolation, avoid global pip modifications, and maintain dependency consistency.",
        "purpose": "Ensures proper Python dependency management within the dedicated `backend/.venv` virtual environment, strictly prohibiting global `pip install` modifications.",
        "when_to_use": [
            "Adding, upgrading, or modifying Python packages in `backend/`.",
            "Before executing Python scripts via the terminal to ensure the correct virtual environment is active."
        ],
        "when_not_to_use": [
            "Frontend npm package management."
        ],
        "required_inputs": [
            "`backend/requirements.txt`, target package name, and Python 3.14.7 virtualenv."
        ],
        "prerequisites": [
            "Active `backend/.venv` virtual environment."
        ],
        "procedure": [
            ("Virtualenv Active Check", "Verify virtualenv: execute `.venv\\Scripts\\python.exe -c 'import sys; print(sys.executable)'`."),
            ("Target Package Specification", "Add package with exact pinned version to `backend/requirements.txt`."),
            ("Virtualenv Installation", "Install package strictly into virtual environment: `.venv\\Scripts\\pip.exe install -r requirements.txt`."),
            ("Conflict & Compatibility Audit", "Verify package installs clean C-extension wheels compatible with Python 3.14.7 on Windows."),
            ("Test Verification", "Execute `pytest` to confirm newly installed package causes zero dependency regressions."),
            ("Lockfile Consistency", "Ensure `requirements.txt` remains the single authoritative source of Python dependencies.")
        ],
        "safety": [
            "CRITICAL: NEVER run global `pip install` on the host machine.",
            "Always pin exact versions to prevent breaking transitive updates."
        ],
        "deliverables": [
            "Updated `backend/requirements.txt`.",
            "Isolated virtual environment with verified packages."
        ],
        "acceptance_criteria": [
            "All packages installed strictly within `backend/.venv`.",
            "Python 3.14.7 compatibility verified.",
            "All backend tests pass cleanly."
        ],
        "error_recovery": [
            "If a package fails to install on Python 3.14, search for compatible pre-built wheels or pure-Python alternatives."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/managing-python-dependencies`.",
            "cursor": "Select `@managing-python-dependencies` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `managing-python-dependencies`.",
            "codex": "Reference `managing-python-dependencies` in Codex context.",
            "gemini": "Invoke via `gemini run managing-python-dependencies`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt managing-python-dependencies`.",
            "windsurf": "Activate `managing-python-dependencies` in Windsurf."
        },
        "references": [
            "`backend/requirements.txt`",
            "`AGENTS.md` - Section 8"
        ]
    }
]

