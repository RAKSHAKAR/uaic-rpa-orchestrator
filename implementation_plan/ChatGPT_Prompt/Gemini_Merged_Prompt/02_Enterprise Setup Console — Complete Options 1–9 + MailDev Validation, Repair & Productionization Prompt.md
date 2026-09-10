# MASTER PROMPT — ENTERPRISE SETUP CONSOLE COMPLETE VALIDATION, REPAIR & PRODUCTIONIZATION

You are working on the **existing UAIC Claim & RPA Orchestrator** application.

The Setup Console currently provides:

```text
[1] Start All Application Services (Interactive Launch with Mode Select)
[2] Stop / Kill All Running Services (Ports 3000, 8000, 5555, Celery)
[3] Enterprise Data Cleanup & Retention (Categories, Time-Based Scopes, Dry-Run & Audit)
[4] Install / Update Dependencies (Python venv, Playwright, NPM)
[5] Purge / Delete All Dependency Folders (.venv, node_modules, .next)
[6] Configure RPA Execution Mode (Attended GUI vs Unattended Headless)
[7] Run Full Diagnostics & Test Suite (Pytest, Ruff, TypeScript)
[8] Docker Stack Deployment (Start/Stop Containerized Stack)
[9] Live Service Status Monitor (Check listening ports & health)
[M] Open MailDev Web Inspector (http://localhost:1080)
[0] Exit Console
```

The current implementation is NOT acceptable as an enterprise-grade operations console because several options are incomplete, inconsistent, or do not fully control the services they claim to control.

For example:

- Option [2] does not clearly stop/kill MailDev.
- Option [4] installs Playwright Chromium even though the RPA requirement is to use the installed system Google Chrome.
- Option [7] reports tests as passed even though there is still a Python/asyncio resource warning that must be investigated.
- Some options may execute commands without robust process lifecycle management.
- Service detection, startup, shutdown, health checking, and recovery must be made reliable.
- The Setup Console must understand all services actually used by the application.
- Every option must be tested in real execution, not merely inspected statically.

Your task is to **deeply inspect, correct, enhance, test, and productionize the entire Setup Console and every option [1]–[9] plus [M]**.

Do NOT create a superficial demo.

Do NOT only fix the visible errors.

Do NOT claim an option works because the PowerShell script exits successfully.

The actual service/process behavior must be verified.

---

# 1. FIRST: INSPECT THE EXISTING IMPLEMENTATION

Before changing anything:

1. Inspect the entire existing `setup-local.ps1`.
2. Inspect all scripts called by `setup-local.ps1`.
3. Inspect all backend startup scripts.
4. Inspect all frontend startup scripts.
5. Inspect Celery worker startup.
6. Inspect Celery Beat startup.
7. Inspect Redis configuration.
8. Inspect MailDev configuration/startup.
9. Inspect Docker Compose.
10. Inspect `.env` and environment configuration without exposing secrets.
11. Inspect service/port configuration.
12. Inspect RPA execution-mode configuration.
13. Inspect dependency installation logic.
14. Inspect cleanup logic.
15. Inspect diagnostics/test logic.
16. Inspect health endpoints.
17. Inspect logging.
18. Inspect PID/process tracking if present.
19. Inspect all documentation related to setup and local development.
20. Inspect all existing tests related to setup scripts and service lifecycle.

Create an internal inventory of every service required by the application.

At minimum determine whether the local environment uses:

- Next.js frontend
- FastAPI backend
- Celery Worker
- Celery Beat
- Redis
- MailDev
- Flower/monitoring service if applicable
- Playwright/system Chrome
- Anti-Captcha extension
- Docker services if Docker mode is used
- Any additional required service

Do not assume the visible menu is the complete service inventory.

---

# 2. IMPORTANT — DO NOT REMOVE EXISTING FUNCTIONALITY

This is an existing application.

The objective is:

**Enhancement + Correction + Completion**

not:

**Rewrite + Remove**

Preserve all valid existing functionality.

Do not remove working application functionality merely to simplify the Setup Console.

If something is technically incorrect, replace it with a better implementation that preserves the intended business behavior.

---

# 3. SERVICE INVENTORY MUST BE CENTRALIZED

Create one authoritative service definition/configuration used by the Setup Console.

Do not duplicate service names, ports, startup commands, shutdown commands, and health URLs throughout multiple PowerShell functions.

The service registry should define, where applicable:

```text
Service Name
Display Name
Process Name
Port
Startup Command
Working Directory
Health Endpoint
Expected Status
Dependencies
Shutdown Strategy
Restart Strategy
Docker Service Name
Required/Optional
```

For example:

```text
Frontend
Backend
Celery Worker
Celery Beat
Redis
MailDev
Flower/Monitoring
```

The exact services must be derived from the actual project.

---

# 4. OPTION [1] — START ALL APPLICATION SERVICES

## Requirement

Option [1] must actually start every required local service.

It must not merely launch a few terminals and assume everything started correctly.

The startup sequence must understand dependencies.

Example dependency model:

```text
Redis
  ↓
Backend
  ↓
Celery Worker / Celery Beat
  ↓
Frontend
  ↓
MailDev / supporting services
```

Use the actual application dependency graph rather than blindly following this example.

---

## 4.1 Interactive RPA Mode Selection

Option [1] must allow the user to select:

```text
Attended (GUI)
Unattended (Headless)
```

The selected mode must actually propagate to the backend/RPA engine.

It must not merely change text displayed by the console.

---

## 4.2 Attended Mode

When Attended mode is selected:

- Use system Google Chrome.
- Browser must be visibly launched when an actual automation task executes.
- GUI automation must actually interact with the visible browser.
- Anti-Captcha integration must use the configured extension.
- The extension path must be resolved dynamically from the project root.

Never hardcode a developer-specific path such as:

```text
C:\Users\priyer\...
```

Use:

```text
<PROJECT_ROOT>\anticaptcha-plugin_v0.83
```

or equivalent dynamically resolved path.

---

## 4.3 Unattended Mode

When Unattended mode is selected:

