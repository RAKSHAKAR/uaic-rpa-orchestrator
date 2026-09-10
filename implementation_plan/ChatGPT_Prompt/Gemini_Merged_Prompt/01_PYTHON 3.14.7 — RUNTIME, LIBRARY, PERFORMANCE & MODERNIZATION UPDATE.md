# PYTHON 3.14.7 — RUNTIME, LIBRARY, PERFORMANCE & MODERNIZATION UPDATE

You must now update the existing implementation to officially target and support:

**Python 3.14.7**

Python 3.14.7 is already installed on the development machine and must be treated as the target Python runtime for the backend.

Do NOT downgrade Python to an older version merely because the existing project was originally built for an older Python release.

---

## 1. Python Runtime Requirement

First verify the currently installed Python runtime:

```powershell
python --version
python -c "import sys; print(sys.version)"
```

The expected runtime is:

```text
Python 3.14.7
```

Also verify:

```powershell
py --version
python -m pip --version
```

The backend must be developed and tested against Python 3.14.7.

If multiple Python versions are installed, explicitly configure the project/virtual environment so that the backend uses Python 3.14.7.

Do not silently use:

- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- or any other older runtime

unless a specific third-party dependency has been proven incompatible with Python 3.14.7.

If a dependency is incompatible, do NOT immediately downgrade Python.

Instead:

1. Check whether a newer compatible version exists.
2. Upgrade the dependency.
3. Check whether an alternative maintained library exists.
4. Refactor the affected code if required.
5. Only if absolutely unavoidable, document the incompatibility clearly.

---

# 2. Audit the Existing Backend Before Changing Anything

Do NOT rebuild the backend.

Inspect the existing backend completely.

Review:

- `requirements.txt`
- `requirements*.txt`
- `pyproject.toml`
- `setup.py`
- `setup.cfg`
- `Pipfile`
- `poetry.lock`
- `uv.lock`
- `requirements.lock`
- Docker files
- PowerShell setup scripts
- startup scripts
- `.env` handling
- FastAPI/Flask/Django configuration
- database layer
- ORM
- browser automation implementation
- queue/worker implementation
- API clients
- Excel/CSV processing
- CAPTCHA/Anti-Captcha integration
- logging
- configuration management
- test dependencies

Determine exactly which Python libraries are currently being used and why.

Create an internal dependency compatibility matrix:

| Library | Current Version | Python 3.14 Compatible? | Latest Suitable Version | Action |
|---|---:|---|---:|---|
| FastAPI | existing | verify | latest compatible | update if safe |
| Uvicorn | existing | verify | latest compatible | update if safe |
| Pydantic | existing | verify | latest compatible | update if safe |
| SQLAlchemy | existing | verify | latest compatible | update if safe |
| Playwright | existing | verify | latest compatible | update if safe |
| HTTP client | existing | verify | latest compatible | update if safe |
| Pandas | existing | verify | latest compatible | update if safe |
| Excel library | existing | verify | latest compatible | update if safe |
| Test framework | existing | verify | latest compatible | update if safe |

This is an audit requirement, not an optional activity.

---

# 3. Use Modern Python 3.14 Code

Where existing code is outdated, modernize it using current Python practices while preserving behavior.

Prefer:

- modern type hints
- `dataclasses` where appropriate
- `Enum`
- `StrEnum` where appropriate
- `TypedDict` where appropriate
- `Protocol` where appropriate
- `TypeAlias`
- structured configuration models
- `async` / `await`
- async context managers
- `asyncio`
- modern exception handling
- modern pathlib APIs
- context managers
- dependency injection
- immutable configuration where appropriate
- clear separation of concerns

Avoid unnecessary legacy patterns.

For example, prefer modern type syntax such as:

```python
def get_record(record_id: str) -> dict[str, object]:
    ...
```

rather than unnecessarily verbose legacy typing where the newer syntax is appropriate.

Use:

```python
from pathlib import Path
```

instead of manual string-based path manipulation.

Use proper resource management:

```python
async with ...
```

or:

```python
with ...
```

where applicable.

Do not introduce clever Python syntax merely to appear modern.

**Correctness, maintainability and performance are more important than novelty.**

---

# 4. Async Architecture

Review the backend for unnecessary blocking operations.

The application contains:

- API requests
- database operations
- queue processing
- browser automation
- external API calls
- fuzzy-match API calls
- Guidewire API calls
- file processing
- Excel/CSV processing

Do not block the API event loop unnecessarily.

Where supported by the selected libraries, use asynchronous APIs.

For example:

```python
async def process_record(...):
    ...
```

Use async HTTP clients for external HTTP APIs where appropriate.

Do not make synchronous HTTP requests from an async endpoint.

Do not use:

