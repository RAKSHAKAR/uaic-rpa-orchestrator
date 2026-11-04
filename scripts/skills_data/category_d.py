"""
Category D: Code Quality & Maintenance
Contains 15 comprehensive skills for code review, refactoring, dead code cleanup,
performance tuning, error handling, security auditing, and coding standards.
"""

SKILLS_D = [
    {
        "name": "code-review",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Review code changes for correctness, maintainability, security, performance, test coverage, and project conventions.",
        "purpose": "Conducts a rigorous, objective code review against repository standards, detecting subtle logic flaws, unhandled exceptions, performance bottlenecks, and security vulnerabilities before merging.",
        "when_to_use": [
            "Reviewing pull requests or local working tree diffs before committing.",
            "Auditing complex algorithmic changes or security-critical code."
        ],
        "when_not_to_use": [
            "Trivial documentation typo corrections."
        ],
        "required_inputs": [
            "Git diff or modified file paths, target requirements, and repository coding standards (`AGENTS.md`)."
        ],
        "prerequisites": [
            "Clean working tree or specific commit range to review."
        ],
        "procedure": [
            ("Diff Scope & Context Inspection", "Inspect git diff (`git diff HEAD~1` or working tree). Check which files were added, modified, or removed."),
            ("Correctness & Logic Verification", "Verify that the code satisfies the stated requirements without off-by-one errors, unhandled nulls, or broken invariants."),
            ("Security & Data Protection Audit", "Check for SQL injection, unescaped parameters, leaked credentials, hardcoded secrets, and unsafe deserialization."),
            ("Performance & Resource Management", "Identify N+1 database queries, unclosed async sessions, memory leaks, unindexed query filters, or unbounded loops."),
            ("Style, Standards & Test Coverage Audit", "Verify adherence to project formatting (Ruff, ESLint), TypeScript strictness, and automated test coverage."),
            ("Review Summary & Findings Synthesis", "Produce a structured review report categorizing findings into: Critical Blockers, Improvements, and Commendations.")
        ],
        "safety": [
            "Never approve code that breaks pre-existing unit or integration tests.",
            "Never overlook hardcoded API tokens or unmasked credentials."
        ],
        "deliverables": [
            "Structured Code Review Report with line-specific findings and recommendations.",
            "Approved or Blocked status recommendation."
        ],
        "acceptance_criteria": [
            "All changed files are reviewed line by line.",
            "Security, performance, and correctness issues are identified with code snippets.",
            "Review explicitly confirms whether automated test coverage is adequate."
        ],
        "error_recovery": [
            "If review findings reveal architectural defects, request redesign before further coding."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/code-review`.",
            "cursor": "Select `@code-review` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `code-review`.",
            "codex": "Reference `code-review` in Codex context.",
            "gemini": "Invoke via `gemini run code-review`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt code-review`.",
            "windsurf": "Activate `code-review` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Definition of Done & Must Do / Must Not Do)",
            "`ruff.toml`"
        ]
    },
    {
        "name": "code-refactoring",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Improve internal code structure, readability, and modularity without changing externally observable behavior.",
        "purpose": "Restructures complex, coupled, or duplicated code into clean, maintainable abstractions while preserving 100% behavioral parity backed by automated regression tests.",
        "when_to_use": [
            "Simplifying oversized functions or classes (e.g. monolithic scraper classes).",
            "Eliminating duplicated logic across Florida and Texas scrapers.",
            "Improving modularity and testability of backend services."
        ],
        "when_not_to_use": [
            "Adding new functional capabilities (keep refactoring and feature additions in separate turns).",
            "When test suites are broken or missing."
        ],
        "required_inputs": [
            "Target code module, existing test suites, and refactoring objectives."
        ],
        "prerequisites": [
            "100% passing test baseline for the target module before touching code."
        ],
        "procedure": [
            ("Baseline Test Pass Verification", "Execute existing test suites to confirm green baseline: `pytest` and `npx tsc --noEmit`."),
            ("Refactoring Strategy Formulation", "Identify specific code smells (Long Method, Feature Envy, Duplicate Code). Plan incremental transformations (Extract Method, Introduce Parameter Object)."),
            ("Incremental Atomic Transformation", "Apply transformations one at a time. Keep public interfaces and signatures identical or provide backward-compatibility wrappers."),
            ("Continuous Test Re-execution", "Rerun the test suite after every single transformation to guarantee zero behavioral regressions."),
            ("Lint & Type Checking", "Run `ruff check` and `tsc --noEmit` to ensure pristine code quality."),
            ("Refactoring Summary", "Document structural improvements, eliminated lines of code, and verified test results.")
        ],
        "safety": [
            "CRITICAL: Never change external API contracts or database schemas during a pure refactoring task.",
            "Never proceed to the next refactoring step if tests are failing."
        ],
        "deliverables": [
            "Refactored source code files with improved readability and cohesion.",
            "Regression test report proving 100% behavioral equivalence."
        ],
        "acceptance_criteria": [
            "All pre-existing tests pass with zero modifications to test assertions.",
            "Cyclomatic complexity and function line counts are reduced.",
            "Zero new linting or type-checking errors introduced."
        ],
        "error_recovery": [
            "If a refactoring step breaks behavioral tests, immediately revert the step via git and choose an alternative transformation."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/code-refactoring`.",
            "cursor": "Select `@code-refactoring` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `code-refactoring`.",
            "codex": "Reference `code-refactoring` in Codex context.",
            "gemini": "Invoke via `gemini run code-refactoring`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt code-refactoring`.",
            "windsurf": "Activate `code-refactoring` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py`",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "code-cleanup",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Remove unnecessary artifacts, orphan files, debug statements, and commented-out code only after confirming zero references.",
        "purpose": "Safely purges stale files, temporary debug scripts, unused import statements, and commented-out blocks, reducing codebase clutter and technical debt.",
        "when_to_use": [
            "Following completion of a major feature implementation.",
            "Pre-release repository hygiene passes.",
            "Cleaning up temporary diagnostic dumps or scratch files."
        ],
        "when_not_to_use": [
            "Removing code whose usage or downstream dependency is unverified."
        ],
        "required_inputs": [
            "Candidate cleanup targets, repository search tools, and test suites."
        ],
        "prerequisites": [
            "Git status clean or committed baseline."
        ],
        "procedure": [
            ("Target Candidate Identification", "Identify candidate cleanup items: temporary scripts in `scripts/`, orphan components, unused imports, or leftover `print()`/`console.log()` statements."),
            ("Reference & Dependency Verification", "Search the entire codebase for references to each candidate symbol or file. Check dynamic imports, settings strings, and documentation links."),
            ("Protected Directory Exclusions", "Verify that no candidates belong to protected directories (`anticaptcha-plugin_v0.83`, `.agents`)."),
            ("Safe Deletion or Pruning", "Remove confirmed dead files or strip debugging code."),
            ("Full Test Suite Verification", "Execute backend pytest suites and frontend TypeScript compile to prove zero broken imports."),
            ("Cleanup Report", "Document all deleted files and purged lines of dead code.")
        ],
        "safety": [
            "CRITICAL: Never delete files from `anticaptcha-plugin_v0.83` or `.agents`.",
            "Do NOT delete loose `.xlsx` or `.csv` files that serve as client demo or test fixtures without explicit approval."
        ],
        "deliverables": [
            "Cleaned codebase with reduced clutter.",
            "Cleanup audit log detailing removed artifacts and verification evidence."
        ],
        "acceptance_criteria": [
            "Zero broken import statements or runtime missing file errors.",
            "`ruff check` reports zero unused imports (`F401`).",
            "All unit and integration tests continue passing."
        ],
        "error_recovery": [
            "If a deletion causes test failures, restore the file immediately using `git checkout`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/code-cleanup`.",
            "cursor": "Select `@code-cleanup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `code-cleanup`.",
            "codex": "Reference `code-cleanup` in Codex context.",
            "gemini": "Invoke via `gemini run code-cleanup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt code-cleanup`.",
            "windsurf": "Activate `code-cleanup` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 2 (Repository Layout) & Section 8 (Must Not Do)"
        ]
    },
    {
        "name": "duplicate-code-detection",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Identify duplicated logic, copy-pasted helper functions, repetitive UI patterns, and redundant scraper routines.",
        "purpose": "Detects structural duplication across Python scrapers, API endpoints, and React components, recommending clean abstractions to reduce maintenance overhead and bug propagation.",
        "when_to_use": [
            "Auditing scraper implementations across the 8 court portals.",
            "Standardizing error handling or date formatting logic across services.",
            "Refactoring repetitive UI form components or stat cards."
        ],
        "when_not_to_use": [
            "Accidental syntactic similarity across completely unrelated business domains."
        ],
        "required_inputs": [
            "Target directories (`backend/app/automation/`, `frontend/src/components/`)."
        ],
        "prerequisites": [
            "Understanding of DRY (Don't Repeat Yourself) principles and when duplication is preferable to wrong abstraction."
        ],
        "procedure": [
            ("Static Similarity Scanning", "Scan codebase for duplicated blocks: date formatting, table parsing, CAPTCHA wait loops, and API error formatting."),
            ("Duplication Classification", "Classify duplication: Exact Duplication (identical code), Semantic Duplication (same logic, different variable names), or Incidental Duplication."),
            ("Consolidation Proposal", "Design a shared abstraction (e.g. `BasePortalScraper` helper method or shared React hook)."),
            ("Impact & Blast Radius Check", "Verify which callers will be affected by consolidating the duplicated routines."),
            ("Consolidation & Regression Verification", "Extract shared routine, update callers, and execute automated test suites.")
        ],
        "safety": [
            "Do NOT force artificial abstractions onto portals with subtle DOM differences.",
            "Ensure portal-specific output schemas (e.g. no `CaseType` for Harris JP/Clerk) remain strictly preserved."
        ],
        "deliverables": [
            "Duplication Audit Report detailing redundant patterns.",
            "Consolidated shared helper modules with comprehensive test coverage."
        ],
        "acceptance_criteria": [
            "Identified duplicated code blocks are replaced with a single shared function.",
            "All affected modules pass their unit tests without behavior changes.",
            "Portal output schemas remain 100% compliant with specifications."
        ],
        "error_recovery": [
            "If a shared abstraction causes regressions in one specific scraper, decouple that scraper with an override method."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/duplicate-code-detection`.",
            "cursor": "Select `@duplicate-code-detection` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `duplicate-code-detection`.",
            "codex": "Reference `duplicate-code-detection` in Codex context.",
            "gemini": "Invoke via `gemini run duplicate-code-detection`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt duplicate-code-detection`.",
            "windsurf": "Activate `duplicate-code-detection` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py`",
            "`AGENTS.md` - Section 3 (Portal Output Schema)"
        ]
    },
    {
        "name": "technical-debt-analysis",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Catalog and prioritize technical debt by business risk, remediation effort, and operational impact.",
        "purpose": "Provides a structured framework to inventory architectural shortcuts, deprecated dependencies, test skips, and workaround logic, formulating an actionable remediation roadmap.",
        "when_to_use": [
            "Periodic engineering health reviews or roadmap planning.",
            "Inheriting legacy modules or preparing for production scaling.",
            "Auditing pre-existing test skips and temporary workarounds."
        ],
        "when_not_to_use": [
            "Triaging immediate active production outages (use `diagnose-issue`)."
        ],
        "required_inputs": [
            "Codebase source files, test skip markers (`@pytest.mark.skip`), TODO comments, and issue trackers."
        ],
        "prerequisites": [
            "Completed `project-deep-analysis`."
        ],
        "procedure": [
            ("Technical Debt Discovery", "Grep codebase for `TODO`, `FIXME`, `HACK`, `WORKAROUND`, and `@pytest.mark.skip`. Identify deprecated library usage."),
            ("Categorization & Scoring", "Categorize debt: Architectural, Code Quality, Test Coverage, Security, or Documentation. Score each item on Severity (1-5) and Remediation Effort (1-5)."),
            ("Business Risk Analysis", "Evaluate operational impact: data loss risk, performance degradation, maintenance slowdown, or compliance risk."),
            ("Prioritization Matrix", "Rank debt items into Quick Wins (High Impact, Low Effort), Strategic Projects (High Impact, High Effort), and Deprioritized items."),
            ("Technical Debt Backlog Synthesis", "Author a comprehensive Technical Debt Register with actionable remediation tickets.")
        ],
        "safety": [
            "Do NOT arbitrarily remove working workarounds without understanding why they were introduced.",
            "Preserve pre-existing org-policy test skips documented in `AGENTS.md`."
        ],
        "deliverables": [
            "Prioritized Technical Debt Register with risk scores and effort estimates.",
            "Remediation Roadmap linked to specific files and lines."
        ],
        "acceptance_criteria": [
            "All TODO/FIXME markers and test skips are catalogued and evaluated.",
            "High-risk architectural bottlenecks are prioritized for remediation.",
            "Remediation tasks include explicit acceptance criteria."
        ],
        "error_recovery": [
            "If remediating a debt item introduces complex dependencies, break it down into an ADR and implementation plan."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/technical-debt-analysis`.",
            "cursor": "Select `@technical-debt-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `technical-debt-analysis`.",
            "codex": "Reference `technical-debt-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run technical-debt-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt technical-debt-analysis`.",
            "windsurf": "Activate `technical-debt-analysis` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 7 (Test Commands & Pre-existing Skips)",
            "`docs/`"
        ]
    },
    {
        "name": "performance-optimization",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Measure and optimize database query latency, API response times, scraper cycle duration, and frontend rendering.",
        "purpose": "Identifies system bottlenecks and applies targeted algorithmic, database, caching, and concurrency optimizations backed by before-and-after benchmark evidence.",
        "when_to_use": [
            "API endpoints exceeding response latency thresholds (> 500ms).",
            "Slow database queries causing lock contention or connection pool exhaustion.",
            "Scraper cycle durations exceeding client SLA requirements."
        ],
        "when_not_to_use": [
            "Premature optimization on cold paths that execute infrequently."
        ],
        "required_inputs": [
            "Profiling telemetry, slow query logs, scraper execution timestamps, and baseline metrics."
        ],
        "prerequisites": [
            "Established, reproducible performance baseline before making code changes."
        ],
        "procedure": [
            ("Baseline Profiling & Metric Capture", "Measure baseline execution duration, CPU usage, memory allocations, and query counts. Record exact baseline numbers."),
            ("Bottleneck Root Cause Analysis", "Identify primary bottleneck: N+1 ORM queries, unindexed filtering, synchronous blocking calls in async loops, or excessive React re-renders."),
            ("Targeted Optimization Application", "Apply specific optimization: eager loading (`selectinload`), database composite index, Redis caching, or React memoization."),
            ("Benchmark Re-measurement", "Rerun the exact baseline benchmark under identical conditions. Calculate percentage latency reduction and throughput gain."),
            ("Regression Verification", "Execute full unit and integration test suites to confirm zero functional regressions."),
            ("Performance Report Synthesis", "Document before-and-after metrics, optimization techniques, and verification evidence.")
        ],
        "safety": [
            "Never apply optimizations that compromise code readability or data integrity without significant measurable gain.",
            "Avoid aggressive concurrency that triggers court portal rate-limiting or IP bans."
        ],
        "deliverables": [
            "Optimized source code files.",
            "Performance Benchmark Report with before-and-after comparison charts."
        ],
        "acceptance_criteria": [
            "Measurable latency reduction (e.g. $\\ge 30\\%$) achieved on the target path.",
            "Zero functional regressions; 100% of test assertions pass.",
            "Memory overhead remains stable under sustained load."
        ],
        "error_recovery": [
            "If an optimization causes race conditions or intermittent failures, revert and profile with finer granularity."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/performance-optimization`.",
            "cursor": "Select `@performance-optimization` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `performance-optimization`.",
            "codex": "Reference `performance-optimization` in Codex context.",
            "gemini": "Invoke via `gemini run performance-optimization`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt performance-optimization`.",
            "windsurf": "Activate `performance-optimization` in Windsurf."
        },
        "references": [
            "`backend/app/services/fuzzy_engine.py` - RapidFuzz High-Performance Matching",
            "`backend/app/core/database.py`"
        ]
    },
    {
        "name": "memory-optimization",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Find and resolve memory leaks, unclosed browser contexts, unbounded caches, and task bloat in long-running services.",
        "purpose": "Diagnoses memory growth in long-running Celery workers, Playwright browser instances, and Next.js servers, preventing Out-Of-Memory (OOM) crashes.",
        "when_to_use": [
            "Celery workers exhibiting unbounded memory consumption over time.",
            "Zombie Chromium processes remaining after scraper completion.",
            "Large file exports (Excel/PDF) exhausting server RAM."
        ],
        "when_not_to_use": [
            "Short-lived CLI scripts that terminate within seconds."
        ],
        "required_inputs": [
            "Process memory logs (`check_python_procs.ps1`), worker PID monitoring, and heap profiling dumps."
        ],
        "prerequisites": [
            "Access to process monitoring tools on Windows/Linux."
        ],
        "procedure": [
            ("Process Memory Monitoring", "Track memory growth over multiple task iterations using `scripts/check_python_procs.ps1` or `tracemalloc`."),
            ("Leak Source Isolation", "Identify leak vectors: unclosed Playwright browser contexts, lingering event listeners, uncollected SQLAlchemy session caches, or unbounded global dicts."),
            ("Resource Lifecycle Cleanup", "Enforce deterministic cleanup using context managers (`with` / `async with`), explicit `browser.close()`, and `gc.collect()`."),
            ("Streaming & Chunking Implementation", "Replace in-memory buffering with chunked streaming (e.g. streaming large CSV/Excel exports directly to disk)."),
            ("Worker Recycling Configuration", "Configure Celery `max_tasks_per_child` to periodically recycle worker processes safely."),
            ("Sustained Load Verification", "Run 100-iteration stress test and verify memory stabilizes within expected bounds.")
        ],
        "safety": [
            "Ensure browser termination logic does not kill other active attended sessions running for different tasks.",
            "Never disable garbage collection globally."
        ],
        "deliverables": [
            "Memory-optimized service and worker code.",
            "Memory Stability Report with process RAM curves before and after fix."
        ],
        "acceptance_criteria": [
            "Zero zombie Chrome or Python processes remain following task completion.",
            "Worker memory footprint stabilizes under sustained task execution.",
            "File exports stream without loading full datasets into RAM."
        ],
        "error_recovery": [
            "If Playwright crashes during context teardown, wrap in try/finally blocks with fallback process cleanup."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/memory-optimization`.",
            "cursor": "Select `@memory-optimization` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `memory-optimization`.",
            "codex": "Reference `memory-optimization` in Codex context.",
            "gemini": "Invoke via `gemini run memory-optimization`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt memory-optimization`.",
            "windsurf": "Activate `memory-optimization` in Windsurf."
        },
        "references": [
            "`backend/app/automation/browser_manager.py`",
            "`scripts/clean_stale_workers.py`"
        ]
    },
    {
        "name": "error-handling",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Implement consistent error hierarchies, typed exceptions, graceful degradation, and user-facing error banners.",
        "purpose": "Standardizes exception handling across the platform, preventing unhandled crashes, establishing clean error classification, and presenting actionable feedback to operators.",
        "when_to_use": [
            "Authoring new service modules, scrapers, or API endpoints.",
            "Refactoring generic `except Exception:` blocks into typed exception handling.",
            "Standardizing frontend error banners and toast notifications."
        ],
        "when_not_to_use": [
            "Suppressing legitimate programming errors or syntax bugs."
        ],
        "required_inputs": [
            "Target error scenarios, exception hierarchy definitions, and error schemas."
        ],
        "prerequisites": [
            "Understanding of FastAPI exception handlers and React Error Boundaries."
        ],
        "procedure": [
            ("Domain Exception Hierarchy Definition", "Define typed exceptions in `app/core/exceptions.py` (e.g., `CaptchaResolutionError`, `PortalNavigationError`, `GuidewireDeliveryError`)."),
            ("Specific Exception Handling", "Replace catch-all `except Exception:` blocks with specific exception traps. Preserve stack traces with `raise ... from exc`."),
            ("FastAPI Exception Handlers", "Register global exception handlers mapping domain exceptions to structured JSON responses (`status`, `error_code`, `message`, `details`)."),
            ("Frontend Error Boundary & Toast Binding", "Wrap React component trees in Error Boundaries. Display user-friendly error banners mapping API error codes."),
            ("Audit Logging & Screenshot Capture", "Capture automated error screenshots (`ErrorScreenshot`) and audit log entries for all runtime scraper exceptions."),
            ("Error Scenario Testing", "Write unit tests deliberately injecting failures and verifying structured error responses.")
        ],
        "safety": [
            "NEVER silently swallow exceptions with bare `pass` blocks.",
            "Never expose internal database connection strings or stack traces to end-users in production."
        ],
        "deliverables": [
            "Domain exception hierarchy and structured exception handlers.",
            "Automated test suite verifying error capture and response mapping."
        ],
        "acceptance_criteria": [
            "Zero unhandled 500 errors returned for known failure modes.",
            "Scraper failures capture diagnostic error screenshots to `backend/screenshots/`.",
            "Frontend displays clear, actionable error banners without crashing the UI."
        ],
        "error_recovery": [
            "If an unknown exception occurs, log the complete traceback to audit logs and present a safe fallback UI."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/error-handling`.",
            "cursor": "Select `@error-handling` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `error-handling`.",
            "codex": "Reference `error-handling` in Codex context.",
            "gemini": "Invoke via `gemini run error-handling`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt error-handling`.",
            "windsurf": "Activate `error-handling` in Windsurf."
        },
        "references": [
            "`backend/app/automation/base.py` - `CaptchaResolutionError`",
            "`backend/app/models/error_screenshot.py`"
        ]
    },
    {
        "name": "logging-observability",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Implement structured JSON logging, correlation IDs, execution telemetry, and health check diagnostics.",
        "purpose": "Ensures the application emits rich, structured operational logs, metrics, and trace IDs enabling rapid root-cause diagnosis across distributed API and Celery workers.",
        "when_to_use": [
            "Adding telemetry to asynchronous queue tasks, scrapers, or third-party integrations.",
            "Standardizing log output formats across backend and worker containers."
        ],
        "when_not_to_use": [
            "Adding temporary local `print()` statements for one-off debugging."
        ],
        "required_inputs": [
            "Logging configuration (`logging.config`), log level guidelines, and metric requirements."
        ],
        "prerequisites": [
            "Python `logging` or `structlog` setup."
        ],
        "procedure": [
            ("Structured Logger Configuration", "Configure Python logging with structured JSON formatting, UTC ISO timestamps, and log level thresholds."),
            ("Correlation & Trace ID Injection", "Generate unique correlation IDs (`X-Correlation-ID`) in FastAPI middleware; propagate IDs across Celery task headers."),
            ("Contextual Log Binding", "Bind contextual metadata (`claim_id`, `portal`, `party_name`, `elapsed_ms`) to logger calls."),
            ("Audit Trail Integration", "Persist significant operational milestones to `AuditLog` database table for permanent tracking."),
            ("Secret Masking Filter", "Apply logging filter automatically redacting passwords, API keys, and customer SSN/PII."),
            ("Verification Pass", "Inspect log output during a simulated claim workflow to verify correlation ID propagation and secret redaction.")
        ],
        "safety": [
            "CRITICAL: Never emit plain-text passwords, tokens, or credentials in log output.",
            "Avoid excessive debug logging in production that exhausts disk space."
        ],
        "deliverables": [
            "Structured logging configuration and correlation middleware.",
            "Verified audit log records and secret masking filters."
        ],
        "acceptance_criteria": [
            "All logs emit valid JSON with correlation ID and timestamp.",
            "All secrets and tokens are masked with `***`.",
            "Scraper execution timing is captured with millisecond accuracy."
        ],
        "error_recovery": [
            "If logging handlers throw disk-full or IO errors, fail safely to console stderr."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/logging-observability`.",
            "cursor": "Select `@logging-observability` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `logging-observability`.",
            "codex": "Reference `logging-observability` in Codex context.",
            "gemini": "Invoke via `gemini run logging-observability`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt logging-observability`.",
            "windsurf": "Activate `logging-observability` in Windsurf."
        },
        "references": [
            "`backend/app/api/v1/endpoints/audit.py`",
            "`backend/app/models/audit_log.py`"
        ]
    },
    {
        "name": "security-audit",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Review application security risks, OWASP Top 10 vulnerabilities, credential leakage, and authorization boundaries.",
        "purpose": "Conducts systematic security evaluations across source code, dependencies, database queries, and network configurations to eliminate vulnerabilities and enforce defensive coding.",
        "when_to_use": [
            "Prior to production releases or major architectural milestones.",
            "Adding authentication, user input parsing, or file upload endpoints.",
            "Auditing credential storage and environment variable handling."
        ],
        "when_not_to_use": [
            "Non-security documentation edits."
        ],
        "required_inputs": [
            "Full codebase access, configuration files, and API endpoint definitions."
        ],
        "prerequisites": [
            "Knowledge of OWASP Top 10 vulnerabilities (Injection, Broken Auth, SSRF, XSS)."
        ],
        "procedure": [
            ("Credential Leakage & Secret Audit", "Scan repository for unmasked secrets, hardcoded API keys, private keys, or credentials using pattern detection."),
            ("Injection & SQL Safety Review", "Audit database queries. Confirm 100% usage of parameterized ORM queries (`select(Model).where(...)`); verify zero raw string interpolation."),
            ("Input Validation & File Upload Security", "Inspect file upload endpoints (`/api/v1/ingest/upload`). Verify file type validation, size limits, and safe storage paths."),
            ("CORS & Security Headers Audit", "Check FastAPI CORS middleware settings (`allow_origins`), Content-Security-Policy, and cookie security attributes."),
            ("Authorization & RBAC Enforcement", "Verify that all mutating endpoints (`POST`, `PUT`, `DELETE`) require authorization."),
            ("Security Audit Report Synthesis", "Publish a comprehensive Security Audit Report categorizing findings by CVSS severity with remediation steps.")
        ],
        "safety": [
            "CRITICAL: Never commit detected secrets or private keys to version control during auditing.",
            "Immediately rotate any credential discovered in plain-text."
        ],
        "deliverables": [
            "Comprehensive Security Audit Report.",
            "Prioritized Remediation Backlog for identified security gaps."
        ],
        "acceptance_criteria": [
            "Zero plain-text credentials or API keys found in codebase.",
            "100% of database queries use parameterized ORM statements.",
            "File upload handlers enforce strict extension and size boundaries."
        ],
        "error_recovery": [
            "If an active secret is found in git history, initiate git secret purge and rotate the key immediately."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/security-audit`.",
            "cursor": "Select `@security-audit` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `security-audit`.",
            "codex": "Reference `security-audit` in Codex context.",
            "gemini": "Invoke via `gemini run security-audit`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt security-audit`.",
            "windsurf": "Activate `security-audit` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Not Do)",
            "`backend/app/core/config.py`"
        ]
    },
    {
        "name": "accessibility-audit",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Evaluate frontend accessibility against WCAG 2.1 AA standards, color contrast, focus rings, and screen-reader semantics.",
        "purpose": "Audits rendered HTML, CSS stylesheets, and interactive React components against international accessibility standards to guarantee usability for all operators.",
        "when_to_use": [
            "Pre-release quality gates for user interfaces.",
            "Following significant redesigns of pages, stat cards, or form controls."
        ],
        "when_not_to_use": [
            "Backend server code or database testing."
        ],
        "required_inputs": [
            "Frontend application running locally on port 3000.",
            "Playwright browser automation or axe-core testing scripts."
        ],
        "prerequisites": [
            "Next.js frontend running and reachable."
        ],
        "procedure": [
            ("Automated Axe-Core Scan", "Run automated accessibility scan across all primary routes (`/`, `/health`, `/monitor`, `/settings`, `/branding`). Log all violations."),
            ("Color Contrast Ratio Calculation", "Measure contrast of all text elements against backgrounds in both Light Mode and Dark Mode. Confirm $\\ge 4.5:1$ ratio."),
            ("Keyboard Navigation Walkthrough", "Traverse entire application using keyboard alone (`Tab`, `Shift+Tab`, `Enter`, `Escape`). Verify visible focus rings and zero focus traps."),
            ("Screen Reader Semantic Verification", "Verify ARIA roles, form labels, and live region announcements for dynamic updates."),
            ("Remediation Roadmap", "Document specific CSS and JSX fixes for all identified contrast or markup issues.")
        ],
        "safety": [
            "Never compromise accessible contrast to satisfy purely subjective aesthetic preferences.",
            "Ensure both Light Mode and Dark Mode are audited equally."
        ],
        "deliverables": [
            "WCAG 2.1 AA Accessibility Audit Report.",
            "Annotated violation list with file locations and recommended JSX fixes."
        ],
        "acceptance_criteria": [
            "Zero Critical or Serious violations reported by automated accessibility audits.",
            "100% of text elements satisfy 4.5:1 contrast in both Light and Dark themes.",
            "All interactive elements support full keyboard navigation."
        ],
        "error_recovery": [
            "If automated axe-core scans fail on dynamic modals, test modal rendering in isolated test fixtures."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/accessibility-audit`.",
            "cursor": "Select `@accessibility-audit` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `accessibility-audit`.",
            "codex": "Reference `accessibility-audit` in Codex context.",
            "gemini": "Invoke via `gemini run accessibility-audit`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt accessibility-audit`.",
            "windsurf": "Activate `accessibility-audit` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md` - Section 2",
            "`frontend/src/app/branding/page.tsx`"
        ]
    },
    {
        "name": "dead-code-removal",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Prove code is completely unreferenced before safely removing it from the repository.",
        "purpose": "Enforces a strict, evidence-based verification protocol before deleting deprecated functions, unused variables, orphan components, or obsolete scripts.",
        "when_to_use": [
            "Retiring deprecated API endpoints or legacy utility scripts.",
            "Cleaning up unused components after refactoring."
        ],
        "when_not_to_use": [
            "Speculative code deletions without exhaustive reference checking."
        ],
        "required_inputs": [
            "Candidate symbol or file path proposed for removal.",
            "Full repository search tools."
        ],
        "prerequisites": [
            "Clean git working tree."
        ],
        "procedure": [
            ("Static Reference Search", "Search all source files, tests, configuration, scripts, and documentation for references to the candidate symbol."),
            ("Dynamic & Reflection Check", "Verify symbol is not referenced dynamically (e.g. `getattr()`, Celery task name strings, dynamic router imports)."),
            ("Test Suite Validation Pass", "Run full test suite (`pytest`, `tsc`) before deletion to establish green baseline."),
            ("Removal Execution", "Remove the unreferenced code cleanly."),
            ("Post-Removal Verification", "Rerun full test suite to prove zero broken imports or side effects."),
            ("Documentation Update", "Remove references from documentation and changelog.")
        ],
        "safety": [
            "CRITICAL: Never delete code merely because it looks unused; prove zero references with concrete evidence.",
            "Never remove protected directories (`anticaptcha-plugin_v0.83`, `.agents`)."
        ],
        "deliverables": [
            "Deleted code commit with reference verification evidence.",
            "Verification test report confirming zero regressions."
        ],
        "acceptance_criteria": [
            "Zero references to the deleted symbol exist anywhere in the repository.",
            "All unit and integration tests pass without failures.",
            "Documentation updated to reflect removal."
        ],
        "error_recovery": [
            "If post-removal tests fail, immediately revert the deletion and investigate the hidden dependency."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/dead-code-removal`.",
            "cursor": "Select `@dead-code-removal` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `dead-code-removal`.",
            "codex": "Reference `dead-code-removal` in Codex context.",
            "gemini": "Invoke via `gemini run dead-code-removal`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt dead-code-removal`.",
            "windsurf": "Activate `dead-code-removal` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Preserve Existing Functionality)"
        ]
    },
    {
        "name": "dependency-cleanup",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Remove or replace unused, deprecated, or vulnerable dependencies safely across Python and Node ecosystems.",
        "purpose": "Audits and purges unused third-party packages from `requirements.txt` and `package.json`, reducing bundle sizes, installation times, and attack surfaces.",
        "when_to_use": [
            "Following refactoring where external libraries were replaced with native code.",
            "Resolving security advisories for unmaintained dependencies."
        ],
        "when_not_to_use": [
            "Removing dependencies without verifying transitive usage."
        ],
        "required_inputs": [
            "Dependency candidate list, `requirements.txt`, `package.json`."
        ],
        "prerequisites": [
            "Working virtual environment and clean package lockfiles."
        ],
        "procedure": [
            ("Import Scanning", "Scan all Python files for `import <pkg>` and frontend files for `from '<pkg>'`. Confirm zero active imports."),
            ("Package Descriptors Update", "Remove package entry from `backend/requirements.txt` or run `npm uninstall <pkg>` in `frontend/`."),
            ("Lockfile Regeneration", "Regenerate lockfiles cleanly without extraneous modifications."),
            ("Clean Environment Build & Test Pass", "Run fresh test execution to verify no transitive runtime crashes occur."),
            ("Cleanup Summary", "Document removed packages and package size savings.")
        ],
        "safety": [
            "Never remove core runtime packages (FastAPI, Celery, SQLAlchemy, Playwright, RapidFuzz, Next.js).",
            "Verify dependencies are not loaded dynamically or utilized exclusively in test fixtures."
        ],
        "deliverables": [
            "Updated `requirements.txt` and `package.json`.",
            "Verification test report confirming full platform stability."
        ],
        "acceptance_criteria": [
            "Removed packages have zero active imports in the repository.",
            "`pytest` and `npm run build` pass cleanly after removal.",
            "Lockfiles are consistent and free of corruption."
        ],
        "error_recovery": [
            "If uninstallation causes missing module errors during runtime, restore the dependency and check dynamic usage."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/dependency-cleanup`.",
            "cursor": "Select `@dependency-cleanup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `dependency-cleanup`.",
            "codex": "Reference `dependency-cleanup` in Codex context.",
            "gemini": "Invoke via `gemini run dependency-cleanup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt dependency-cleanup`.",
            "windsurf": "Activate `dependency-cleanup` in Windsurf."
        },
        "references": [
            "`backend/requirements.txt`",
            "`frontend/package.json`"
        ]
    },
    {
        "name": "code-documentation",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Document non-obvious algorithms, scraper heuristics, fuzzy cascade logic, and API interface contracts.",
        "purpose": "Authors clear, concise, and accurate docstrings, module documentation, and inline comments explaining the *why* behind complex business logic and architectural choices.",
        "when_to_use": [
            "Writing complex business logic (e.g. RapidFuzz cascade, DOL date conversion).",
            "Implementing complex Playwright DOM interaction workarounds.",
            "Authoring public service interfaces and utility libraries."
        ],
        "when_not_to_use": [
            "Writing redundant comments that merely restate self-explanatory code (e.g., `i += 1  # increment i`)."
        ],
        "required_inputs": [
            "Source code files needing documentation.",
            "Business rule context from `AGENTS.md`."
        ],
        "prerequisites": [
            "Complete understanding of the underlying business constraints."
        ],
        "procedure": [
            ("Module & Function Docstrings", "Add Google-style docstrings to Python functions/classes detailing Args, Returns, Raises, and business rationale."),
            ("Complex Heuristic Documentation", "Document non-obvious heuristics (e.g. why Date of Loss uses 1899-12-30 base, why 9-digit ClaimNumber gets '0' prefix)."),
            ("TypeScript Interface Comments", "Add JSDoc comments to TypeScript interfaces and API client methods in `frontend/src/`."),
            ("Preserve Documentation Integrity", "Preserve all pre-existing comments and docstrings unrelated to current edits."),
            ("Linter Verification", "Run `ruff check` to ensure docstrings adhere to formatting standards.")
        ],
        "safety": [
            "Never write misleading, stale, or contradictory documentation.",
            "Preserve existing comments and license headers."
        ],
        "deliverables": [
            "Fully documented source code with standardized docstrings and JSDoc blocks."
        ],
        "acceptance_criteria": [
            "All public classes and functions have meaningful docstrings.",
            "Complex business invariants are thoroughly explained with references to `AGENTS.md`.",
            "Zero docstring formatting errors reported by linter."
        ],
        "error_recovery": [
            "If docstrings desynchronize from code during refactoring, update docstrings immediately as part of the change."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/code-documentation`.",
            "cursor": "Select `@code-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `code-documentation`.",
            "codex": "Reference `code-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run code-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt code-documentation`.",
            "windsurf": "Activate `code-documentation` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Critical Business Rules)",
            "`backend/app/services/fuzzy_engine.py`"
        ]
    },
    {
        "name": "coding-standards",
        "category_code": "D",
        "category_name": "Code Quality & Maintenance",
        "description": "Enforce repository-specific formatting, naming, linting, and quality conventions across all source code.",
        "purpose": "Maintains strict code hygiene and stylistic consistency across Python, TypeScript, and PowerShell files, enforcing automated linting and formatting gates.",
        "when_to_use": [
            "Pre-commit quality verification on any modified or newly created files.",
            "Resolving linting failures or formatting discrepancies."
        ],
        "when_not_to_use": [
            "Running destructive formatting across unchanged legacy files."
        ],
        "required_inputs": [
            "Modified source files, `ruff.toml`, `cspell.json`, and TypeScript configuration."
        ],
        "prerequisites": [
            "Configured linters in local virtual environment."
        ],
        "procedure": [
            ("Python Linting & Formatting Check", "Run `ruff check app tests` in `backend/`. Verify zero syntax or style errors."),
            ("TypeScript Type Check", "Run `npx tsc --noEmit` in `frontend/`. Verify zero type errors."),
            ("PowerShell Syntax Check", "Run `powershell -File scripts/check_ps1_syntax.ps1`. Verify zero syntax errors."),
            ("Spelling & Dictionary Check", "Verify new symbols and variables against `cspell.json` dictionary."),
            ("Automated Fix Application", "Apply safe automated formatting fixes (`ruff check --fix`) where appropriate."),
            ("Final Clean Baseline Verification", "Confirm all linters report 0 errors.")
        ],
        "safety": [
            "Never bypass or disable linter rules merely to silence warnings.",
            "Avoid massive whitespace reformatting on untouched legacy files."
        ],
        "deliverables": [
            "100% compliant source code matching repository standards.",
            "Zero linter and type-checker error baseline."
        ],
        "acceptance_criteria": [
            "Python `ruff check` passes with 0 errors.",
            "Frontend `tsc --noEmit` passes with 0 errors.",
            "PowerShell syntax check passes with 0 errors."
        ],
        "error_recovery": [
            "If a linter rule conflicts with project conventions, adjust `ruff.toml` with documented justification."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/coding-standards`.",
            "cursor": "Select `@coding-standards` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `coding-standards`.",
            "codex": "Reference `coding-standards` in Codex context.",
            "gemini": "Invoke via `gemini run coding-standards`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt coding-standards`.",
            "windsurf": "Activate `coding-standards` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 7 (Test Commands)",
            "`ruff.toml`"
        ]
    }
]