- Run the automation without requiring visible GUI interaction.
- Do not require a logged-in desktop session where technically avoidable.
- Anti-Captcha integration must use the configured extension.
- Ensure all browser and automation configuration is compatible with headless execution.
- Verify that queue processing works.

Attended and unattended execution must use the same core business workflow.

---

## 4.4 Startup Verification

After starting each service:

1. Verify the process exists.
2. Verify the expected port is listening.
3. Verify the health endpoint where available.
4. Verify the service reports healthy.
5. Record the result in the setup log.
6. Do not report "Started" if verification failed.

If a service fails:

- Show the actual failure.
- Identify the service.
- Show the relevant log location.
- Attempt safe recovery where appropriate.
- Do not silently continue.

---

# 5. OPTION [2] — STOP / KILL ALL RUNNING SERVICES

This option currently has an important gap.

The menu says:

```text
Stop / Kill All Running Services
```

but **MailDev is not included clearly in the shutdown scope**.

This must be fixed.

## Option [2] MUST stop every service actually started by the application.

At minimum audit and include:

```text
Frontend — 3000
Backend — 8000
MailDev — 1080
Celery / Worker
Celery Beat
Redis — 6379
Flower/Monitoring — if used
Any other application-owned local process
```

Do not hardcode the above list if the actual project differs; derive it from the centralized service registry.

---

## 5.1 Safe Shutdown

Shutdown must:

1. Attempt graceful shutdown first.
2. Wait for termination.
3. Verify process termination.
4. Verify port release.
5. Force terminate only if graceful shutdown fails.
6. Verify again after force termination.
7. Report the final state.

Do not blindly execute:

```text
taskkill /F
```

against broad process names if that could terminate unrelated user applications.

Target only processes belonging to this application.

---

## 5.2 MailDev Requirement

MailDev must explicitly be handled by Option [2].

After Option [2]:

```text
localhost:1080
```

must no longer be serving MailDev.

Verify both:

- MailDev process is stopped.
- Port 1080 is released.

This requirement is mandatory.

---

## 5.3 Idempotency

Running Option [2] when nothing is running must not produce an error.

It should report something similar to:

```text
All application services are already stopped.
```

Running Option [2] multiple times must remain safe.

---

# 6. OPTION [3] — ENTERPRISE DATA CLEANUP & RETENTION

This option must be a real enterprise cleanup tool.

It must NOT delete configuration or secrets accidentally.

The cleanup UI must allow selection of:

### Data Categories

At minimum audit whether the application contains:

- Claims
- Claim execution data
- Scraped court cases
- Queue records
- Audit events
- Telemetry
- Automation execution history
- Notification history
- Error records
- Export history
- Screenshots
- Temporary files
- Cached data
- Other application-generated records

The exact categories must be based on the actual database/storage model.

---

## 6.1 Time-Based Cleanup

Support:

- Days
- Weeks
- Months
- Years
- Current Month
- Previous Month
- Current Quarter
- Previous Quarter
- Current Year
- Previous Year
- Before Date
- After Date
- Custom Date Range

---

## 6.2 Dry Run

Before deleting anything:

Show:

```text
Category
Records Found
Storage Size if available
Date Range
Estimated Impact
```

Nothing should be deleted during dry-run.

---

## 6.3 Confirmation

For destructive cleanup:

- Require explicit confirmation.
- Show exactly what will be deleted.
- Require confirmation before execution.

---

## 6.4 Referential Integrity

Cleanup must understand relationships.

Do not create orphan records.

Do not delete parent records while leaving invalid child records.

Use transactions wherever supported.

If cleanup fails:

- Roll back where possible.
- Record the failure.
- Do not claim success.

---

## 6.5 Dashboard and Cache Reconciliation

After cleanup:

- Refresh affected dashboard statistics.
- Invalidate relevant caches.
- Refresh queues.
- Refresh audit/monitoring counts.
- Ensure UI does not show stale records.

---

## 6.6 Configuration Protection

Do NOT delete:

- Application configuration
- User configuration
- RPA settings
- Branding settings
- Portal configuration
- Secrets
- Credentials
- Provider configuration

unless explicitly selected as a separate administrative action and intentionally supported.

---

Yes. Since the current **Browser Automation Engine explicitly supports Chromium, Google Chrome, and Microsoft Edge**, Option **[4] Install / Update Dependencies** must be updated so it does **not assume Google Chrome or Chromium only**.

Replace the existing **Section 7 — OPTION [4]** with the following:

````markdown
# 7. OPTION [4] — INSTALL / UPDATE DEPENDENCIES

## OBJECTIVE

Option [4] must fully install, update, repair, and validate ALL dependencies required by the existing UAIC Claim & RPA Orchestrator.

The application currently supports THREE browser runtimes:

1. Chromium
2. Google Chrome
3. Microsoft Edge

This browser support is already part of the application and MUST NOT be removed, restricted, or simplified.

The dependency installer must therefore understand and validate ALL THREE supported browser engines.

---

## 7.1 SUPPORTED BROWSER RUNTIMES

The dependency system MUST support:

| Browser | Support | Runtime |
|---|---|---|
| Chromium | REQUIRED | Playwright/Chromium-compatible runtime |
| Google Chrome | REQUIRED | Installed host Google Chrome |
| Microsoft Edge | REQUIRED | Installed host Microsoft Edge |

The browser selected from the application's Browser Automation Engine settings must determine which browser runtime is used by the RPA engine.

DO NOT hardcode Google Chrome as the only supported browser.

DO NOT hardcode Chromium as the only supported browser.

DO NOT remove Microsoft Edge support.

---

## 7.2 BROWSER DETECTION

Option [4] must detect all supported browsers independently.

For each browser, determine:

- Installed / Not Installed
- Version
- Executable path
- Architecture
- Availability
- Launch capability
- Automation capability
- Extension compatibility
- Anti-Captcha compatibility
- Current configured/default status

Example:

```text
Browser Runtime Detection

[✓] Chromium
    Version: x.x.x
    Runtime: Available
    Automation: Available
    Anti-Captcha: Compatible

[✓] Google Chrome
    Version: x.x.x
    Executable: C:\...\chrome.exe
    Automation: Available
    Anti-Captcha: Compatible

[✓] Microsoft Edge
    Version: x.x.x
    Executable: C:\...\msedge.exe
    Automation: Available
    Anti-Captcha: Compatible
````

If a browser is unavailable, clearly identify which browser is missing.

DO NOT fail the entire dependency installation merely because one optional browser is unavailable.

However, if the application is configured to use that unavailable browser, Option [4] MUST report the configuration as invalid and provide a clear remediation.

---

# 7.3 BROWSER RUNTIME INSTALLATION

Option [4] must install or repair the runtime required by EACH supported browser.

### Chromium

Verify the Chromium runtime required by the application's automation framework.

If the application intentionally uses a Playwright-managed Chromium distribution, install/repair that distribution.

However:

* Do not install Chromium unnecessarily.
* Do not repeatedly download Chromium on every setup execution.
* Detect whether the required runtime already exists.
* Reuse an existing valid installation.
* Validate its version.
* Repair only when missing or corrupted.

### Google Chrome

Detect the installed system Google Chrome.

Do NOT automatically replace it with bundled Chromium.

Do NOT install another Chrome copy if a valid supported installation already exists.

Verify:

* Chrome executable exists
* Chrome launches
* version can be retrieved
* automation connection works
* required automation flags work
* Anti-Captcha extension can load
* selected profile/configuration works

### Microsoft Edge

Detect the installed Microsoft Edge.

Verify:

* Edge executable exists
* Edge launches
* version can be retrieved
* automation connection works
* Chromium extension APIs required by Anti-Captcha are supported
* Anti-Captcha extension can load
* selected profile/configuration works

---

# 7.4 IMPORTANT — DO NOT CONFUSE PLAYWRIGHT DEPENDENCIES WITH BROWSER SUPPORT

The installer must distinguish between:

1. Python Playwright package
2. Node/JavaScript Playwright dependencies, if applicable
3. Playwright-managed Chromium browser
4. System Google Chrome
5. System Microsoft Edge
6. Anti-Captcha browser extension
7. Browser-specific automation configuration

Installing the Python Playwright package does NOT automatically mean that Chromium must always be downloaded.

The installer must determine whether the current application actually requires the Playwright-managed Chromium distribution.

If Chromium is supported and required, install it.

If only Google Chrome or Edge is selected for the current RPA configuration, do not unnecessarily download another large browser distribution simply because Playwright is installed.

The final implementation must optimize setup time, disk usage, startup time, and maintenance.

---

# 7.5 BROWSER SELECTION MUST BE CONFIGURATION-DRIVEN

Browser selection must come from the application's centralized Settings / Browser Automation Engine configuration.

Supported values:

```text
chromium
chrome
edge
```

Do NOT hardcode:

```text
browser = chrome
```

throughout the backend.

Instead:

```text
Settings
   ↓
Browser Automation Engine
   ↓
Selected Browser Runtime
   ↓
Browser Factory / Launcher
   ↓
County Scraper
   ↓
Anti-Captcha Extension
```

All 8 county scrapers must use the centralized browser factory/runtime abstraction.

No scraper should independently decide that it must use Chrome, Chromium, or Edge.

---

# 7.6 BROWSER FACTORY / ABSTRACTION

Implement or repair a centralized browser-launching abstraction.

Example conceptual API:

```text
BrowserRuntime.CHROMIUM
BrowserRuntime.CHROME
BrowserRuntime.EDGE
```

The browser factory must resolve:

* executable
* launch arguments
* profile directory
* headless/attended mode
* extension path
* user-data directory
* debugging configuration
* timeout
* download directory
* proxy configuration if supported
* Anti-Captcha configuration
* browser-specific compatibility flags

Example:

```text
launch_browser(
    browser="chrome",
    mode="attended",
    extension_path="<PROJECT_ROOT>/anticaptcha-plugin_v0.83"
)
```

The same abstraction must work for:

```text
launch_browser("chromium", ...)
launch_browser("chrome", ...)
launch_browser("edge", ...)
```

---

# 7.7 ANTI-CAPTCHA EXTENSION SUPPORT

Anti-Captcha compatibility must be validated for ALL THREE supported browsers.

The extension path MUST be dynamically resolved from the project root:

```text
<PROJECT_ROOT>/anticaptcha-plugin_v0.83
```

NEVER hardcode a developer-specific path such as:

```text
C:\Users\...
```

The installer must verify:

* extension directory exists
* required manifest exists
* manifest is valid
* extension files are complete
* service worker/background configuration is valid
* browser compatibility requirements are satisfied
* extension can actually load in Chromium
* extension can actually load in Google Chrome
* extension can actually load in Microsoft Edge

If browser-specific compatibility differences exist, implement the required compatibility layer rather than disabling the browser.

---

# 7.8 BROWSER COMPATIBILITY TEST

Option [4] must perform an actual browser smoke test for every installed supported browser.

For each available browser:

```text
Launch browser
        ↓
Create automation context
        ↓
Load Anti-Captcha extension
        ↓
Open test page
        ↓
Verify browser DOM interaction
        ↓
Verify JavaScript execution
        ↓
Verify extension availability
        ↓
Close browser
        ↓
Record result
```

Do NOT mark a browser as "Installed" merely because an executable exists.

The result must distinguish:

```text
Installed
Available
Launchable
Automatable
Extension Compatible
Fully Validated
```

---

# 7.9 ATTENDED MODE VALIDATION

Because the application supports attended mode, Option [4] must validate visible browser operation.

For the selected browser:

* browser window must actually appear
* automation must connect
* page navigation must work
* DOM interaction must work
* extension must load
* browser must close cleanly

If Attended Mode is selected, a successful test must NOT be based only on a background/headless process.

---

# 7.10 UNATTENDED MODE VALIDATION

The same browser runtime must also be validated in unattended/headless mode where supported.

Test:

```text
Selected Browser
      ↓