```python
requests.get(...)
```

inside an async request handler if an async HTTP client is appropriate.

Use a modern async HTTP client such as the currently supported version of `httpx` or another maintained equivalent when appropriate.

---

# 5. IMPORTANT — Browser Automation Is Different

Do NOT attempt to make browser automation artificially asynchronous if that would make the automation unstable.

The browser automation must remain reliable.

The priority is:

1. Correct browser behavior
2. Reliable CAPTCHA handling
3. Correct extraction
4. Correct tab/session management
5. Recovery/retry
6. Then performance

Use the asynchronous Playwright APIs if the existing implementation and extension architecture support them reliably.

However, if the Anti-Captcha browser extension requires a persistent Chrome context or a specific browser-launch architecture, preserve that requirement.

Do NOT switch from normal Chrome to bundled Chromium just to make Playwright implementation easier.

The automation must continue to use the **normal/default Chrome installation** required by the existing Anti-Captcha extension.

---

# 6. Modern Browser Automation Architecture

Refactor browser automation into clean reusable components if the current implementation is fragmented.

Recommended conceptual architecture:

```text
BrowserManager
    |
    +── ChromeSession
    |
    +── ExtensionManager
    |
    +── CaptchaManager
    |
    +── TabManager
    |
    +── SiteAutomationManager
             |
             +── BrowardAdapter
             +── HillsboroughAdapter
             +── MiamiAdapter
             +── DallasAdapter
             +── TravisAdapter
             +── HarrisJPAdapter
             +── HarrisDistrictAdapter
             +── HarrisCountyClerkAdapter
```

Each site adapter should have a clear contract.

For example:

```python
class CountySiteAdapter(Protocol):
    async def search(...)
    async def extract_results(...)
    async def paginate(...)
    async def cleanup(...)
```

Do not duplicate browser/session/CAPTCHA logic across eight site implementations.

---

# 7. Connection Pooling

Where applicable, use connection pooling for:

- PostgreSQL
- HTTP clients
- external APIs

Do not create a new HTTP client for every API request.

Do not create a new database connection for every record.

Prefer reusable application-scoped clients/pools.

Example concept:

```text
Application
   |
   +── DB Pool
   |
   +── HTTP Client Pool
   |
   +── Worker
   |
   +── Browser Session Manager
```

Ensure resources are properly closed during application shutdown.

---

# 8. Database Performance

Audit all database queries.

Look specifically for:

- N+1 queries
- repeated queries inside loops
- unnecessary SELECT *
- missing indexes
- loading thousands of records into memory
- unnecessary serialization/deserialization
- repeated status queries
- inefficient pagination
- unnecessary commits
- excessive transactions

Use appropriate indexes for:

- status
- state
- claim number
- queue status
- created timestamp
- updated timestamp
- processing timestamp
- retry count
- site status
- fuzzy-match status

Do NOT add indexes blindly.

Only add indexes that support actual query patterns.

---

# 9. Queue Performance

The queue must remain reliable and sequential where business logic requires sequential processing.

Do NOT sacrifice correctness for concurrency.

The required processing model remains:

```text
Record 1
   ↓
Process selected sites
   ↓
Complete Record 1
   ↓
Record 2
   ↓
Process selected sites
   ↓
Complete Record 2
```

However, optimize everything around that sequential business rule.

For example:

- avoid repeated database polling
- use efficient queue queries
- minimize serialization
- reuse browser resources during one record
- reuse tabs
- minimize unnecessary page reloads
- avoid opening irrelevant sites
- avoid unnecessary browser startup
- avoid repeated authentication
- avoid unnecessary API calls

If concurrency is introduced anywhere, it must not violate the required record-processing semantics.

---

# 10. Browser Startup Optimization

Do not launch Chrome unnecessarily.

Required behavior:

```text
Start record
    ↓
Determine required states/sites
    ↓
Launch normal Chrome once
    ↓
Open only required sites
    ↓
Reuse tabs
    ↓
Process record
    ↓
Finish all required sites
    ↓
Close Chrome
```

Do NOT:

```text
Record
 → Chrome
 → close
 → Chrome
 → close
 → Chrome
```

for every individual site.

Likewise, do not open all eight sites when only Florida or only Texas sites are required.

---

# 11. CAPTCHA Performance

CAPTCHA handling must be event/condition based wherever possible.

Avoid arbitrary large sleeps such as:

```python
await asyncio.sleep(60)
```

when the page can be monitored for a real condition.

Prefer:

```text
Click CAPTCHA
      ↓
Monitor CAPTCHA state
      ↓
Detect successful verification
      ↓
Continue immediately
```

The configured timeout remains the upper limit.

Do not wait the entire timeout if CAPTCHA is already solved.

