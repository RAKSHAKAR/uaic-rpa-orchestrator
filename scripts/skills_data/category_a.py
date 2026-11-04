"""
Category A: Project Discovery & Requirements
Contains 12 comprehensive skills for discovering, assessing, and analyzing
project context, architecture, requirements, and gaps.
"""

SKILLS_A = [
    {
        "name": "project-discovery",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Understand the product purpose, users, repository structure, tech stack, and current baseline state before planning or writing code.",
        "purpose": "Provides a systematic, non-invasive protocol to inspect an unknown or existing repository, understand its core business value, identify primary actors and users, catalogue root directories, detect technologies, and establish an operational baseline.",
        "when_to_use": [
            "Initial onboarding onto a new codebase or unfamiliar repository.",
            "Starting a major new initiative or architectural review.",
            "Re-aligning project assumptions after major team or dependency updates."
        ],
        "when_not_to_use": [
            "Trivial single-line hotfixes where the codebase context is already thoroughly verified.",
            "Mid-flight execution of an already approved and ongoing implementation plan."
        ],
        "required_inputs": [
            "Access to workspace root directory.",
            "Read access to repository configuration files (`package.json`, `pyproject.toml`, `requirements.txt`, `docker-compose.yml`, `README.md`)."
        ],
        "prerequisites": [
            "Terminal read-only execution capabilities (directory listing, file reading).",
            "Zero destructive command authorization (strictly passive discovery)."
        ],
        "procedure": [
            ("Root Directory & Configuration Survey", "Enumerate root-level files and directories. Inspect package descriptors (`package.json`, `requirements.txt`, `.env.example`, `docker-compose.yml`) to identify language runtimes, package managers, and core frameworks."),
            ("README & Documentation Review", "Read the primary `README.md`, architecture manuals, and historical project docs. Extract stated project identity, business objectives, and supported environments."),
            ("Service & Entrypoint Mapping", "Identify frontend entrypoints (e.g., Next.js `src/app/page.tsx`), backend entrypoints (e.g., FastAPI `app/main.py`), and background worker queues (e.g., Celery tasks)."),
            ("Data Store & External Service Identification", "Detect database engines (PostgreSQL, SQLite), caches/brokers (Redis), third-party APIs (Guidewire, SMTP), and integration endpoints."),
            ("Synthesis & Baseline Documentation", "Synthesize findings into a structured discovery brief summarizing the project purpose, architecture, primary workflows, and operational state.")
        ],
        "safety": [
            "Do NOT modify or delete any files during discovery.",
            "Do NOT run active mutation scripts or connect to external production services.",
            "Never expose unmasked credentials or tokens found in `.env` files."
        ],
        "deliverables": [
            "Structured Project Discovery Brief in `docs/` or session artifact.",
            "High-level directory and service topology map."
        ],
        "acceptance_criteria": [
            "Product identity, primary users, and core workflows are explicitly documented.",
            "Languages, frameworks, package managers, and runtimes are verified with exact versions.",
            "Database, queue, and external service touchpoints are identified.",
            "Zero project files modified during execution."
        ],
        "error_recovery": [
            "If package files are missing or malformed, search for lock files (`package-lock.json`, `poetry.lock`) or environment files.",
            "If project documentation is missing or outdated, rely directly on source code inspection and test files."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/project-discovery` or ask the agent to run project discovery.",
            "cursor": "Select `@project-discovery` rule in Cursor chat.",
            "claude_code": "Reference `project-discovery` skill in Claude Code prompt.",
            "codex": "Reference `project-discovery` workflow in Codex prompt.",
            "gemini": "Invoke via `gemini run project-discovery` or GEMINI.md guideline.",
            "github_copilot": "Invoke via Copilot Chat `/prompt project-discovery`.",
            "windsurf": "Activate `project-discovery` workflow rule in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 1 (Project Identity) & Section 2 (Repository Layout)",
            "`README.md` - Master Architectural Booklet"
        ]
    },
    {
        "name": "project-deep-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Inspect the repository architecture, code entry points, database models, internal interfaces, test suites, and runtime behaviors in depth.",
        "purpose": "Performs exhaustive technical code-level analysis across frontend, backend, database layers, background queues, and test infrastructure to build an authoritative mental model of code paths and system state.",
        "when_to_use": [
            "Prior to authoring complex, multi-service implementation plans.",
            "Diagnosing deep architectural regressions or elusive lifecycle bugs.",
            "Evaluating migration paths for frameworks, databases, or runtime environments."
        ],
        "when_not_to_use": [
            "High-level initial project discovery (use `project-discovery` instead).",
            "Isolated UI styling tweaks that do not touch state or backend services."
        ],
        "required_inputs": [
            "Full read access to source trees (`backend/app`, `frontend/src`, `e2e`, `tests`).",
            "Git log history to trace recent architectural changes."
        ],
        "prerequisites": [
            "Completed `project-discovery` phase.",
            "Local environment tooling available for passive type-checking and test suite introspection."
        ],
        "procedure": [
            ("Backend Architecture & Data Flow Inspection", "Trace request flow from FastAPI routers (`app/api/v1/router.py`) through service layers (`app/services/`) to database models (`app/models/`). Inspect transaction lifecycles and session management."),
            ("Frontend State & Component Hierarchy Inspection", "Analyze Next.js App Router layout (`layout.tsx`), client state providers (`BrandingContext`, React Query), API clients (`lib/api.ts`), and TypeScript contracts (`types/index.ts`)."),
            ("Asynchronous Task & Worker Pipeline Inspection", "Inspect Celery tasks (`app/tasks/`), queue routing configurations, broker bindings, retry mechanisms, and concurrency semaphores."),
            ("Test Coverage & Harness Audit", "Analyze test suites in `tests/` and `e2e/`. Identify mocked vs. live integration tests, coverage gaps, and pre-existing skips."),
            ("Synthesis & Technical Deep Analysis Report", "Produce an authoritative technical deep-analysis document highlighting architectural strengths, bottlenecks, and structural constraints.")
        ],
        "safety": [
            "Strictly read-only; no code modifications permitted.",
            "Avoid running tests that perform live network calls or database truncations during deep analysis."
        ],
        "deliverables": [
            "Deep Technical Architecture & Component Analysis Document.",
            "Detailed dataflow diagram and transaction boundary map."
        ],
        "acceptance_criteria": [
            "Every primary API router, service layer, and database model is documented with line references.",
            "Async queue bindings and task lifecycles are mapped end-to-end.",
            "Current test coverage and harness limitations are explicitly quantified."
        ],
        "error_recovery": [
            "If circular imports or obfuscated logic are detected, trace execution starting from test files or FastAPI entrypoint.",
            "If dynamic imports obscure routing, check router inclusion statements in `app/api/v1/router.py`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/project-deep-analysis`.",
            "cursor": "Select `@project-deep-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `project-deep-analysis` guidelines.",
            "codex": "Reference `project-deep-analysis` in OpenAI Codex.",
            "gemini": "Invoke via `gemini run project-deep-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt project-deep-analysis`.",
            "windsurf": "Activate `project-deep-analysis` rule in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 2 (Repository Layout) & Section 5 (API Endpoints Summary)",
            "`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`"
        ]
    },
    {
        "name": "requirement-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Convert raw client inputs, feature requests, and legacy specifications into clear, unambiguous functional and non-functional requirements.",
        "purpose": "Bridges the gap between ambiguous user requests or legacy specifications (such as RPA Robin scripts) and rigorous, actionable engineering requirements with objective acceptance criteria.",
        "when_to_use": [
            "Receiving a new client feature brief or problem statement.",
            "Porting legacy desktop flows (e.g. Power Automate Desktop V4) to modern services.",
            "Refactoring complex business logic where business rules must be preserved."
        ],
        "when_not_to_use": [
            "Fixing straightforward runtime syntax errors or lint warnings.",
            "Executing pre-approved, well-specified tasks from an existing WBS."
        ],
        "required_inputs": [
            "Client request text, ticket descriptions, or reference workflow scripts.",
            "Existing business rules documentation (`AGENTS.md`, `docs/`)."
        ],
        "prerequisites": [
            "Understanding of existing domain terms and business models."
        ],
        "procedure": [
            ("Source Material Ingestion", "Read and parse the raw requirements document, prompt, or legacy automation flow. Extract business objectives, explicit constraints, and user personas."),
            ("Functional Decomposition", "Break down stated requirements into discrete functional capabilities (inputs, state transformations, outputs, persistence, and external events)."),
            ("Non-Functional Requirement Specification", "Define performance latency targets, concurrency thresholds, availability constraints, accessibility standards (WCAG 2.1 AA), and data retention rules."),
            ("Edge Case & Boundary Identification", "Identify boundary conditions, exception states, missing fields, timeout behaviors, and human-in-the-loop fallback scenarios."),
            ("Requirements Traceability Matrix (RTM) Formulation", "Map every functional requirement to an ID (REQ-XXX), source reference, and preliminary acceptance test scenario.")
        ],
        "safety": [
            "Do NOT invent or assume business rules when specifications are ambiguous; flag them for `grill-me` clarification.",
            "Do NOT discard legacy safety constraints (e.g. CAPTCHA verification delays or state routing logic)."
        ],
        "deliverables": [
            "Structured Functional & Non-Functional Requirements Specification (FRS).",
            "Requirements Traceability Matrix (RTM)."
        ],
        "acceptance_criteria": [
            "All functional requirements have unique identifiers and unambiguous descriptions.",
            "Non-functional constraints specify measurable thresholds (latency, throughput, availability).",
            "Edge cases and error states are documented with explicit fallback behavior."
        ],
        "error_recovery": [
            "If user requirements conflict with core architectural rules, raise an explicit warning and invoke `grill-me`.",
            "If legacy flow code is incomplete, cross-reference annotated flow documentation (`docs/v4_all_8_subflows_annotated.txt`)."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/requirement-analysis`.",
            "cursor": "Select `@requirement-analysis` rule in Cursor chat.",
            "claude_code": "Prompt Claude Code with `requirement-analysis` workflow.",
            "codex": "Reference `requirement-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run requirement-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt requirement-analysis`.",
            "windsurf": "Activate `requirement-analysis` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Critical Business Rules)",
            "`docs/STAGE_AND_STATUS_DEFINITIONS.md`"
        ]
    },
    {
        "name": "requirement-gap-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Find missing, conflicting, ambiguous, duplicated, or unimplemented requirements between specifications and current codebase reality.",
        "purpose": "Compares expected requirements against actual codebase implementation to detect unfulfilled promises, behavioral divergences, dead specifications, or unhandled edge cases before release.",
        "when_to_use": [
            "Auditing a feature implementation prior to client acceptance testing.",
            "Comparing modern web orchestration against legacy RPA V4 behavior.",
            "Evaluating test suite coverage against business requirements."
        ],
        "when_not_to_use": [
            "Greenfield exploration where no code or specification exists yet."
        ],
        "required_inputs": [
            "Approved Requirements Specification or master booklet (`README.md`).",
            "Current codebase and test suite results."
        ],
        "prerequisites": [
            "Completed `requirement-analysis` and `project-deep-analysis`."
        ],
        "procedure": [
            ("Baseline Specification Mapping", "Extract all verified requirements from specification documents and project guidelines into an audit checklist."),
            ("Codebase & Test Verification Audit", "Verify whether each requirement is implemented in source code and backed by automated tests. Check API routes, UI controls, and worker tasks."),
            ("Divergence & Conflict Classification", "Classify each discrepancy: Missing (not implemented), Incomplete (partially implemented), Conflicting (deviates from spec), or Outdated (spec obsolete)."),
            ("Impact & Risk Assessment", "Assess operational and business risk for each identified gap (e.g. data loss risk, compliance breach, UI failure)."),
            ("Remediation Plan Formulation", "Draft actionable remediation recommendations prioritized by severity (Critical, High, Medium, Low).")
        ],
        "safety": [
            "Never assume code matches documentation without checking actual source and tests.",
            "Do not silently delete unfulfilled requirements from documentation."
        ],
        "deliverables": [
            "Requirement Gap Analysis Report with categorized findings.",
            "Actionable Remediation Backlog linked to specific file locations."
        ],
        "acceptance_criteria": [
            "100% of specified requirements are audited against actual code implementation.",
            "Every gap has an assigned severity, evidence reference, and remediation recommendation.",
            "Gaps affecting data integrity or external APIs (Guidewire) are prioritized as Critical."
        ],
        "error_recovery": [
            "If test evidence is inconclusive, write an isolated verification script in `scripts/` to probe live behavior.",
            "If documentation and code contradict each other, consult `AGENTS.md` and git commit history to determine authoritative intent."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/requirement-gap-analysis`.",
            "cursor": "Select `@requirement-gap-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `requirement-gap-analysis`.",
            "codex": "Reference `requirement-gap-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run requirement-gap-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt requirement-gap-analysis`.",
            "windsurf": "Activate `requirement-gap-analysis` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Definition of Done & AI Agent Rules)",
            "`README.md` - Section on Power Automate V4 Behavioral Parity"
        ]
    },
    {
        "name": "grill-me",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Conduct a structured, interactive interview with the user to resolve critical ambiguities and design trade-offs before making irreversible assumptions.",
        "purpose": "Engages the user in targeted, high-signal inquiry to clarify material uncertainties, architectural trade-offs, security boundaries, and edge-case handling before authoring an implementation plan.",
        "when_to_use": [
            "User request contains underspecified requirements with multiple viable architectures.",
            "Encountering conflicting business rules between different specifications.",
            "Consequential design decisions involving database migrations, external integrations, or breaking API changes."
        ],
        "when_not_to_use": [
            "Trivial questions with self-evident answers already documented in `AGENTS.md` or `README.md`.",
            "During automated test execution or non-interactive background tasks."
        ],
        "required_inputs": [
            "List of specific, well-articulated ambiguities or design options.",
            "Context on trade-offs (pros, cons, risks, effort) for each option."
        ],
        "prerequisites": [
            "Thorough review of existing documentation to ensure the answer is not already documented."
        ],
        "procedure": [
            ("Ambiguity Clustering", "Group open questions into logical themes: Architecture, Data Model, User Experience, External Integrations, and Security/Safety."),
            ("Option Formulation with Recommendations", "For each question, formulate clear options, highlight the recommended approach prefixed with '(Recommended)', and explain trade-offs."),
            ("Interactive Interview Presentation", "Present questions concisely using the `ask_question` tool or structured interactive prompts. Avoid overwhelming the user with more than 3-4 questions at once."),
            ("User Decision Ingestion & Confirmation", "Record user choices, confirm consensus, and extract explicit constraints."),
            ("Decision Archival", "Archive finalized decisions into the session context and cross-reference them in the upcoming Implementation Plan.")
        ],
        "safety": [
            "Do NOT ask open-ended or trivial questions that can be answered by reading the codebase.",
            "Do NOT proceed with speculative assumptions if the user has not confirmed critical architectural directions."
        ],
        "deliverables": [
            "Interview Findings & Decision Log summarizing confirmed requirements.",
            "Updated assumptions list ready for inclusion in the Implementation Plan."
        ],
        "acceptance_criteria": [
            "All material ambiguities identified during discovery are resolved by explicit user decisions.",
            "Every question presented included an explicit recommendation and trade-off summary.",
            "Confirmed decisions are recorded in project documentation or session artifacts."
        ],
        "error_recovery": [
            "If the user is unsure of a technical decision, provide a sensible default based on existing project conventions (`AGENTS.md`).",
            "If user choices contradict existing safety rules, explain the constraint and seek consensus."
        ],
        "tool_invocations": {
            "antigravity": "Invoke native slash command `/grill-me` or ask the agent to interview you on requirements.",
            "cursor": "Select `@grill-me` rule in Cursor chat.",
            "claude_code": "Prompt Claude Code: 'Interview me using the grill-me protocol before designing.'",
            "codex": "Reference `grill-me` workflow in Codex prompt.",
            "gemini": "Invoke via `gemini run grill-me`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt grill-me`.",
            "windsurf": "Activate `grill-me` workflow in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)",
            "`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`"
        ]
    },
    {
        "name": "business-process-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Map actors, business rules, lifecycle process states, handoffs, exception conditions, and outcomes into structured workflows.",
        "purpose": "Formalizes complex domain workflows (such as insurance claims processing, legal court discovery, deduplication cascades, and carrier integrations) into comprehensive state diagrams and transition matrices.",
        "when_to_use": [
            "Designing or refactoring core business lifecycle engines (e.g. claim ingestion, batch queue processing).",
            "Aligning frontend UI state displays with backend database state machines.",
            "Auditing legal or insurance compliance handoffs."
        ],
        "when_not_to_use": [
            "Low-level infrastructure configuration (Docker, CI/CD, linting).",
            "Generic utility functions that do not affect business lifecycle states."
        ],
        "required_inputs": [
            "Domain specifications, state enumeration files (`app/models/claim.py`), and operational guides (`docs/STAGE_AND_STATUS_DEFINITIONS.md`)."
        ],
        "prerequisites": [
            "Domain understanding of business entities and their terminal vs. transient states."
        ],
        "procedure": [
            ("Actor & Role Identification", "Catalogue all system actors (Human Operator, Admin, Celery Scraper Worker, Guidewire Client, Scheduler)."),
            ("State Machine Extraction", "Extract all valid entity states, transient processing stages, failure statuses, and terminal states from database models and enums."),
            ("State Transition Mapping", "Document allowed transitions, triggering events, required preconditions, and state mutation functions."),
            ("Exception & Retry Modeling", "Map exception handling paths: CAPTCHA resolution timeout, portal network retry, dead-letter queue routing, and manual review escalation."),
            ("Visual Workflow & State Diagram Generation", "Generate Mermaid state diagrams (`stateDiagram-v2`) visualizing the end-to-end lifecycle and decision branches.")
        ],
        "safety": [
            "Never define invalid or orphaned states where entities can become permanently stuck without recovery.",
            "Preserve strict state transition invariants (e.g. claims cannot jump from `NEW` directly to `PUSHED` without matching)."
        ],
        "deliverables": [
            "Business Process & State Machine Specification.",
            "Mermaid State Diagram illustrating all valid transitions and exception paths."
        ],
        "acceptance_criteria": [
            "Every state in `RecordStatusEnum`, `BotStatusEnum`, and `StageEnum` is mapped with incoming/outgoing transitions.",
            "Retry limits, backoff periods, and human escalation triggers are explicitly documented.",
            "Terminal states (Complete, Push Succeeded, Fatal Error) are verified as immutable without operator intervention."
        ],
        "error_recovery": [
            "If state transition inconsistencies are detected in code, trace transitions in Celery task runners (`app/tasks/queue_runner.py`).",
            "Cross-reference `docs/STAGE_AND_STATUS_DEFINITIONS.md` as the authoritative single source of state truth."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/business-process-analysis`.",
            "cursor": "Select `@business-process-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `business-process-analysis` workflow.",
            "codex": "Reference `business-process-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run business-process-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt business-process-analysis`.",
            "windsurf": "Activate `business-process-analysis` rule in Windsurf."
        },
        "references": [
            "`docs/STAGE_AND_STATUS_DEFINITIONS.md` - Authoritative Stage & Status Definitions Manual",
            "`backend/app/models/claim.py` - Core Domain Enums"
        ]
    },
    {
        "name": "existing-system-assessment",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Assess an existing solution before proposing changes; guarantee preservation of valid functionality, active data, and test baselines.",
        "purpose": "Conducts a rigorous pre-modification audit of an operational system to capture existing behavior, quantify baseline metrics, identify critical invariants, and prevent accidental regression or architectural damage.",
        "when_to_use": [
            "Prior to refactoring or upgrading existing backend services, scrapers, or database models.",
            "Inheriting legacy components with existing test suites.",
            "Modifying core shared utilities utilized by multiple downstream services."
        ],
        "when_not_to_use": [
            "Completely greenfield modules with zero existing dependencies or callers."
        ],
        "required_inputs": [
            "Target module/service file paths.",
            "Existing test suites covering the target area.",
            "Runtime logs or production telemetry."
        ],
        "prerequisites": [
            "Passing test suite baseline (`pytest`, `tsc`)."
        ],
        "procedure": [
            ("Caller & Dependency Discovery", "Identify all upstream callers and downstream dependencies of the target module using AST search or symbol references."),
            ("Behavioral Contract Audit", "Document the existing function signatures, input parameters, return types, raised exceptions, and side-effects."),
            ("Test Coverage Baseline Verification", "Execute the existing test suite for the component. Verify current pass rates and record baseline execution latency."),
            ("Invariant & Business Rule Identification", "Identify non-negotiable rules embedded in the component (e.g. 1899-12-30 date conversion base, 9-digit ClaimNumber '0' prefix)."),
            ("Assessment & Preservation Summary", "Author an assessment summary defining which behaviors must remain 100% invariant during any upcoming refactoring.")
        ],
        "safety": [
            "CRITICAL: Never remove existing methods or alter public contracts without backward-compatibility wrappers.",
            "Do NOT assume an undocumented behavior is a bug; verify business intent before altering."
        ],
        "deliverables": [
            "System Assessment & Contract Inventory Document.",
            "Baseline Test Report documenting pre-change behavior and metrics."
        ],
        "acceptance_criteria": [
            "All public methods, parameters, and return types of the existing system are catalogued.",
            "Baseline test pass rate is established and recorded.",
            "Invariants and non-negotiable business rules are explicitly flagged for preservation."
        ],
        "error_recovery": [
            "If existing tests fail before changes begin, document pre-existing failures in the assessment before touching code.",
            "If dependencies cannot be fully traced, write characterization tests to capture existing behavior."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/existing-system-assessment`.",
            "cursor": "Select `@existing-system-assessment` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `existing-system-assessment`.",
            "codex": "Reference `existing-system-assessment` in Codex prompt.",
            "gemini": "Invoke via `gemini run existing-system-assessment`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt existing-system-assessment`.",
            "windsurf": "Activate `existing-system-assessment` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Critical Business Rules)",
            "`backend/app/services/fuzzy_engine.py`"
        ]
    },
    {
        "name": "architecture-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Inspect frontend, backend, database, APIs, background queues, integrations, and deployment topology across the entire platform.",
        "purpose": "Evaluates architectural patterns, component coupling, cohesion, scalability bottlenecks, deployment topology, and security perimeters across the full stack.",
        "when_to_use": [
            "Planning architectural evolutions (e.g., SQLite to PostgreSQL, monorepo reorganization).",
            "Evaluating platform scalability under increased concurrency or data volume.",
            "Reviewing multi-service integration boundaries and protocol consistency."
        ],
        "when_not_to_use": [
            "Localized bug fixing within an isolated function.",
            "Adding standard UI components that follow existing patterns."
        ],
        "required_inputs": [
            "Full codebase access across frontend, backend, and infrastructure definitions.",
            "`docker-compose.yml`, configuration schemas, and network port bindings."
        ],
        "prerequisites": [
            "Understanding of modern distributed architecture patterns (FastAPI, Next.js, Celery, Redis)."
        ],
        "procedure": [
            ("Topology & Boundary Mapping", "Map physical and logical tiers: Browser Client -> Next.js Frontend (Port 3000) -> FastAPI Backend (Port 8000) -> Redis Broker (Port 6379) -> Celery Workers -> Relational Database."),
            ("Communication Protocols & Data Formats", "Examine inter-service protocols (HTTP/REST JSON, Redis Pub/Sub, Celery AMQP task messages, Playwright CDP)."),
            ("Persistence Architecture Audit", "Analyze database schema design, connection pooling (`AsyncSessionMaker`), transaction scopes, and SQLite/PostgreSQL parity."),
            ("Asynchronous Queue & Concurrency Topology", "Analyze Celery queue partition strategy, prefetch multipliers, concurrency limits, and worker thread safety."),
            ("Architectural Health & Scalability Report", "Synthesize findings into an Architecture Blueprint highlighting architectural strengths, technical debt, and scaling limits.")
        ],
        "safety": [
            "Do NOT initiate live performance benchmarks that overload local Redis or database instances.",
            "Do NOT expose internal network credentials or connection strings in architecture diagrams."
        ],
        "deliverables": [
            "Holistic Architectural Blueprint and Topology Map.",
            "Mermaid Component Diagram (`flowchart TD`) illustrating inter-service communication."
        ],
        "acceptance_criteria": [
            "All network ports, protocols, and data payloads between services are documented.",
            "Database connection pooling and transaction lifecycle patterns are evaluated.",
            "Worker concurrency and semaphore bottlenecks are identified and documented."
        ],
        "error_recovery": [
            "If port bindings conflict or service addresses are ambiguous, inspect `backend/app/core/config.py` and `docker-compose.yml`.",
            "If worker concurrency behaviors are unclear, inspect `backend/app/core/celery_app.py`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/architecture-analysis`.",
            "cursor": "Select `@architecture-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `architecture-analysis`.",
            "codex": "Reference `architecture-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run architecture-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt architecture-analysis`.",
            "windsurf": "Activate `architecture-analysis` rule in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 2 (Repository Layout)",
            "`docker-compose.yml` - Multi-Container Service Definitions"
        ]
    },
    {
        "name": "dependency-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Review dependency versions, compatibility, known vulnerabilities, licensing, and maintenance status across all package managers.",
        "purpose": "Audits external libraries and runtime dependencies across Python (`requirements.txt`, `.venv`) and JavaScript/TypeScript (`package.json`, `package-lock.json`) to prevent security vulnerabilities, version pinning conflicts, and deprecated API usage.",
        "when_to_use": [
            "Preparing for dependency upgrades or Python/Node runtime updates.",
            "Pre-release security and licensing compliance audits.",
            "Diagnosing mysterious build failures caused by transitive package updates."
        ],
        "when_not_to_use": [
            "Writing internal domain logic with no external dependency changes."
        ],
        "required_inputs": [
            "`backend/requirements.txt`, `backend/.venv`, `frontend/package.json`, `frontend/package-lock.json`."
        ],
        "prerequisites": [
            "Access to package management CLIs (`pip`, `npm`)."
        ],
        "procedure": [
            ("Package Descriptor Inventory", "Parse `backend/requirements.txt` and `frontend/package.json`. Catalogue direct dependencies, version constraints, and development dependencies."),
            ("Python Virtualenv Audit", "Check installed Python packages against pinned requirements using `.venv\\Scripts\\pip list --outdated` (passively). Check compatibility with Python 3.14.7."),
            ("Frontend NPM Audit", "Inspect npm packages for security advisories using `npm audit` (audit-only, no active fix). Check peer dependency compatibility."),
            ("License & Deprecation Review", "Verify that all third-party dependencies carry permissible open-source licenses (MIT, Apache 2.0, BSD) and identify deprecated packages."),
            ("Dependency Health Report", "Produce a prioritized dependency audit report detailing upgrade candidates, critical security patches, and potential breaking changes.")
        ],
        "safety": [
            "Do NOT run `pip install --upgrade` or `npm audit fix --force` without a planned, verified test pass.",
            "Strictly respect Python 3.14.7 compatibility constraints across all native wheels."
        ],
        "deliverables": [
            "Comprehensive Dependency Health & Security Audit Report.",
            "Recommended dependency upgrade path with risk ratings."
        ],
        "acceptance_criteria": [
            "100% of Python and Node dependencies are inventoried with exact pinned versions.",
            "Known vulnerabilities and outdated packages are documented with CVE IDs where applicable.",
            "Zero package modifications performed during analysis."
        ],
        "error_recovery": [
            "If npm audit reports high severity vulnerabilities, evaluate whether they impact build-time vs. runtime code.",
            "If pip packages fail under Python 3.14, search for compatible pre-built wheels or pure-Python alternatives."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/dependency-analysis`.",
            "cursor": "Select `@dependency-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `dependency-analysis`.",
            "codex": "Reference `dependency-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run dependency-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt dependency-analysis`.",
            "windsurf": "Activate `dependency-analysis` in Windsurf."
        },
        "references": [
            "`backend/requirements.txt`",
            "`frontend/package.json`"
        ]
    },
    {
        "name": "impact-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Trace affected modules, data models, API endpoints, background tasks, tests, and users for any proposed code or architectural change.",
        "purpose": "Calculates the blast radius of a planned change before execution, ensuring that all upstream and downstream ramifications are understood, tested, and accounted for.",
        "when_to_use": [
            "Modifying database schemas, columns, or relationship constraints.",
            "Refactoring shared API response schemas or frontend typed models.",
            "Altering Celery task signatures, queue names, or scheduling intervals."
        ],
        "when_not_to_use": [
            "Adding isolated documentation or standalone diagnostic scripts."
        ],
        "required_inputs": [
            "Description or diff of the proposed change.",
            "Repository source tree and test files."
        ],
        "prerequisites": [
            "Completed `existing-system-assessment`."
        ],
        "procedure": [
            ("Scope & Target Identification", "Identify the primary files, functions, schemas, or models proposed for modification."),
            ("Static Dependency Traversal", "Trace all direct and indirect references to the target symbols across backend APIs, Celery tasks, and frontend components."),
            ("Data Model & Persistence Impact", "Determine if database tables, migrations, serialized JSON bodies, or cache keys are affected."),
            ("API Contract & Client Impact", "Determine if frontend Axios endpoints, TypeScript types (`types/index.ts`), or external API payloads (Guidewire) are altered."),
            ("Test Suite & Harness Impact", "Identify all unit, integration, and E2E tests that exercise the affected paths and must be updated or re-verified."),
            ("Impact Matrix Formulation", "Construct an Impact Matrix detailing affected components, risk severity, required test suites, and rollback considerations.")
        ],
        "safety": [
            "Flag any change that modifies database schemas without backward compatibility as High/Critical risk.",
            "Ensure external third-party contracts (Guidewire payload schema) remain strictly backward-compatible."
        ],
        "deliverables": [
            "Impact & Blast Radius Matrix.",
            "Mandatory Test Verification Checklist for the proposed change."
        ],
        "acceptance_criteria": [
            "Every affected backend module, frontend page, database table, and test suite is enumerated.",
            "Breaking change risks are classified and mitigation strategies documented.",
            "Explicit test commands are listed for post-implementation verification."
        ],
        "error_recovery": [
            "If blast radius is unexpectedly large, recommend refactoring using the Strangler Fig or adapter pattern to isolate the change.",
            "If downstream callers cannot be safely updated at once, maintain dual-mode support during migration."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/impact-analysis`.",
            "cursor": "Select `@impact-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `impact-analysis`.",
            "codex": "Reference `impact-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run impact-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt impact-analysis`.",
            "windsurf": "Activate `impact-analysis` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 3 (Critical Business Rules) & Section 11 (Guidewire Contract)",
            "`backend/app/schemas/settings.py`"
        ]
    },
    {
        "name": "technical-feasibility",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Compare feasible implementation approaches, technical constraints, performance trade-offs, and risks before choosing a path.",
        "purpose": "Conducts comparative technical trade-off analysis between 2 or more architecture/implementation candidates, evaluating performance, maintainability, risk, and delivery effort.",
        "when_to_use": [
            "Choosing between competing third-party libraries, architectural patterns, or database technologies.",
            "Designing complex features with multiple viable designs (e.g., synchronous vs asynchronous scraping).",
            "Resolving major architectural blockers."
        ],
        "when_not_to_use": [
            "Implementing standard boilerplate with established project patterns."
        ],
        "required_inputs": [
            "Problem statement and functional requirements.",
            "Candidate technical approaches."
        ],
        "prerequisites": [
            "Understanding of project performance targets and infrastructure constraints."
        ],
        "procedure": [
            ("Candidate Approach Formulation", "Define at least 2 distinct technical approaches (e.g. Option A: Synchronous In-Process Playwright vs Option B: Remote CDP WebSocket Worker)."),
            ("Evaluation Criteria Definition", "Establish objective evaluation criteria: Performance & Latency, Memory Overhead, Reliability, Implementation Complexity, and Maintenance Cost."),
            ("Comparative Scoring & Trade-Off Analysis", "Score each candidate against criteria with documented technical rationale and benchmark evidence."),
            ("Risk & Failure Mode Analysis", "Identify edge-case failure modes for each approach (e.g. extension crashes, zombie processes, memory leaks)."),
            ("Recommendation & Decision Matrix", "Select the optimal approach with justified rationale and draft a recommended adoption roadmap.")
        ],
        "safety": [
            "Never select an approach that violates project non-negotiables (e.g. AntiCaptcha MV3 stability, Python 3.14 compatibility).",
            "Do not optimize prematurely for hypothetical scale at the expense of current stability."
        ],
        "deliverables": [
            "Technical Feasibility & Trade-Off Assessment Document.",
            "Candidate Comparison Matrix with final architectural recommendation."
        ],
        "acceptance_criteria": [
            "At least 2 viable approaches are rigorously evaluated across objective criteria.",
            "Constraints, risks, and failure modes are explicitly identified for each option.",
            "The recommended approach is directly aligned with project business rules."
        ],
        "error_recovery": [
            "If trade-off scores are tied, prioritize the approach with lower implementation complexity and lower blast radius.",
            "If uncertain about external library behavior, run a lightweight spike script in `scripts/`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/technical-feasibility`.",
            "cursor": "Select `@technical-feasibility` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `technical-feasibility`.",
            "codex": "Reference `technical-feasibility` in Codex context.",
            "gemini": "Invoke via `gemini run technical-feasibility`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt technical-feasibility`.",
            "windsurf": "Activate `technical-feasibility` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)",
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "project-documentation-analysis",
        "category_code": "A",
        "category_name": "Project Discovery & Requirements",
        "description": "Read existing specifications, operator manuals, and implementation plans; reconcile them with actual repository reality.",
        "purpose": "Audits existing project documentation (`README.md`, `docs/`, `AGENTS.md`, operator manuals) against the actual codebase to identify stale guides, dead documentation, and missing operational instructions.",
        "when_to_use": [
            "Prior to updating `README.md` or writing new subsystem documentation.",
            "Following major feature implementations or architectural refactoring.",
            "Onboarding new operators or preparing production handovers."
        ],
        "when_not_to_use": [
            "Executing code changes that do not touch documented interfaces."
        ],
        "required_inputs": [
            "All markdown files in `docs/` and root documentation (`README.md`, `AGENTS.md`, `DEPLOYMENT.md`)."
        ],
        "prerequisites": [
            "Access to current codebase to verify documented commands and endpoints."
        ],
        "procedure": [
            ("Documentation Inventory & Indexing", "Catalogue all markdown files in root, `docs/`, and `implementation_plan/`. Record document title, date, version, and declared scope."),
            ("Command & Endpoint Cross-Verification", "Verify documented shell commands, API routes, and script paths against reality. Check if documented endpoints exist in `app/api/v1/endpoints/`."),
            ("Configuration & Settings Drift Audit", "Compare documented settings keys with `SystemSettings` schema in `app/schemas/settings.py`."),
            ("Discrepancy Cataloguing", "Log all documentation drift: outdated URLs, obsolete parameters, dead screenshots, or deprecated scripts."),
            ("Documentation Synchronization Plan", "Formulate a prioritized list of documentation updates required to bring docs into 100% alignment with code.")
        ],
        "safety": [
            "NEVER replace comprehensive project booklets (`README.md`) with simplified summaries.",
            "Preserve historical implementation records in `docs/` for auditability."
        ],
        "deliverables": [
            "Documentation Drift & Reconciled Audit Report.",
            "Actionable Documentation Sync Checklist."
        ],
        "acceptance_criteria": [
            "All documentation files in `docs/` and root are audited against codebase reality.",
            "Every documented API route, shell command, and settings key is verified.",
            "Stale or conflicting documentation is catalogued with required corrections."
        ],
        "error_recovery": [
            "If a documented feature appears missing in code, check recent git commits or branch history before marking it dead.",
            "If contradictory documentation exists, `AGENTS.md` and `README.md` take precedence."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/project-documentation-analysis`.",
            "cursor": "Select `@project-documentation-analysis` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `project-documentation-analysis`.",
            "codex": "Reference `project-documentation-analysis` in Codex context.",
            "gemini": "Invoke via `gemini run project-documentation-analysis`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt project-documentation-analysis`.",
            "windsurf": "Activate `project-documentation-analysis` in Windsurf."
        },
        "references": [
            "`README.md` - Master Architectural Booklet",
            "`docs/` - Operational Guides & Implementation Records"
        ]
    }
]