Unattended Launch
      ↓
Automation Context
      ↓
Navigation
      ↓
DOM Interaction
      ↓
Extension/automation validation
      ↓
Clean Shutdown
```

Attended and Unattended modes must use the same browser abstraction and configuration.

A browser passing Attended Mode but failing Unattended Mode is NOT considered fully validated.

---

# 7.11 SYSTEM BROWSER VERSION COMPATIBILITY

For Google Chrome and Microsoft Edge:

* detect installed version
* detect executable path
* verify automation compatibility
* report incompatible versions clearly
* do not silently downgrade the browser
* do not silently replace the user's installed browser
* do not modify unrelated browser installations

For Chromium:

* validate the managed/runtime version against the application's supported Playwright version.

If browser-driver/runtime compatibility is required by the implementation, it must be resolved automatically and safely.

---

# 7.12 PYTHON 3.14.7

The dependency installer MUST remain aligned with:

```text
Python 3.14.7
```

Do NOT downgrade Python.

Verify:

```text
python --version
```

and ensure the backend virtual environment is using Python 3.14.7 or the project's explicitly supported Python 3.14.7 environment.

Install/update:

* FastAPI
* Uvicorn
* Celery
* Redis client
* SQLAlchemy
* Playwright
* RapidFuzz
* Pydantic
* database dependencies
* Excel/CSV/PDF dependencies
* testing dependencies
* linting/formatting dependencies
* all other dependencies actually used by the application

Do not install packages merely because they appear in obsolete files.

---

# 7.13 NODE / FRONTEND DEPENDENCIES

Verify and install the frontend dependencies required by the existing application.

Validate:

* package.json
* lock file
* Next.js/React dependencies
* TypeScript
* UI component dependencies
* export dependencies
* testing dependencies
* build dependencies

Investigate installation warnings such as:

```text
unrs-resolver@1.12.2 install script blocked
```

Do NOT simply ignore the warning.

Determine:

1. Why the install script is blocked.
2. Whether the package is actually required.
3. Whether the dependency can be safely updated.
4. Whether the package manager configuration is responsible.
5. Whether the warning affects development.
6. Whether it affects production builds.
7. Whether it affects runtime functionality.

Fix the underlying issue where required.

---

# 7.14 DO NOT INSTALL UNNECESSARY DEPENDENCIES

Option [4] must be intelligent and idempotent.

Running:

```text
setup-local.ps1
```

multiple times must NOT repeatedly:

* download browsers
* reinstall unchanged packages
* recreate environments unnecessarily
* overwrite valid configuration
* corrupt browser profiles
* reinstall extensions
* kill unrelated applications

The second and subsequent executions should detect already-valid components and reuse them.

---

# 7.15 DEPENDENCY VERSION VALIDATION

After installation/update, produce a dependency validation report:

```text
Python                 PASS
Python Version         3.14.7
Backend Dependencies   PASS
Frontend Dependencies  PASS
Playwright             PASS
Chromium               PASS / NOT REQUIRED
Google Chrome          PASS / NOT INSTALLED
Microsoft Edge         PASS / NOT INSTALLED
Anti-Captcha           PASS
Redis Client           PASS
Celery                 PASS
Database Dependencies  PASS
Testing Dependencies   PASS
Linting                PASS
Build Dependencies     PASS
```

Do not treat "not installed" as a failure when the browser is genuinely optional and not selected.

However, the configured browser MUST always be installed and validated.

---

# 7.16 CONFIGURATION CONSISTENCY

After Option [4]:

* verify Settings browser selection
* verify runtime configuration
* verify browser executable
* verify extension path
* verify attended/unattended mode
* verify scraper configuration
* verify environment variables
* verify backend configuration
* verify Celery configuration
* verify Redis configuration

No dependency installation may silently change production credentials or secrets.

---

# 7.17 SCRAPER COMPATIBILITY VALIDATION

Because all 8 county scrapers depend on the browser automation engine, Option [4] must verify that the browser factory is compatible with:

### Florida

1. Broward
2. Hillsborough
3. Miami-Dade

### Texas

4. Travis
5. Dallas
6. Harris JP
7. Harris District
8. Harris County Clerk

IMPORTANT:

Miami-Dade is ALWAYS Florida.

It must NEVER be classified as Texas.

The dependency validation report must therefore explicitly show:

```text
Florida: 3 scrapers
Texas:   5 scrapers
Total:   8 scrapers
```

---

# 7.18 REAL BROWSER SMOKE TEST

Where practical, perform a real navigation smoke test against the configured county automation environment.

The test must verify:

```text
Application
   ↓
Browser Factory
   ↓
Selected Browser
   ↓
Anti-Captcha Extension
   ↓
County Portal
   ↓
Page Load
   ↓
DOM Interaction
   ↓