If CAPTCHA is not solved within the configured timeout:

```text
CAPTCHA timeout
      ↓
Record diagnostic information
      ↓
Refresh page
      ↓
Retry
```

Use the existing Settings configuration for timeout/retry values.

Do not hardcode credentials or API keys.

---

# 12. HTTP/API Performance

Audit every external API integration.

Use:

- connection reuse
- sensible timeouts
- retries only where appropriate
- exponential backoff where appropriate
- idempotency where appropriate
- response validation
- structured errors

Do not retry permanent 4xx errors unnecessarily.

Retry transient failures such as:

- connection reset
- timeout
- 502
- 503
- 504

when appropriate.

Do not create infinite HTTP retries.

All retry limits must be configurable.

---

# 13. FastAPI Modernization

If the current backend uses FastAPI, ensure it follows current supported FastAPI patterns.

Review:

- lifespan management
- dependency injection
- Pydantic models
- response models
- validation
- middleware
- exception handlers
- CORS
- authentication
- background processing

Prefer application lifespan management for long-lived resources such as:

- DB connection pools
- HTTP clients
- browser managers
- worker managers

Do not initialize expensive resources repeatedly per request.

---

# 14. Pydantic Modernization

If Pydantic is used, use the currently supported major version compatible with Python 3.14.7 and the selected FastAPI version.

Audit old Pydantic patterns.

Modernize models where safe.

Do not change API contracts unnecessarily.

Existing frontend/backend JSON contracts must remain backward compatible unless the change is explicitly required.

---

# 15. Dependency Management

Replace obsolete or abandoned dependencies when there is a safe maintained alternative.

Before changing a dependency:

1. Determine why it is used.
2. Check the current API.
3. Check Python 3.14 compatibility.
4. Check whether the replacement changes behavior.
5. Update imports/code.
6. Run tests.
7. Run integration tests.
8. Run browser automation smoke tests.

Do not perform blind mass upgrades.

Do not use packages that are:

- abandoned
- unmaintained
- known vulnerable
- incompatible with Python 3.14
- unnecessary duplicates of standard-library functionality

---

# 16. Requirements File

Update the backend dependency specification appropriately.

The final dependency file must:

- support Python 3.14.7
- use compatible current stable releases
- avoid unnecessary dependencies
- avoid duplicate packages
- clearly separate runtime and development/test dependencies if appropriate

Where appropriate, use version constraints that prevent accidental installation of incompatible future major versions.

Example concept:

```text
package>=minimum,<next-breaking-major
```

Use the actual appropriate constraints after verifying compatibility.

Do NOT invent package versions without checking compatibility.

---

# 17. Python Environment

Create/update the project's virtual environment using Python 3.14.7.

For Windows, verify the setup process works using commands equivalent to:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
```

Then install the project dependencies.

The setup script must not silently select another Python version.

If an existing `setup.ps1` exists, inspect and update it safely.

Preserve existing cleanup/reset functionality.

Do not make cleanup scripts destructive beyond their documented purpose.

---

# 18. Development Tooling

Modernize development tooling where appropriate.

Consider current maintained tools for:

- formatting
- linting
- type checking
- testing
- dependency auditing

For example, evaluate modern tooling such as:

- Ruff
- Pyright or mypy
- pytest
- pytest-asyncio
- coverage

Do not introduce every tool automatically.

Use a practical, maintainable toolchain.

---

# 19. Logging Performance

Use structured logging.

Do not build huge strings unnecessarily.

Do not log:

- passwords
- API keys
- tokens
- cookies
- session secrets
- sensitive authentication data

Log useful execution information such as:

```text
record_id
claim_number
state
site
run_id
attempt
duration
status
error_type
```

Use correlation/run IDs so one automation run can be traced across:

```text
Frontend
 → API
 → Queue
 → Browser
 → Site
 → Database
 → Fuzzy Match
 → Guidewire