Clean Shutdown
```

Do not claim county automation compatibility merely because unit tests passed.

---

# 7.19 FAILURE HANDLING

If one browser fails:

```text
Chromium     PASS
Chrome       PASS
Edge         FAIL
```

Option [4] must report:

```text
Edge validation failed.
Reason: <actual reason>
Executable: <path>
Version: <version>
Recommended action: <action>
```

It must NOT falsely report:

```text
All dependencies installed successfully
```

if the configured browser is broken.

---

# 7.20 SAFE UPDATE POLICY

Dependency updates must:

* preserve existing functionality
* preserve browser support
* preserve Anti-Captcha support
* preserve attended mode
* preserve unattended mode
* preserve all 8 scrapers
* preserve Celery
* preserve Redis
* preserve email/MailDev
* preserve exports
* preserve database functionality
* preserve frontend functionality

After dependency updates, run regression tests.

If an update breaks functionality:

1. identify the package
2. identify the breaking change
3. apply a compatible version/update
4. document the decision
5. rerun all affected tests

Do NOT blindly upgrade every package to the newest version.

---

# 7.21 OPTION [4] MUST NOT CHANGE APPLICATION FUNCTIONALITY

Option [4] is an installation/update/repair operation.

It must NOT:

* remove browser support
* remove scrapers
* remove existing features
* delete configuration
* delete database records
* delete credentials
* change business logic
* disable Anti-Captcha
* force Chrome when another browser is selected
* force Chromium when another browser is selected
* remove Edge support

---

# 7.22 FINAL OPTION [4] ACCEPTANCE CRITERIA

Option [4] is successful only when:

### Python

* [ ] Python 3.14.7 verified
* [ ] backend dependencies installed
* [ ] imports succeed

### Frontend

* [ ] frontend dependencies installed
* [ ] TypeScript passes
* [ ] production/development build passes

### Chromium

* [ ] Chromium detected/installed when required
* [ ] Chromium launches
* [ ] automation works
* [ ] Anti-Captcha compatibility validated

### Google Chrome

* [ ] Google Chrome detected when installed
* [ ] correct executable resolved
* [ ] Chrome launches
* [ ] automation works
* [ ] Anti-Captcha compatibility validated

### Microsoft Edge

* [ ] Microsoft Edge detected when installed
* [ ] correct executable resolved
* [ ] Edge launches
* [ ] automation works
* [ ] Anti-Captcha compatibility validated

### Browser Engine

* [ ] centralized browser factory works
* [ ] browser selection is settings-driven
* [ ] no scraper hardcodes a browser
* [ ] attended mode works
* [ ] unattended mode works
* [ ] browser switching works
* [ ] extension path is dynamically resolved

### RPA

* [ ] all 8 county scrapers remain available
* [ ] Florida = 3
* [ ] Texas = 5
* [ ] Miami-Dade = Florida
* [ ] county routing remains correct
* [ ] real browser smoke test passes

### Dependency Quality

* [ ] no unnecessary Chromium download
* [ ] no repeated unnecessary installation
* [ ] no dependency corruption
* [ ] no silent downgrade
* [ ] no unsupported package versions
* [ ] all installation warnings investigated
* [ ] final dependency report generated

---

# 7.23 CRITICAL RULE

The current Browser Automation Engine UI explicitly supports:

```text
┌──────────────┐
│  Chromium    │
├──────────────┤
│ Google Chrome│
├──────────────┤
│ Microsoft Edge│
└──────────────┘
```

Therefore Option [4] MUST maintain all three.

The implementation must be:

```text
Browser Selection
       ↓
Central Browser Configuration
       ↓
Browser Factory
       ↓
Chromium / Chrome / Edge
       ↓
Anti-Captcha Extension
       ↓
Attended / Unattended RPA
       ↓
All 8 County Scrapers
```

The goal is NOT merely to make dependency installation pass.

The goal is to ensure that **every supported browser is genuinely usable by the real UAIC RPA engine**, while keeping installation fast, repeatable, dynamic, secure, and enterprise-grade.

```

**Important correction to the previous prompt:** the earlier instruction that effectively treated **system Google Chrome as the required browser** should be removed/replaced. Your current UI clearly establishes **Chromium + Google Chrome + Microsoft Edge as supported browser runtimes**, so the setup system should validate all three while using the **currently selected browser from Settings** for actual RPA execution.
```

The current output shows:

```text
Installing Playwright Chromium browser distribution...
System Google Chrome detected at:
C:\Program Files\Google\Chrome\Application\chrome.exe
```

This must be investigated.

The application's real RPA requirement is to use **system Google Chrome**, not bundled Playwright Chromium.

Therefore:

## DO NOT blindly install Playwright Chromium.

Determine exactly whether Playwright Chromium is required anywhere.

If it is not required for the production/local RPA workflow:

- Remove unnecessary Chromium installation from Option [4].
- Do not waste disk space/time installing an unused browser.
- Keep the Playwright Python package if required by the automation.
- Configure browser launch to use the installed Google Chrome executable.

If a bundled browser is genuinely required for automated tests, clearly separate:

```text
Production RPA Browser
=
System Google Chrome

Test-only Browser
=
Playwright-managed browser, if actually required
```

Do not confuse these two.

---

## 7.1 Python Environment

Verify:

```text
Python 3.14.7
```

is used.

Do not downgrade Python.

Create/update the backend virtual environment safely.

Install dependencies from the authoritative dependency files.

Validate:

- Python version
- pip/uv if used
- package installation
- import health
- application startup

---

## 7.2 Frontend Dependencies

Validate:

- Node version
- npm version
- package-lock consistency
- dependency installation
- TypeScript
- Next.js build/runtime dependencies

The warning:

```text
unrs-resolver@1.12.2
postinstall script blocked
```

must be investigated.

Do not simply ignore it.

Determine:

1. Whether the package is required.
2. Whether the blocked script is required.
3. Whether npm configuration intentionally blocks it.
4. Whether the package can be safely installed.
5. Whether there is a better supported dependency version.
6. Whether functionality is affected.

Do not weaken security merely to suppress the warning.

---

## 7.3 Dependency Verification

After installation verify:

```text
Python
FastAPI
Celery
Redis client
Playwright
RapidFuzz
SQLAlchemy
Frontend
Next.js
TypeScript
Required libraries
```

---

# 8. OPTION [5] — PURGE / DELETE DEPENDENCY FOLDERS

This must be a safe and complete cleanup option.

Target only generated dependency/build folders.

At minimum audit:

```text
backend/.venv
node_modules
.next
```

and other generated directories if actually used.

Do NOT delete:

- Source code
- Database
- User data
- Configuration
- `.env`
- Secrets
- Automation settings
- Branding
- County scraper code
- Anti-Captcha extension
- Documentation
- Tests

---

## 8.1 Precondition

Before deleting dependency folders:

1. Detect running services.
2. Stop application services if necessary.
3. Verify no application process is using the folders.
4. Ask for confirmation for destructive cleanup.
5. Delete only approved generated directories.

---

## 8.2 Post-Cleanup Verification

Verify:

```text
Folders removed
No locked files remain
No source files were removed
```

Then Option [4] must be able to recreate the environment successfully.

Test:

```text
Option [5]
→ Option [4]
→ Option [7]
→ Option [1]
→ Option [9]
```

as a complete recovery sequence.

---

# 9. OPTION [6] — CONFIGURE RPA EXECUTION MODE

This option must control the actual RPA engine.

Support:

```text
Attended (GUI)
Unattended (Headless)
```

The selected configuration must be:

- Persisted
- Loaded by backend
- Used by scraper execution
- Reflected by the Setup Console
- Reflected by UI/settings where applicable

Do not create multiple conflicting sources of truth.

---

## 9.1 Mode Switching

Test:

```text
Attended
→ Unattended
→ Attended
→ Unattended
```

without restarting the entire development environment unless technically required.

If restart is required, clearly report it.

---

# 10. OPTION [7] — FULL DIAGNOSTICS & TEST SUITE

Current output reports:

```text
Pytest Suite: ALL TESTS PASSED.
Ruff Linter: ALL CHECKS PASSED.
TypeScript: 0 ERRORS DETECTED.
Docker Compose: CONFIGURATION VALID.
```

However, Pytest still reports:

```text
PytestUnraisableExceptionWarning
Exception ignored while calling deallocator
_proactor_events.py
ValueError: I/O operation on closed pipe
```

Do NOT simply call this "all clean".

Investigate the warning.

Determine whether it originates from:

- Playwright
- Asyncio
- Test fixture lifecycle
- Browser lifecycle
- Windows Proactor event loop
- Unclosed transport
- Improper cleanup
- Another dependency

Fix the root cause if it is application/test related.

If it is a third-party limitation that cannot reasonably be eliminated, document it explicitly and ensure it does not represent a real resource leak.

---

## 10.1 Diagnostics Must Include

At minimum:

### Backend

- Pytest
- Ruff
- Python compilation/import validation
- Application startup test
- Database connectivity
- Redis connectivity
- Celery connectivity
- Configuration validation

### Frontend

- TypeScript
- ESLint if configured
- Build validation
- Import validation

### Infrastructure

- Docker Compose validation
- Port checks
- Service health checks
- Redis health
- MailDev health
- Backend health
- Frontend availability

### RPA

- Chrome detection
- Anti-Captcha extension detection
- Browser launch configuration
- Attended/unattended configuration
- County portal configuration

---

## 10.2 Exit Codes

Option [7] must return a meaningful success/failure state.

If any mandatory test fails:

```text
DIAGNOSTICS FAILED
```

must be reported.

Do not report success because some tests passed.

---

# 11. OPTION [8] — DOCKER STACK DEPLOYMENT

This option must correctly support:

```text
Start
Stop
Restart
Status
```

where appropriate.

Inspect the actual Docker Compose configuration.

Verify:

- Services
- Dependencies
- Ports
- Volumes
- Environment variables
- Health checks
- Restart policies
- Network
- Database
- Redis
- Backend
- Frontend
- Worker
- Beat
- MailDev if containerized
- Any other required service

---

## 11.1 Docker vs Local Mode

Clearly distinguish:

```text
Local/PowerShell Mode
```

from:

```text
Docker Mode
```

Do not accidentally start both versions of the same service on the same port.

For example, do not start:

```text
Local Redis + Docker Redis
```

simultaneously unless explicitly configured.

---

# 12. OPTION [9] — LIVE SERVICE STATUS MONITOR

Option [9] must be a real service monitoring function.

For every service show:

```text
Service
Process
Port
PID if available
Running/Stopped
Healthy/Unhealthy
Response Time if available
Configured/Expected
Last Error
```

At minimum monitor:

- Frontend
- Backend
- Redis
- Celery Worker
- Celery Beat
- MailDev
- Flower/monitoring if applicable

---

## 12.1 Port Verification

Do not only check whether a port is open.

A port being open does not guarantee that the correct application is running.

For HTTP services:

1. Connect.
2. Call the health endpoint.
3. Verify expected response.
4. Report actual health.

For Redis:

- Verify Redis responds correctly.

For Celery:

- Verify worker is actually connected.
- Verify expected queues.
- Verify worker responsiveness where supported.

For MailDev:

- Verify MailDev API/web endpoint.

---

# 13. OPTION [M] — MAILDEV WEB INSPECTOR

MailDev is part of the local development notification/email workflow.

Option [M] must:

1. Detect whether MailDev is running.
2. If not running, clearly report that it is unavailable.
3. Optionally offer to start MailDev if appropriate.
4. Open:

```text
http://localhost:1080
```

only when available.
5. Verify the web endpoint.

---

# 14. MAILDEV MUST BE FULLY INTEGRATED INTO SERVICE LIFECYCLE

MailDev must not be treated as an unrelated optional process if the application depends on it for local email testing.

Ensure:

### Start

Option [1] starts MailDev when local email functionality requires it.

### Stop

Option [2] stops MailDev.

### Status

Option [9] monitors MailDev.

### Diagnostics

Option [7] verifies MailDev.

### Health

Health checks must correctly report MailDev.

### Email Tests

Email test functionality must actually reach MailDev.

---

# 15. CELERY / REDIS VALIDATION

The previous environment showed issues such as:

```text
Automatic queue runner is OFF.
Halting sequential queue advancement.
```

This must be investigated.

Do not assume Celery is working because the worker process exists.

Verify:

```text
Redis
↓
Celery Worker
↓
Celery Beat
↓
Queues
↓
Task Execution
↓
Database
```

Verify that Auto Queue is enabled by default according to the application requirement.

Test an actual queue task.

---

# 16. PROCESS MANAGEMENT MUST BE ROBUST

Do not depend solely on:

```text
taskkill /IM python.exe
```

or similar broad process termination.

That can terminate unrelated user applications.

Implement application-scoped process management.

Where possible track:

- PID
- Command line
- Working directory
- Process owner
- Service identity

Use graceful shutdown first.

Force termination only when necessary.

---

# 17. PORT CONFLICT HANDLING

The application has previously encountered errors such as:

```text
EADDRINUSE :::3000
```

The Setup Console must detect port conflicts before startup.

If port 3000 is already occupied:

1. Determine which process owns the port.
2. Determine whether it belongs to UAIC.
3. If it is already the correct UAIC service, reuse it.
4. If it is an unrelated process, do NOT kill it automatically.
5. Report the conflict clearly.
6. Provide a safe recovery option.

Do the same for all configured ports.

---

# 18. STARTUP RECOVERY

If startup partially succeeds:

Example:

```text
Redis = Started
Backend = Started
Worker = Failed
Frontend = Started
MailDev = Failed
```

the console must clearly report the partial state.

Do not say:

```text
All services started successfully.
```

Provide:

```text
Started
Failed
Skipped
Already Running
Unhealthy
```

for each service.

---

# 19. LOGGING

Every Setup Console operation must have structured logging.

The existing log location pattern is acceptable:

```text
logs/setup_<timestamp>.log
```

but improve it where required.

Logs should capture:

- Timestamp
- Operation
- Service
- Command
- Exit code
- PID
- Port
- Result
- Error
- Recovery action

Do not log:

- Passwords
- API keys
- Tokens
- Secrets
- Credentials

---

# 20. CONSOLE UX

The Setup Console itself should be enterprise-grade.

Requirements:

- Clear menu
- Clear status
- Consistent formatting
- Helpful errors
- No unexplained failures
- No false success messages
- Confirmation for destructive operations
- Progress indicators where appropriate
- Return-to-menu behavior
- Safe cancellation
- Ctrl+C handling
- Invalid input handling
- Repeated execution handling

Invalid selections must not crash the console.

---

# 21. OPTION COMBINATION TESTING

Do not test options only individually.

Test realistic operational sequences.

## Sequence A — Clean Startup

```text
[2] Stop
→ [9] Status
→ [4] Install Dependencies
→ [7] Diagnostics
→ [1] Start Services
→ [9] Status
→ [M] MailDev
```

---

## Sequence B — Clean Rebuild

```text
[2] Stop
→ [5] Purge Dependencies
→ [4] Install Dependencies
→ [7] Diagnostics
→ [1] Start
→ [9] Status
```

---

## Sequence C — Mode Switching

```text
[6] Attended
→ [1] Start
→ Run automation
→ [2] Stop