```

---

# 20. Memory Usage

The application may process a large number of records.

Do NOT load the entire database into memory.

Use:

- pagination
- streaming
- generators where appropriate
- batch processing
- incremental exports

Excel/CSV export must remain efficient for large datasets.

Avoid constructing unnecessarily large Python lists when streaming is possible.

---

# 21. Excel/CSV Performance

The existing export requirement remains mandatory.

Support:

- CSV
- Excel/XLSX

Exports must respect:

- active filters
- selected columns
- date filters
- status filters
- search criteria

For large datasets, do not load the entire dataset into memory if the selected library supports streaming/write-only approaches.

---

# 22. File Upload Performance & Security

If Excel/CSV imports are supported:

- validate file type
- validate extension
- validate MIME type where appropriate
- enforce file-size limits
- prevent path traversal
- sanitize filenames
- validate columns
- validate data types
- process large files efficiently
- report row-level validation errors
- avoid loading unnecessarily large files into memory

Do not trust the uploaded filename or MIME type alone.

---

# 23. Caching

Where appropriate, introduce caching for data that is:

- expensive to calculate
- rarely changing
- safe to cache

Do NOT cache dynamic automation results incorrectly.

Do not cache:

- CAPTCHA state
- browser session state
- real-time queue state
- mutable site results

unless the cache design explicitly guarantees correctness.

---

# 24. Performance Measurement

Do not claim that the application is "faster" without measuring it.

Before optimization, identify major bottlenecks.

Measure:

- API response time
- database query time
- queue pickup time
- browser startup time
- tab startup time
- CAPTCHA processing time
- site search time
- extraction time
- fuzzy-match API time
- Guidewire API time
- total record processing time

After optimization, compare results.

Where practical, record:

```text
duration_ms
```

for important operations.

---

# 25. Do NOT Break Existing Functional Behavior

This is extremely important.

Python modernization must NOT change the established business behavior.

Do not accidentally change:

- state routing
- site selection
- name-search logic
- DOL conversion
- output field semantics
- queue sequencing
- status values
- CAPTCHA retry behavior
- browser/tab behavior
- fuzzy matching
- Guidewire payload
- retry rules
- existing API contracts
- frontend behavior

Modernize the implementation underneath the existing business behavior.

---

# 26. Python 3.14 Compatibility Gate

Before declaring the implementation complete, run a compatibility check.

Verify:

```text
Python = 3.14.7
Backend starts successfully
All imports succeed
Database connects
Migrations succeed
API starts
API health endpoint works
Queue starts
Browser automation starts
Normal Chrome launches
Anti-Captcha extension loads
Settings are read correctly
CAPTCHA manager works
All site adapters initialize
Fuzzy API integration works
Guidewire integration works in configured test mode
Tests pass
```

There must be no hidden fallback to an older Python installation.

---

# 27. Performance Regression Test

After modernization, run the existing test suite.

Then specifically test:

### Backend

- startup
- authentication
- settings
- CRUD
- pagination
- filtering
- sorting
- bulk operations
- imports
- exports
- queue
- retries
- status updates
- API validation

### Automation

- browser startup
- extension loading
- CAPTCHA handling
- Florida workflow
- Texas workflow
- multi-site tab reuse
- site failures
- retry
- timeout
- browser cleanup

### Data

- Excel import
- DOL conversion
- state routing
- search-count logic
- JSON output
- status updates
- fuzzy matching
- Guidewire payload

---

# 28. Frontend Must Remain Compatible

Do not make Python backend changes that unnecessarily break the existing Next.js frontend.

If an API response needs improvement, maintain backward compatibility where possible.

If a breaking change is genuinely necessary:

1. Update backend.
2. Update frontend.
3. Update tests.
4. Update API documentation.
5. Verify all affected screens.

Do not leave frontend calls pointing to obsolete endpoints.

---

# 29. Performance Optimization Priority

Use this priority order:

```text
1. Correctness
2. Reliability
3. Security
4. Data integrity
5. Browser automation stability
6. API responsiveness
7. Database performance
8. Queue performance
9. Memory efficiency
10. Startup performance
11. UI performance
12. Micro-optimizations
```

Do NOT optimize code at the expense of automation reliability.

---

# 30. Final Python Modernization Requirement

At the end of implementation, provide a concise engineering report containing:

### Runtime

```text
Python version:
Python executable:
Virtual environment:
```

### Dependency modernization

```text
Updated packages:
Removed packages:
Replaced packages:
Packages intentionally kept:
```

### Performance improvements

```text
Before:
After:
Improvement:
```

where actual measurements are available.

### Compatibility

Confirm:

```text
Python 3.14.7 compatible: YES/NO
Backend startup: PASS/FAIL
Tests: PASS/FAIL
Browser automation: PASS/FAIL
Chrome extension: PASS/FAIL
Florida automation: PASS/FAIL
Texas automation: PASS/FAIL
Database: PASS/FAIL
Queue: PASS/FAIL
Fuzzy matching: PASS/FAIL
Guidewire integration: PASS/FAIL
```

Do not report PASS unless it was actually tested.

---

# FINAL INSTRUCTION

Do not simply update `requirements.txt`.

This is a **full Python 3.14.7 modernization and performance pass over the existing application**.

Inspect the existing implementation first, identify outdated code/dependencies, safely modernize them, preserve all existing business behavior, improve performance where measurable, run the complete test suite, fix all resulting issues, and verify the actual application through the browser.

Do not stop at analysis.

**Implement → test → measure → fix → retest → verify.**