[6] Unattended
→ [1] Start
→ Run automation
→ [2] Stop
```

---

## Sequence D — MailDev

```text
[1] Start
→ [9] Verify MailDev
→ [M] Open MailDev
→ Send Test Email
→ Verify Email
→ [2] Stop
→ [9] Verify MailDev stopped
```

---

## Sequence E — Docker

```text
[2] Stop Local Services
→ [8] Docker Start
→ [9] Verify
→ [8] Docker Stop
→ [9] Verify
```

---

## Sequence F — Cleanup

```text
[3] Dry Run
→ Review
→ Cancel

[3] Confirm Cleanup
→ Execute
→ Verify Database
→ Verify Dashboard
→ Verify Audit
→ Verify Monitor
```

---

# 22. COMPLETE RECOVERY TEST

Perform this critical test:

```text
Initial State
↓
Stop Everything
↓
Purge Dependencies
↓
Reinstall Dependencies
↓
Run Diagnostics
↓
Start Everything
↓
Check Health
↓
Check Monitor
↓
Open MailDev
↓
Run Test Email
↓
Run Queue Test
↓
Run RPA Test
↓
Verify Database
↓
Verify Audit
↓
Verify Telemetry
↓
Verify Exports
```

The complete environment must recover successfully.

---

# 23. REAL BROWSER VALIDATION

Do not consider RPA startup successful simply because Python starts.

In **Attended mode**, execute an actual automation test.

Verify:

```text
Setup Console
→ Attended Mode
→ Backend
→ Celery
→ Queue
→ RPA task
→ System Google Chrome
→ Anti-Captcha extension
→ County Portal
→ Search
→ Result
→ Database
→ Telemetry
```

The browser must actually become visible.

---

# 24. COUNTY PORTAL VALIDATION

The Setup Console changes must not break the eight-county automation.

Verify all eight:

### Florida

1. Broward
2. Hillsborough
3. Miami-Dade

### Texas

4. Travis
5. Dallas
6. Harris JP
7. Harris District
8. Harris County Clerk

Miami-Dade must remain classified as **Florida**, never Texas.

Each portal must be tested from its configured home page through the actual search flow.

---

# 25. ATTENDED / UNATTENDED PARITY

The same business workflow must work in:

```text
Attended GUI
```

and:

```text
Unattended Headless
```

Do not allow a situation where:

```text
Attended works
Unattended fails
```

or vice versa.

Test both modes after Setup Console changes.

---

# 26. PYTHON 3.14.7 REQUIREMENT

The solution must remain compatible with:

```text
Python 3.14.7
```

Do not downgrade Python to make Setup Console functionality work.

If a dependency is incompatible:

1. Identify it.
2. Find a compatible version.
3. Upgrade/replace it safely.
4. Test it.

---

# 27. SECURITY REQUIREMENTS

Do not expose:

- Passwords
- API keys
- Tokens
- CAPTCHA credentials
- Guidewire credentials
- Email credentials

Do not print `.env` contents into logs.

Do not use insecure broad process termination.

Do not automatically kill unrelated applications.

---

# 28. TEST AUTOMATION

Create automated tests for Setup Console functionality where practical.

Test:

- Menu parsing
- Service registry
- Port detection
- Process detection
- Startup
- Shutdown
- MailDev lifecycle
- Dependency installation validation
- Cleanup safety
- Diagnostics
- Docker validation
- Health monitoring
- RPA mode configuration
- Invalid input
- Idempotency
- Failure recovery

For operations that require real Windows processes, supplement unit tests with controlled integration tests.

---

# 29. REAL MANUAL/BROWSER QA

After automated tests pass, actually run the Setup Console.

Do not rely only on unit tests.

Manually execute:

```text
[1]
[2]
[3]
[4]
[5]
[6]
[7]
[8]
[9]
[M]
[0]
```

and test all important combinations.

Record the actual observed result.

---

# 30. FINAL VALIDATION MATRIX

Create a final matrix similar to:

| Option | Tested | Passed | Real Execution | Recovery Tested | Evidence |
|---|---|---|---|---|---|
| [1] Start | | | | | |
| [2] Stop | | | | | |
| [3] Cleanup | | | | | |
| [4] Dependencies | | | | | |
| [5] Purge | | | | | |
| [6] RPA Mode | | | | | |
| [7] Diagnostics | | | | | |
| [8] Docker | | | | | |
| [9] Status | | | | | |
| [M] MailDev | | | | | |

Do not mark an option "Passed" unless it was actually executed and verified.

---

# 31. REQUIRED ACCEPTANCE CONDITIONS

The work is NOT complete unless all of the following are true:

### Setup Console

- [1] works
- [2] works
- [3] works
- [4] works
- [5] works
- [6] works
- [7] works
- [8] works
- [9] works
- [M] works
- [0] works

### Service Lifecycle

- Frontend lifecycle works
- Backend lifecycle works
- Celery lifecycle works
- Celery Beat lifecycle works
- Redis lifecycle works
- MailDev lifecycle works
- Monitoring lifecycle works where applicable

### Critical Correction

**Option [2] MUST stop MailDev and release port 1080.**

### Dependencies

- Python 3.14.7 verified
- Required dependencies installed
- Unnecessary Playwright Chromium installation removed or explicitly justified
- System Google Chrome verified
- npm dependency warnings investigated

### Diagnostics

- Pytest passes
- Ruff passes
- TypeScript passes
- Build passes
- Docker configuration passes
- No unexplained resource warnings
- Service health checks pass

### RPA

- Attended mode works
- Unattended mode works
- System Chrome works
- Anti-Captcha extension works
- Queue works
- Auto Queue works
- Eight county portals remain functional
- Miami-Dade remains Florida

### Operations

- Startup works
- Shutdown works
- Restart works
- Recovery works
- Port conflicts are handled safely
- Partial failures are reported correctly
- Logs are generated
- Secrets are protected

---

# 32. DO NOT ACCEPT THESE FALSE SUCCESS CONDITIONS

The following are NOT sufficient:

```text
PowerShell command exited with code 0
```

```text
Process was launched
```

```text
Port is listening
```

```text
Pytest passed
```

```text
TypeScript passed
```

```text
Docker Compose is valid
```

A service is considered working only when its **actual expected behavior is verified**.

For example:

```text
MailDev "started"
```

is not enough.

The system must verify:

```text
MailDev process exists
→ Port 1080 is listening
→ MailDev HTTP endpoint responds
→ MailDev can receive a test email
→ Email appears in MailDev
```

Similarly:

```text
Celery worker "started"
```

is not enough.

Verify:

```text
Worker connected to Redis
→ Worker registered expected tasks
→ Worker consumes queue
→ Test task executes
→ Result/state is persisted
```

---

# 33. DOCUMENTATION

Update all relevant project documentation.

At minimum review:

- Setup instructions
- Local development instructions
- RPA execution mode documentation
- Service architecture documentation
- Dependency installation documentation
- Docker documentation
- MailDev documentation
- Troubleshooting documentation
- Testing documentation
- Operations/runbook documentation

Document:

- What each option does
- Required services
- Ports
- Dependencies
- Attended mode
- Unattended mode
- MailDev
- Docker mode
- Cleanup behavior
- Recovery procedures

---

# 34. FINAL REPORT

At the end provide a clear report containing:

## A. Root Causes Found

List every actual issue discovered.

## B. Changes Implemented

List every code/configuration/documentation change.

## C. Setup Console Validation

Show the result of:

```text
[1]
[2]
[3]
[4]
[5]
[6]
[7]
[8]
[9]
[M]
[0]
```

## D. Service Validation

Show:

```text
Frontend
Backend
Redis
Celery Worker
Celery Beat
MailDev
Monitoring
```

with actual status.

## E. Test Results

Include:

- Pytest
- Ruff
- TypeScript
- Build
- Docker
- Integration tests
- RPA tests
- Attended tests
- Unattended tests

## F. Known Warnings

Do not hide warnings.

Explain each remaining warning and whether it represents an actual problem.

## G. Regression Results

Confirm that existing application functionality remains intact.

## H. Evidence

Provide actual evidence such as:

- Logs
- Test results
- Screenshots where appropriate
- Service status
- Port verification
- Email verification
- Browser execution
- Queue execution
- Database verification

---

# 35. FINAL DEFINITION OF DONE

The Setup Console is considered complete only when:

**Every menu option is functional.**

**Every service that the application actually uses is represented in the lifecycle management.**

**MailDev is explicitly included in start, stop, status, diagnostics, and email testing.**

**Option [2] successfully stops MailDev and releases port 1080.**

**Option [4] does not unnecessarily install Playwright Chromium when system Google Chrome is the required RPA browser.**

**Option [7] does not hide or ignore meaningful warnings.**

**Option [9] verifies actual service health rather than merely checking processes or ports.**

**Option [1] starts the complete working environment.**

**Option [2] cleanly stops the complete working environment.**

**Option [3] safely cleans selected data without corrupting relationships or configuration.**

**Option [5] safely removes generated dependencies only.**

**Option [6] actually controls Attended/Unattended RPA execution.**

**Option [8] correctly manages Docker mode without conflicting with local services.**

**Option [M] correctly handles MailDev.**

**The complete environment can be destroyed and recreated successfully.**

**Attended RPA works with visible system Google Chrome.**

**Unattended RPA works without GUI dependency.**

**The eight county court portals remain functional.**

**The application remains compatible with Python 3.14.7.**

**All changes are documented and covered by repeatable test cases.**

Most importantly:

> **Do not report completion based on code inspection or command exit codes. Execute every option, verify its real-world result, fix every failure discovered, and repeat the complete regression cycle until the Setup Console and the application it controls operate reliably as an enterprise-grade local operations console.**