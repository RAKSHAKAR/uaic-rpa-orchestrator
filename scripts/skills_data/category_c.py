"""
Category C: Website & Application Development
Contains 19 comprehensive skills for building modern full-stack web applications,
APIs, databases, theme systems, accessible UI components, and dashboards.
"""

SKILLS_C = [
    {
        "name": "website-creation",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Build or extend complete web applications adhering to approved architecture, design system, theme tokens, and accessibility standards.",
        "purpose": "Guides the end-to-end development of modern web applications, coordinating routing, layout hierarchies, component trees, state management, and API integration into a cohesive, performant platform.",
        "when_to_use": [
            "Scaffolding a new web application or major multi-page web module.",
            "Building high-impact user-facing portals with modern frameworks (Next.js 14, React 18)."
        ],
        "when_not_to_use": [
            "Building backend-only background daemons with zero UI surfaces."
        ],
        "required_inputs": [
            "UI/UX wireframes or mockups, page hierarchy specifications, design system tokens, and API schemas."
        ],
        "prerequisites": [
            "Configured Next.js or React runtime with TypeScript and Tailwind CSS."
        ],
        "procedure": [
            ("Layout & Route Hierarchy Scaffolding", "Establish Next.js App Router structure (`app/layout.tsx`, `app/page.tsx`, nested routes). Implement unified `<Navbar />` and footer landmarks."),
            ("Design Token & Theme Integration", "Bind semantic theme tokens (`bg-white dark:bg-slate-900`, CSS variables) ensuring zero hardcoded contrast-breaking colors."),
            ("Page View & State Implementation", "Build responsive page views (`w-full max-w-none flex-1`) with robust loading, empty, and error states."),
            ("API Client Binding & Data Fetching", "Connect UI views to backend REST endpoints via typed Axios/Fetch clients with error boundaries."),
            ("Full-Stack Verification & Accessibility Pass", "Run `tsc --noEmit`, test keyboard navigation, verify contrast, and capture dual-mode screenshots.")
        ],
        "safety": [
            "Never implement auto/OS theme detection; enforce explicit Light and Dark mode selectors.",
            "Do NOT artificially constrain enterprise layouts with fixed max-widths (like `max-w-4xl`)."
        ],
        "deliverables": [
            "Complete responsive web application routes and components.",
            "Dual-theme visual verification evidence in `docs/`."
        ],
        "acceptance_criteria": [
            "All pages render without errors in both Light Mode and Dark Mode.",
            "TypeScript type check passes with 0 errors (`npx tsc --noEmit`).",
            "Responsive layout adapts cleanly to desktop, tablet, and mobile viewports."
        ],
        "error_recovery": [
            "If SSR hydration mismatches occur, verify client-only providers have `'use client'` directives."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/website-creation`.",
            "cursor": "Select `@website-creation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `website-creation`.",
            "codex": "Reference `website-creation` in Codex context.",
            "gemini": "Invoke via `gemini run website-creation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt website-creation`.",
            "windsurf": "Activate `website-creation` in Windsurf."
        },
        "references": [
            "`frontend/src/app/layout.tsx`",
            "`.agents/skills/theme-system/SKILL.md`"
        ]
    },
    {
        "name": "full-stack-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement frontend, backend, database models, and background task processing end-to-end with seamless contract alignment.",
        "purpose": "Coordinates vertical slice development connecting database models, migrations, FastAPI endpoints, Celery workers, and Next.js frontend components in lockstep.",
        "when_to_use": [
            "Implementing vertical business features touching database, API, and UI simultaneously.",
            "Refactoring end-to-end data pipelines from user submission to Guidewire delivery."
        ],
        "when_not_to_use": [
            "Purely frontend cosmetic styling changes.",
            "Backend performance tuning with no UI impact."
        ],
        "required_inputs": [
            "End-to-end feature requirements, entity models, and UI wireframes."
        ],
        "prerequisites": [
            "Active local development stack (`setup_local.ps1` or Docker)."
        ],
        "procedure": [
            ("Database Layer Implementation", "Create or update SQLAlchemy async models (`app/models/`), table schemas, constraints, and migrations."),
            ("Backend Service & Queue Tasks", "Implement business logic services (`app/services/`) and Celery background tasks (`app/tasks/`)."),
            ("FastAPI Endpoint & Schema Exposure", "Create REST API handlers (`app/api/v1/endpoints/`), Pydantic validation schemas, and register routes in `router.py`."),
            ("Frontend Type & Client Generation", "Add TypeScript types to `frontend/src/types/index.ts` and API methods to `frontend/src/lib/api.ts`."),
            ("Frontend Component & Page Development", "Build Next.js pages and components consuming the new API endpoints."),
            ("End-to-End Integration Verification", "Execute backend pytest suites and frontend Playwright E2E tests to verify full workflow.")
        ],
        "safety": [
            "Never hold database transactions open during asynchronous browser automation.",
            "Ensure backend Pydantic schemas and frontend TypeScript types remain 100% synchronized."
        ],
        "deliverables": [
            "Full-stack code changes across backend and frontend repositories.",
            "Automated integration test suite passing with 100% success rate."
        ],
        "acceptance_criteria": [
            "Data roundtrips cleanly from frontend submission through API to database and UI display.",
            "Backend `pytest` and frontend `tsc --noEmit` pass with zero errors.",
            "Audit logging and error telemetry capture feature events."
        ],
        "error_recovery": [
            "If API contract mismatches cause frontend crashes, inspect browser Developer Console and update TypeScript definitions."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/full-stack-development`.",
            "cursor": "Select `@full-stack-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `full-stack-development`.",
            "codex": "Reference `full-stack-development` in Codex context.",
            "gemini": "Invoke via `gemini run full-stack-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt full-stack-development`.",
            "windsurf": "Activate `full-stack-development` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 2 (Repository Layout) & Section 5 (API Endpoints Summary)",
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "frontend-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement accessible, maintainable Next.js 14 App Router pages, components, layouts, and state management.",
        "purpose": "Provides expert engineering guidance for authoring high-performance React 18 components, custom hooks, and full-width layouts using TypeScript and Tailwind CSS.",
        "when_to_use": [
            "Authoring new Next.js routes, dashboard views, or interactive UI components.",
            "Refactoring complex React component state and optimizing render performance."
        ],
        "when_not_to_use": [
            "Backend API development or database schema design."
        ],
        "required_inputs": [
            "Component specification, UI design tokens, and typed API response schemas."
        ],
        "prerequisites": [
            "Next.js 14 App Router project setup (`frontend/`)."
        ],
        "procedure": [
            ("Route & Page Scaffolding", "Create App Router route (`app/<route>/page.tsx`). Mark client-interactive components with `'use client'`."),
            ("Layout & Landmark Architecture", "Enforce enterprise full-width layout (`w-full max-w-none flex-1`) with semantic `<header>`, `<main>`, `<section>` landmarks."),
            ("State & Hook Architecture", "Implement local state (`useState`, `useReducer`), debounce hooks for inputs, and context consumers."),
            ("Dual-Theme Styling", "Apply Tailwind utility classes with dual-mode semantics (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`)."),
            ("Accessibility & Form Validation", "Implement accessible focus rings, ARIA labels, and live region announcements."),
            ("Type Checking & Lint Verification", "Run `npx tsc --noEmit` and `npm run lint`.")
        ],
        "safety": [
            "NEVER use browser `alert()` for user notifications; use toast banners or modal dialogs.",
            "Avoid massive single-file components; modularize into `components/` subdirectories."
        ],
        "deliverables": [
            "Modular React components and Next.js page routes.",
            "Zero TypeScript and ESLint error baseline."
        ],
        "acceptance_criteria": [
            "`npx tsc --noEmit` compiles cleanly with 0 errors.",
            "Component renders identically across Light and Dark themes without visual defects.",
            "Interactive elements are 100% keyboard navigable with visible focus indicators."
        ],
        "error_recovery": [
            "If React useEffect dependency warnings occur, wrap callbacks in `useCallback` or decouple state updates."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/frontend-development`.",
            "cursor": "Select `@frontend-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `frontend-development`.",
            "codex": "Reference `frontend-development` in Codex context.",
            "gemini": "Invoke via `gemini run frontend-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt frontend-development`.",
            "windsurf": "Activate `frontend-development` in Windsurf."
        },
        "references": [
            "`frontend/src/app/page.tsx`",
            "`.agents/skills/theme-system/SKILL.md`"
        ]
    },
    {
        "name": "backend-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement robust FastAPI endpoints, Pydantic schemas, business logic services, and Celery asynchronous workers.",
        "purpose": "Guides backend development adhering to clean architecture, asynchronous database querying (`asyncpg` / `aiosqlite`), structured logging, and resilient background task processing.",
        "when_to_use": [
            "Developing new REST API endpoints, Celery workers, or core business services.",
            "Refactoring database queries and transactional boundaries."
        ],
        "when_not_to_use": [
            "Authoring frontend HTML/CSS components."
        ],
        "required_inputs": [
            "API route specification, database schema models, and task execution parameters."
        ],
        "prerequisites": [
            "Python 3.14.7 virtual environment with installed backend dependencies."
        ],
        "procedure": [
            ("Pydantic Schema Definition", "Define request, response, and query parameter models in `app/schemas/` with strict type annotations."),
            ("Service Layer Implementation", "Author domain business logic in `app/services/` decoupled from HTTP routing logic."),
            ("FastAPI Endpoint Handlers", "Implement async route handlers in `app/api/v1/endpoints/`. Inject `AsyncSession` dependencies and apply HTTP exception handling."),
            ("Router Registration", "Register new router in `app/api/v1/router.py` with appropriate tags and prefixes."),
            ("Celery Task Authoring", "Implement background workers in `app/tasks/` with explicit queue routing, retry policies, and error logging."),
            ("Unit & Integration Testing", "Write comprehensive pytest suites in `tests/` using `AsyncClient` and `ASGITransport`.")
        ],
        "safety": [
            "Never hold database transactions open across long-running external API calls or scraping cycles.",
            "Mask all secrets, passwords, and API tokens in logs and responses."
        ],
        "deliverables": [
            "FastAPI endpoint handlers, Pydantic schemas, and Celery tasks.",
            "Comprehensive pytest integration tests with high assertion coverage."
        ],
        "acceptance_criteria": [
            "All endpoints return appropriate HTTP status codes (200, 201, 400, 404, 422, 500).",
            "Ruff linting passes with 0 errors (`ruff check app tests`).",
            "Backend pytest suite passes without failures."
        ],
        "error_recovery": [
            "If async SQLAlchemy sessions encounter `PendingRollbackError`, ensure all exceptions trigger clean rollbacks in `finally` blocks."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/backend-development`.",
            "cursor": "Select `@backend-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `backend-development`.",
            "codex": "Reference `backend-development` in Codex context.",
            "gemini": "Invoke via `gemini run backend-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt backend-development`.",
            "windsurf": "Activate `backend-development` in Windsurf."
        },
        "references": [
            "`backend/app/main.py`",
            "`backend/app/api/v1/router.py`"
        ]
    },
    {
        "name": "database-design",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Design normalized relational entities, relationships, constraints, indexes, and soft-delete conventions.",
        "purpose": "Establishes sound, scalable relational database architectures ensuring data integrity, foreign key cascading safety, query index efficiency, and multi-tenant isolation.",
        "when_to_use": [
            "Designing new data models or extending existing entities in `app/models/`.",
            "Optimizing slow database queries with targeted composite or partial indexes."
        ],
        "when_not_to_use": [
            "Executing ad-hoc SQL queries or running tests."
        ],
        "required_inputs": [
            "Domain entity specifications, relationship cardinality, and query access patterns."
        ],
        "prerequisites": [
            "Understanding of SQLAlchemy 2.0 declarative models and SQLite/PostgreSQL differences."
        ],
        "procedure": [
            ("Entity & Attribute Normalization", "Define entities to Third Normal Form (3NF). Choose appropriate column types (UUID, String, Integer, DateTime with UTC timezone, JSONB/Text)."),
            ("Relationship & Constraint Modeling", "Specify primary keys, foreign keys, unique constraints, and check constraints. Define explicit `ondelete` cascading behavior (`CASCADE`, `SET NULL`, `RESTRICT`)."),
            ("Index Strategy Formulation", "Design B-tree indexes for foreign keys, filter predicates, and sorting columns. Formulate composite indexes for frequent multi-column queries."),
            ("SQLAlchemy Model Implementation", "Implement declarative models in `app/models/` inheriting from `Base`. Use `Mapped` and `mapped_column` type annotations."),
            ("Schema Documentation & ERD Generation", "Generate Mermaid Entity-Relationship Diagrams (`erDiagram`) documenting table relationships.")
        ],
        "safety": [
            "Never create unbounded text or JSON columns for fields requiring strict validation or indexing.",
            "Ensure SQLite and PostgreSQL compatibility parity across all column definitions."
        ],
        "deliverables": [
            "SQLAlchemy model class definitions in `app/models/`.",
            "Mermaid Entity-Relationship Diagram (ERD)."
        ],
        "acceptance_criteria": [
            "All models define explicit primary keys, column types, and foreign key constraints.",
            "Foreign key columns and common query filter columns are indexed.",
            "Models pass all SQLAlchemy initialization tests without mapping warnings."
        ],
        "error_recovery": [
            "If circular foreign key dependencies occur, utilize `use_alter=True` or decouple relationships via associative tables."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/database-design`.",
            "cursor": "Select `@database-design` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `database-design`.",
            "codex": "Reference `database-design` in Codex context.",
            "gemini": "Invoke via `gemini run database-design`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt database-design`.",
            "windsurf": "Activate `database-design` in Windsurf."
        },
        "references": [
            "`backend/app/models/claim.py`",
            "`backend/app/core/database.py`"
        ]
    },
    {
        "name": "database-migration",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Create safe, idempotent, forward-compatible schema migrations with validated rollback procedures and zero downtime.",
        "purpose": "Guides the authoring, testing, and execution of database schema migrations, ensuring existing production data is preserved, column transformations are reversible, and locks are minimized.",
        "when_to_use": [
            "Adding, altering, or dropping database columns, tables, or constraints.",
            "Backfilling historical data following schema transformations."
        ],
        "when_not_to_use": [
            "Initial database creation during fresh test fixture setup."
        ],
        "required_inputs": [
            "Target model changes in `app/models/` and target database connection string."
        ],
        "prerequisites": [
            "Verified database backup or snapshot.",
            "Understanding of Alembic or programmatic migration scripts."
        ],
        "procedure": [
            ("Pre-Migration Snapshot & Backup", "Verify that an automated snapshot or file backup (`orchestrator.db.bak`) exists before migration execution."),
            ("Migration Script Generation", "Author the forward migration (`upgrade()`) and corresponding backward rollback (`downgrade()`) script."),
            ("Backward Compatibility & Non-Destructive Column Additions", "Add new columns as `nullable=True` or with server defaults to prevent deployment locking."),
            ("Data Backfill & Transformation Pass", "If populating new columns from existing data, write an idempotent batch script updating records in chunks."),
            ("Dry-Run & Rollback Verification", "Test `upgrade()` and immediate `downgrade()` on an isolated test database to verify reversibility."),
            ("Live Migration Execution & Schema Integrity Check", "Execute migration and verify column presence and index creation via database introspection.")
        ],
        "safety": [
            "CRITICAL: Never execute `DROP COLUMN` or `DROP TABLE` without explicit user approval and a verified backup.",
            "Avoid table-locking operations on high-volume tables during business hours."
        ],
        "deliverables": [
            "Idempotent migration script with verified `upgrade` and `downgrade` methods.",
            "Migration execution and verification log."
        ],
        "acceptance_criteria": [
            "Migration executes cleanly without errors on both fresh and populated databases.",
            "Downgrade rollback restores exact prior schema without data loss.",
            "Existing application queries continue functioning seamlessly."
        ],
        "error_recovery": [
            "If migration fails mid-execution, execute the rollback script immediately and restore from the pre-migration snapshot."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/database-migration`.",
            "cursor": "Select `@database-migration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `database-migration`.",
            "codex": "Reference `database-migration` in Codex context.",
            "gemini": "Invoke via `gemini run database-migration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt database-migration`.",
            "windsurf": "Activate `database-migration` in Windsurf."
        },
        "references": [
            "`backend/app/core/database.py`",
            "`scripts/sync_sqlite_to_postgres.py`"
        ]
    },
    {
        "name": "api-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Design and implement OpenAPI-compliant, versioned REST endpoints with strict validation, pagination, and error handling.",
        "purpose": "Enforces best practices for authoring resilient, discoverable, and performant REST APIs using FastAPI, Pydantic v2, and OpenAPI specifications.",
        "when_to_use": [
            "Adding new API resources or endpoints in `app/api/v1/endpoints/`.",
            "Standardizing error responses, pagination query parameters, and sorting logic."
        ],
        "when_not_to_use": [
            "Internal helper functions that are not exposed over HTTP."
        ],
        "required_inputs": [
            "Resource specifications, HTTP method requirements, path parameters, and query schemas."
        ],
        "prerequisites": [
            "FastAPI application routing setup (`app/api/v1/router.py`)."
        ],
        "procedure": [
            ("Endpoint Path & Method Design", "Design RESTful URI adhering to resource naming conventions (e.g. `GET /api/v1/claims`, `POST /api/v1/claims/{id}/start`)."),
            ("Request & Response Schema Binding", "Define input body schemas and output response models with Pydantic `Field` descriptions, examples, and constraints."),
            ("Query Parameter & Pagination Standardization", "Implement standardized pagination parameters (`skip`, `limit`, `sort_by`, `sort_order`)."),
            ("Service Delegation & Dependency Injection", "Delegate business operations to service layer functions; inject `AsyncSession` and authenticated user context."),
            ("Error Handling & Status Codes", "Raise typed `HTTPException` with informative error detail objects for 400, 404, 409, 422 conditions."),
            ("Automated Contract Testing", "Write pytest tests verifying status codes, schema validation rejections, and edge cases.")
        ],
        "safety": [
            "Never return unhandled 500 Internal Server Errors; wrap unexpected exceptions in structured error responses.",
            "Ensure sensitive credentials and tokens are excluded from response schemas."
        ],
        "deliverables": [
            "FastAPI endpoint module registered in `router.py`.",
            "OpenAPI documentation auto-generated and verified at `/docs`.",
            "Comprehensive pytest contract tests."
        ],
        "acceptance_criteria": [
            "All endpoints return typed Pydantic responses with appropriate HTTP status codes.",
            "Malformed inputs trigger descriptive 422 Unprocessable Entity errors.",
            "API appears in OpenAPI `/docs` with detailed summary and schema examples."
        ],
        "error_recovery": [
            "If FastAPI validation fails unexpectedly, inspect Pydantic field validators and serialization modes."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/api-development`.",
            "cursor": "Select `@api-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `api-development`.",
            "codex": "Reference `api-development` in Codex context.",
            "gemini": "Invoke via `gemini run api-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt api-development`.",
            "windsurf": "Activate `api-development` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 5 (API Endpoints Summary)",
            "`backend/app/api/v1/endpoints/claims.py`"
        ]
    },
    {
        "name": "api-integration",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Integrate internal and third-party APIs (e.g. Guidewire, SMTP) with resilient retry backoff, circuit breaking, and telemetry.",
        "purpose": "Provides patterns and safeguards for consuming external HTTP/REST APIs, managing authentication lifecycles (Bearer tokens, API keys, OAuth2), and handling downstream timeouts gracefully.",
        "when_to_use": [
            "Connecting to external enterprise systems (Guidewire Insurance Cloud, AntiCaptcha, Twilio).",
            "Implementing external webhook consumers or outbound dispatchers."
        ],
        "when_not_to_use": [
            "Calling internal database queries or in-process services."
        ],
        "required_inputs": [
            "External API documentation, authentication credentials, endpoint URLs, and payload specifications."
        ],
        "prerequisites": [
            "Configured HTTP client library (`httpx`) with async connection pooling."
        ],
        "procedure": [
            ("Client Architecture & Authentication", "Create dedicated client class (e.g. `GuidewireClient`) encapsulating authentication headers, token refresh, and base URLs."),
            ("Payload Serializer & Contract Validation", "Implement strict payload transformers formatting outgoing data to the exact external contract (e.g. 9-digit ClaimNumber '0' prefix)."),
            ("Timeout & Connection Pool Configuration", "Set explicit connect, read, and write timeouts (e.g. 30s timeout) to prevent hanging worker threads."),
            ("Retry Policy & Exponential Backoff", "Implement exponential backoff with jitter for transient HTTP 429, 502, 503, 504 errors using Celery or tenacity."),
            ("Logging, Telemetry & Secret Masking", "Log request timing, URL, and status codes while masking authorization tokens and customer PII."),
            ("Mock Test Suite Verification", "Author comprehensive mock unit tests simulating external success, timeout, 401 unauthorized, and 500 error responses.")
        ],
        "safety": [
            "CRITICAL: Never log raw API authorization headers, Bearer tokens, or API keys.",
            "Always enforce strict timeout limits to prevent thread exhaustion in Celery workers."
        ],
        "deliverables": [
            "Dedicated API Client class in `app/services/`.",
            "Mock-backed integration test suite covering success and failure modes."
        ],
        "acceptance_criteria": [
            "External calls adhere strictly to target third-party payload schemas.",
            "Transient network failures trigger retry with exponential backoff.",
            "Zero plain-text credentials leak into logs or telemetry."
        ],
        "error_recovery": [
            "If external API changes response format, capture error body in audit logs and update Pydantic client schema."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/api-integration`.",
            "cursor": "Select `@api-integration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `api-integration`.",
            "codex": "Reference `api-integration` in Codex context.",
            "gemini": "Invoke via `gemini run api-integration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt api-integration`.",
            "windsurf": "Activate `api-integration` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 11 (Guidewire Payload Contract)",
            "`backend/app/services/guidewire_client.py`"
        ]
    },
    {
        "name": "authentication-authorization",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement authentication, role-based authorization (RBAC), secure session cookies, API tokens, and access boundaries.",
        "purpose": "Establishes multi-layer security controls protecting sensitive routes, APIs, and administrative functions from unauthorized access, privilege escalation, or session hijacking.",
        "when_to_use": [
            "Adding authentication to unprotected endpoints or administrative control panels.",
            "Implementing role-based permissions (Admin, Operator, Read-Only Auditor).",
            "Hardening API token authentication for automated system clients."
        ],
        "when_not_to_use": [
            "Public health-check endpoints (`/health`)."
        ],
        "required_inputs": [
            "User identity models, role definitions, permission matrix, and token signing secrets."
        ],
        "prerequisites": [
            "Cryptographic hashing library (e.g. `passlib`, `bcrypt`, `pyjwt`)."
        ],
        "procedure": [
            ("Identity & Credential Modeling", "Define User, Role, and Permission entities with hashed password storage (bcrypt/argon2)."),
            ("Token & Session Management", "Implement JWT or secure HTTP-only session cookie issuance with explicit expiration and rotation policies."),
            ("FastAPI Security Dependency Injection", "Create security dependencies (`get_current_user`, `require_admin_role`) using FastAPI `Security` and `HTTPBearer`."),
            ("Role & Permission Matrix Enforcement", "Enforce permission checks at endpoint boundaries. Block unauthorized requests with 401 Unauthorized or 403 Forbidden."),
            ("Frontend Auth State & Route Protection", "Implement client-side authentication guards, token refresh interceptors, and login/logout state transitions."),
            ("Security Test Suite Execution", "Write tests verifying that unauthenticated and unauthorized requests are rejected consistently.")
        ],
        "safety": [
            "Never store plain-text passwords or secret keys in source code or repositories.",
            "Ensure session cookies specify `HttpOnly`, `Secure`, and `SameSite=Lax/Strict` attributes."
        ],
        "deliverables": [
            "Authentication dependencies and role-based guards.",
            "Automated security tests verifying access control enforcement."
        ],
        "acceptance_criteria": [
            "Protected endpoints reject unauthenticated requests with HTTP 401.",
            "Role restrictions reject unauthorized users with HTTP 403.",
            "Passwords are hashed with salt using modern cryptographic algorithms."
        ],
        "error_recovery": [
            "If token expiration causes UI loops, implement seamless refresh token handling in Axios interceptors."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/authentication-authorization`.",
            "cursor": "Select `@authentication-authorization` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `authentication-authorization`.",
            "codex": "Reference `authentication-authorization` in Codex context.",
            "gemini": "Invoke via `gemini run authentication-authorization`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt authentication-authorization`.",
            "windsurf": "Activate `authentication-authorization` in Windsurf."
        },
        "references": [
            "`backend/app/core/config.py`",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "multi-tenant-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Enforce strict tenant, organization, or carrier data isolation across database queries, caching, and background workers.",
        "purpose": "Guarantees complete data segregation between different business tenants or carriers, preventing cross-tenant data leakage in multi-tenant SaaS environments.",
        "when_to_use": [
            "Adding multi-carrier or multi-organization support to the platform.",
            "Auditing database queries and cache keys for data leakage risks."
        ],
        "when_not_to_use": [
            "Single-tenant dedicated local installations."
        ],
        "required_inputs": [
            "Tenant entity definitions, tenant identification headers/tokens, and database isolation strategy (row-level, schema-level, or DB-level)."
        ],
        "prerequisites": [
            "Understanding of tenant context propagation in async Python and Next.js."
        ],
        "procedure": [
            ("Tenant Context Extraction", "Extract tenant identity from incoming requests (subdomain, JWT claim, or `X-Tenant-ID` header) via middleware."),
            ("Context Variable Binding", "Bind active tenant ID to Python `contextvars.ContextVar` or request state for thread-safe access."),
            ("ORM Query Filtering Enforcement", "Ensure all database queries automatically filter by `tenant_id` using SQLAlchemy event listeners or base queries."),
            ("Cache & Task Partitioning", "Prefix all Redis cache keys and Celery task payload arguments with the active `tenant_id`."),
            ("Tenant Isolation Test Pass", "Write automated tests creating records under Tenant A and proving Tenant B cannot query or mutate them.")
        ],
        "safety": [
            "CRITICAL: Never execute unfiltered queries (`select(Model)`) without tenant scoping in a multi-tenant environment.",
            "Ensure shared background workers do not leak tenant state across tasks."
        ],
        "deliverables": [
            "Tenant middleware, context handlers, and auto-filtering query hooks.",
            "Multi-tenant isolation verification test suite."
        ],
        "acceptance_criteria": [
            "All queries are strictly partitioned by tenant ID.",
            "Cross-tenant data access attempts return 404 or 403.",
            "Cache keys and background queues maintain clean tenant namespaces."
        ],
        "error_recovery": [
            "If an un-scoped query is detected, patch the repository layer to mandate tenant parameters."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/multi-tenant-development`.",
            "cursor": "Select `@multi-tenant-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `multi-tenant-development`.",
            "codex": "Reference `multi-tenant-development` in Codex context.",
            "gemini": "Invoke via `gemini run multi-tenant-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt multi-tenant-development`.",
            "windsurf": "Activate `multi-tenant-development` in Windsurf."
        },
        "references": [
            "`backend/app/core/database.py`"
        ]
    },
    {
        "name": "responsive-ui-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Build and validate fluid, usable layouts across mobile (375px), tablet (768px), and widescreen desktop (1920px) viewports.",
        "purpose": "Ensures all web interfaces adapt seamlessly across diverse screen resolutions without horizontal overflow, overlapping controls, unreadable text, or truncated data tables.",
        "when_to_use": [
            "Authoring or revising UI pages, stat cards, data grids, or navigation headers.",
            "Fixing mobile layout glitches or table scrolling defects."
        ],
        "when_not_to_use": [
            "Backend API or headless worker tasks."
        ],
        "required_inputs": [
            "Target page components, responsive breakpoint specifications, and viewports."
        ],
        "prerequisites": [
            "Tailwind CSS responsive modifiers (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)."
        ],
        "procedure": [
            ("Mobile-First Layout Scaffolding", "Design base utility classes for mobile screens (375px-640px) with single-column flow and responsive typography."),
            ("Grid & Flex Adaptability", "Implement adaptive grids (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`) for stat cards and metric panels."),
            ("Table & Data Grid Responsiveness", "Wrap wide tabular data in horizontal scroll containers (`overflow-x-auto`) with fixed column headers."),
            ("Navigation Drawer & Header Adaptability", "Provide responsive hamburger drawers for mobile viewports and persistent navigation bars on desktop."),
            ("Multi-Viewport Verification", "Validate rendering across 375px, 768px, 1280px, and 1920px viewports using Playwright or browser DevTools.")
        ],
        "safety": [
            "Never allow horizontal scroll on the primary `body` or `html` element.",
            "Do NOT use fixed pixel widths on container elements (use `w-full` or percentages)."
        ],
        "deliverables": [
            "Responsive Next.js components and layouts.",
            "Multi-viewport visual screenshot evidence."
        ],
        "acceptance_criteria": [
            "Zero horizontal overflow on mobile viewports (375px).",
            "Stat cards and grids reflow gracefully across tablet and desktop sizes.",
            "Touch targets on mobile meet minimum 44x44px accessibility guidelines."
        ],
        "error_recovery": [
            "If elements cause horizontal overflow, inspect DevTools DOM with `* { outline: 1px solid red; }` to locate rogue fixed-width elements."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/responsive-ui-development`.",
            "cursor": "Select `@responsive-ui-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `responsive-ui-development`.",
            "codex": "Reference `responsive-ui-development` in Codex context.",
            "gemini": "Invoke via `gemini run responsive-ui-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt responsive-ui-development`.",
            "windsurf": "Activate `responsive-ui-development` in Windsurf."
        },
        "references": [
            "`frontend/src/app/page.tsx`",
            "`frontend/src/components/Navbar.tsx`"
        ]
    },
    {
        "name": "design-system",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Maintain centralized semantic tokens, typography scales, spacing units, and reusable UI component primitives.",
        "purpose": "Establishes a unified visual design language across the application, preventing fragmented styles, inconsistent padding, and rogue colors through centralized tokens.",
        "when_to_use": [
            "Creating or standardizing core UI primitives (Buttons, Inputs, Badges, Modals, Cards).",
            "Updating global application typography, spacing, or branding palettes."
        ],
        "when_not_to_use": [
            "Backend service logic."
        ],
        "required_inputs": [
            "Brand identity guidelines, color palettes, typography specs, and spacing scales."
        ],
        "prerequisites": [
            "Tailwind CSS configuration (`tailwind.config.ts`) and CSS variable root."
        ],
        "procedure": [
            ("Semantic Token Definition", "Define semantic color tokens in CSS variables: `--primary`, `--background`, `--card`, `--border`, `--muted`."),
            ("Tailwind Token Extension", "Map CSS variables into `tailwind.config.ts` allowing standard utility consumption (`bg-primary`, `border-border`)."),
            ("Typography & Elevation Scales", "Standardize font sizes (`text-xs` to `text-3xl`), font weights, and shadow elevations (`shadow-sm`, `shadow-md`)."),
            ("Component Primitive Library", "Author standardized UI primitives (`Button`, `Badge`, `Input`, `Card`, `Modal`) in `frontend/src/components/ui/`."),
            ("Living Styleguide Documentation", "Document token usage and component variants in the `/branding` management console.")
        ],
        "safety": [
            "Never use raw hex codes directly in page components; always consume semantic tokens.",
            "Ensure every token pair maintains WCAG AA contrast (4.5:1) in both Light and Dark modes."
        ],
        "deliverables": [
            "Updated `tailwind.config.ts` and global CSS variable definitions.",
            "Standardized UI component primitives in `frontend/src/components/`."
        ],
        "acceptance_criteria": [
            "All new UI components consume centralized semantic tokens.",
            "The `/branding` page reflects live palette updates in real time.",
            "Zero rogue hex codes exist in newly developed components."
        ],
        "error_recovery": [
            "If Tailwind classes fail to compile, verify that custom token names in `tailwind.config.ts` match CSS variable definitions."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/design-system`.",
            "cursor": "Select `@design-system` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `design-system`.",
            "codex": "Reference `design-system` in Codex context.",
            "gemini": "Invoke via `gemini run design-system`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt design-system`.",
            "windsurf": "Activate `design-system` in Windsurf."
        },
        "references": [
            "`frontend/src/app/branding/page.tsx`",
            "`.agents/skills/theme-system/SKILL.md`"
        ]
    },
    {
        "name": "theme-system",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Global Light and Dark mode theme governance: strictly enforce dual modes, prohibit OS auto-detection, and unify Branding tokens.",
        "purpose": "Governs the application's Light and Dark theme architecture. Strictly prohibits system/OS automatic detection and mandates the `/branding` page as the single authoritative source of truth for 26 semantic color tokens.",
        "when_to_use": [
            "Authoring or revising ANY UI component, modal, form, page, or table.",
            "Auditing theme contrast, readability, and dynamic palette synchronization."
        ],
        "when_not_to_use": [
            "Backend headless scripts or Celery workers with no UI output."
        ],
        "required_inputs": [
            "`frontend/src/context/BrandingContext.tsx`, `app/branding/page.tsx`, and Tailwind CSS configuration."
        ],
        "prerequisites": [
            "Knowledge of CSS variable dynamic injection in `:root` and `.dark`."
        ],
        "procedure": [
            ("Enforce Exactly Two Theme Modes", "Support strictly `Light` (`[data-theme='light']`) and `Dark` (`[data-theme='dark']`). Prohibit OS auto-detection (`prefers-color-scheme`)."),
            ("Branding Page Authority", "Ensure `/branding` controls both Light Mode and Dark Mode palettes, persisted in database settings (`BrandingSettings`)."),
            ("Dual-Token Pairing", "Pair every background utility with a corresponding text color (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`)."),
            ("Dynamic Injection Verification", "Verify that `BrandingContext.tsx` updates active CSS variables in `:root` and `.dark` in real time without page reloads."),
            ("Dual-Mode Visual Verification", "Inspect all pages in both Light Mode and Dark Mode. Confirm zero white-on-white or black-on-black defects.")
        ],
        "safety": [
            "CRITICAL: NEVER implement `window.matchMedia('(prefers-color-scheme: ...)')` or auto-detection toggles.",
            "Never allow white text on white background or black text on black background under either mode."
        ],
        "deliverables": [
            "Theme-compliant React components and layouts.",
            "Dual-theme screenshot verification artifacts in `docs/`."
        ],
        "acceptance_criteria": [
            "Application toggles cleanly between Light and Dark modes via the header selector.",
            "All inputs, cards, borders, and modals are clearly readable under both themes.",
            "Zero OS auto-detection logic exists in codebase."
        ],
        "error_recovery": [
            "If text is unreadable in Dark Mode, replace hardcoded slate classes with semantic token classes or explicit `dark:text-slate-100` variants."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/theme-system` or follow `.agents/skills/theme-system/SKILL.md`.",
            "cursor": "Select `@theme-system` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `theme-system`.",
            "codex": "Reference `theme-system` in Codex context.",
            "gemini": "Invoke via `gemini run theme-system`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt theme-system`.",
            "windsurf": "Activate `theme-system` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md` (Authoritative Theme Governance Skill)",
            "`frontend/src/app/branding/page.tsx`"
        ]
    },
    {
        "name": "component-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Create encapsulated, accessible, and testable React components with strict TypeScript contracts and clear prop interfaces.",
        "purpose": "Guides the authoring of reusable frontend components that adhere to Single Responsibility, strict typing, memoization, and accessible keyboard interactions.",
        "when_to_use": [
            "Building new UI widgets, data cards, modals, or filter controls.",
            "Extracting repetitive JSX markup into shared reusable components."
        ],
        "when_not_to_use": [
            "Writing one-off script commands or backend functions."
        ],
        "required_inputs": [
            "Component functional requirements, prop definitions, and event callback signatures."
        ],
        "prerequisites": [
            "TypeScript and React 18 component architecture."
        ],
        "procedure": [
            ("Prop Interface Definition", "Define strict TypeScript `interface <ComponentName>Props` with explicit types, optional flags, and JSDoc descriptions."),
            ("Component Implementation", "Implement functional component using named export. Destructure props with clean defaults."),
            ("State & Effect Management", "Manage internal state with `useState` or custom hooks. Avoid unnecessary `useEffect` triggers."),
            ("Accessibility & ARIA", "Apply semantic HTML elements (`<button>`, `<dialog>`), ARIA labels (`aria-label`, `aria-expanded`), and keyboard event handlers (`onKeyDown`)."),
            ("Dual-Theme Styling", "Style with Tailwind utility classes adhering to the dual-theme token system."),
            ("Component Verification", "Verify component rendering and interactions with TypeScript type-checking.")
        ],
        "safety": [
            "Avoid prop drilling deeper than 2 levels; use Context or state management for deep state.",
            "Never use `any` in component prop interfaces."
        ],
        "deliverables": [
            "TypeScript React component file in `frontend/src/components/`.",
            "Exported component contract and unit test if applicable."
        ],
        "acceptance_criteria": [
            "Component compiles cleanly with zero TypeScript errors.",
            "Keyboard interactions (Enter, Space, Escape, Tab) function properly.",
            "Renders cleanly in both Light Mode and Dark Mode."
        ],
        "error_recovery": [
            "If re-renders cause performance drops, wrap component in `React.memo` or extract memoized subcomponents."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/component-development`.",
            "cursor": "Select `@component-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `component-development`.",
            "codex": "Reference `component-development` in Codex context.",
            "gemini": "Invoke via `gemini run component-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt component-development`.",
            "windsurf": "Activate `component-development` in Windsurf."
        },
        "references": [
            "`frontend/src/components/Navbar.tsx`",
            "`frontend/src/types/index.ts`"
        ]
    },
    {
        "name": "form-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Build accessible forms with client and server-side validation, accessible error announcements, and debounced submission.",
        "purpose": "Ensures user input forms handle data entry, validation feedback, submission states, and backend error mapping reliably and accessibly.",
        "when_to_use": [
            "Authoring forms for claim creation, settings configuration, or filter criteria.",
            "Implementing complex multi-step wizards or upload dialogs."
        ],
        "when_not_to_use": [
            "Read-only data display grids."
        ],
        "required_inputs": [
            "Form field schemas, validation rules (regex, ranges, required fields), and submission endpoint."
        ],
        "prerequisites": [
            "Typed API client and backend Pydantic validation schemas."
        ],
        "procedure": [
            ("Form State & Schema Definition", "Define form state interface with TypeScript. Establish validation rules mirroring backend Pydantic schemas."),
            ("Accessible Field Rendering", "Render form controls with associated `<label htmlFor='...'>`, `<input id='...'>`, and `<span role='alert'>` error messages."),
            ("Client-Side Validation & Feedback", "Validate fields on blur and submit. Display inline error messages with clear, actionable guidance."),
            ("Submission State & Debounce", "Disable submit button during active submission (`isSubmitting`). Prevent duplicate clicks with debounced handlers."),
            ("Backend Error Mapping", "Parse FastAPI 422 validation detail arrays and map field-specific errors back to corresponding form inputs."),
            ("Success Notification & Form Reset", "Show success toast notification upon completion and optionally reset form state.")
        ],
        "safety": [
            "Never submit passwords or sensitive tokens via unencrypted query parameters.",
            "Always validate inputs on the server regardless of client-side validation."
        ],
        "deliverables": [
            "Accessible React form component with complete validation logic.",
            "Error handling and submission verification pass."
        ],
        "acceptance_criteria": [
            "All required fields enforce validation before submission.",
            "Server-side 422 validation errors are rendered inline beside offending inputs.",
            "Submitting state prevents concurrent duplicate submissions."
        ],
        "error_recovery": [
            "If form state desynchronizes, reset to last known-good state or initial defaults."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/form-development`.",
            "cursor": "Select `@form-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `form-development`.",
            "codex": "Reference `form-development` in Codex context.",
            "gemini": "Invoke via `gemini run form-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt form-development`.",
            "windsurf": "Activate `form-development` in Windsurf."
        },
        "references": [
            "`frontend/src/app/settings/page.tsx`",
            "`backend/app/schemas/settings.py`"
        ]
    },
    {
        "name": "dashboard-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Build functional, real-time operational dashboards with responsive stat cards, filter bars, telemetry grids, and charts.",
        "purpose": "Guides the creation of high-density executive and operational dashboards that present real-time system metrics, queue depths, throughput charts, and searchable data grids.",
        "when_to_use": [
            "Authoring or enhancing main application dashboards (`/`, `/monitor`, `/health`).",
            "Adding operational stat cards, throughput charts, or batch telemetry views."
        ],
        "when_not_to_use": [
            "Backend scraper tasks with no UI representation."
        ],
        "required_inputs": [
            "Metric definitions, aggregate API endpoints (`/api/v1/claims/stats`), and filter dimensions."
        ],
        "prerequisites": [
            "FastAPI stats endpoints and Next.js page routing."
        ],
        "procedure": [
            ("Dashboard Grid Scaffolding", "Establish full-width container (`w-full max-w-none flex-1`). Create responsive stat card grid (`grid-cols-2 md:grid-cols-4 lg:grid-cols-8`)."),
            ("Metric Stat Cards Implementation", "Implement clickable stat cards displaying title, count, trend indicator, and active filter state."),
            ("Filter Bar & Search Controls", "Implement debounced text search, dropdown status filters, date range pickers, and clear-all actions."),
            ("Data Grid & Table Integration", "Render paginated data table with sortable column headers, status badges, and action buttons."),
            ("Real-Time Telemetry & Polling", "Implement automatic periodic refresh (e.g. 10s poll) with visual pause toggle for live queue monitoring."),
            ("Loading & Empty States", "Provide clean skeleton loaders during fetch and helpful empty state illustrations when zero records match filters.")
        ],
        "safety": [
            "Never allow rapid polling intervals (< 2s) that overload the backend or SQLite database locks.",
            "Ensure dashboard filters update URL query parameters for shareability."
        ],
        "deliverables": [
            "Operational dashboard page with interactive stat cards, filters, and data grid.",
            "Verified responsive layout across desktop and mobile screens."
        ],
        "acceptance_criteria": [
            "Stat cards accurately reflect backend database counts.",
            "Filtering data table dynamically updates view without full page reloads.",
            "Auto-refresh functions reliably without causing memory leaks or UI jitter."
        ],
        "error_recovery": [
            "If polling fails due to network disconnect, back off polling interval and display a discreet reconnecting banner."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/dashboard-development`.",
            "cursor": "Select `@dashboard-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `dashboard-development`.",
            "codex": "Reference `dashboard-development` in Codex context.",
            "gemini": "Invoke via `gemini run dashboard-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt dashboard-development`.",
            "windsurf": "Activate `dashboard-development` in Windsurf."
        },
        "references": [
            "`frontend/src/app/page.tsx` - Main Claims Dashboard",
            "`frontend/src/app/monitor/page.tsx` - Queue Monitor Dashboard"
        ]
    },
    {
        "name": "admin-panel-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement secure administration workflows, system configuration forms, audit viewers, and bulk operations.",
        "purpose": "Provides engineering patterns for administrative consoles (e.g. `/settings`, `/branding`, `/audit`) with elevated privileges, bulk management actions, and tamper-evident audit trails.",
        "when_to_use": [
            "Building or expanding administrator control panels or robot configuration pages.",
            "Implementing bulk deletion, bulk retriggering, or system reset functions."
        ],
        "when_not_to_use": [
            "Standard consumer or read-only user views."
        ],
        "required_inputs": [
            "Administrative action definitions, settings schemas, and audit logging endpoints."
        ],
        "prerequisites": [
            "Role-based access control or operator authentication."
        ],
        "procedure": [
            ("Tabbed Navigation & Sectioning", "Organize administrative controls into tabbed sections (General, Automation, Portals, Email, Proxy, Audit, Branding)."),
            ("Configuration Form Implementation", "Bind controls (toggles, sliders, inputs) to backend `SystemSettings`. Implement save, cancel, and reset-to-defaults actions."),
            ("Confirmation Modals for Dangerous Actions", "Require explicit typed confirmation modals for destructive operations (e.g. Clean All Records, Clear Redis Queue)."),
            ("Bulk Action Toolbar", "Implement multi-select checkboxes on data grids with bulk start, bulk retry, and bulk export actions."),
            ("Audit Logging Integration", "Log every administrative setting change and bulk action to `AuditLog` table with timestamp, operator ID, and change diff."),
            ("Verification Pass", "Test setting persistence across page reloads and backend service restarts.")
        ],
        "safety": [
            "CRITICAL: Always require explicit double-confirmation before executing destructive bulk operations.",
            "Ensure administrative endpoints verify credentials on the backend, not merely via hidden UI buttons."
        ],
        "deliverables": [
            "Secure administrative management page with verified settings persistence.",
            "Audit trail capturing all administrative actions."
        ],
        "acceptance_criteria": [
            "Settings changes persist in database and reload accurately across sessions.",
            "Dangerous bulk actions require explicit confirmation dialog.",
            "All administrative mutations generate immutable audit log records."
        ],
        "error_recovery": [
            "If saving settings fails due to validation errors, display field-specific error highlights and preserve user inputs."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/admin-panel-development`.",
            "cursor": "Select `@admin-panel-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `admin-panel-development`.",
            "codex": "Reference `admin-panel-development` in Codex context.",
            "gemini": "Invoke via `gemini run admin-panel-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt admin-panel-development`.",
            "windsurf": "Activate `admin-panel-development` in Windsurf."
        },
        "references": [
            "`frontend/src/app/settings/page.tsx`",
            "`backend/app/api/v1/endpoints/settings.py`"
        ]
    },
    {
        "name": "mobile-app-development",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Guidelines and scaffolding for building native or hybrid mobile client applications and consuming backend APIs.",
        "purpose": "Provides architectural guidelines for developing cross-platform mobile applications (React Native, Flutter, PWA) that consume backend REST APIs securely with offline caching.",
        "when_to_use": [
            "Designing or implementing mobile client applications companion to the web platform.",
            "Configuring Progressive Web App (PWA) manifests and service workers."
        ],
        "when_not_to_use": [
            "Standard desktop browser web applications."
        ],
        "required_inputs": [
            "Mobile screen designs, touch interaction specifications, and mobile API endpoints."
        ],
        "prerequisites": [
            "REST API documentation and authentication schemas."
        ],
        "procedure": [
            ("Mobile Architecture & Framework Selection", "Select target framework (PWA, React Native, or native Kotlin/Swift) based on offline requirements and hardware access."),
            ("PWA Manifest & Icon Scaffolding", "Create `manifest.json` with app icons, theme colors, display modes, and service worker registration."),
            ("Touch Interaction & Gesture Design", "Implement touch-optimized controls with minimum 44x44px hit targets and swipe gesture navigation."),
            ("Offline Storage & Synchronization", "Implement local caching (IndexedDB, SQLite) with background queue synchronization when network restores."),
            ("Push Notification Integration", "Configure push notification services for claim completion and system alerts."),
            ("Mobile Emulation Verification", "Test application in mobile device emulators across iOS and Android viewports.")
        ],
        "safety": [
            "Never store unencrypted tokens or credentials in insecure mobile device storage.",
            "Handle intermittent network connectivity gracefully with offline retry queues."
        ],
        "deliverables": [
            "PWA manifest and mobile-responsive shell or mobile client project.",
            "Offline caching and sync handlers."
        ],
        "acceptance_criteria": [
            "Application installs as PWA or runs on mobile device emulator without errors.",
            "Touch interactions and gestures function smoothly without lag.",
            "Offline state displays clear notification and queues actions for sync."
        ],
        "error_recovery": [
            "If sync collisions occur upon reconnecting, apply server-wins or timestamp-based reconciliation."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/mobile-app-development`.",
            "cursor": "Select `@mobile-app-development` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `mobile-app-development`.",
            "codex": "Reference `mobile-app-development` in Codex context.",
            "gemini": "Invoke via `gemini run mobile-app-development`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt mobile-app-development`.",
            "windsurf": "Activate `mobile-app-development` in Windsurf."
        },
        "references": [
            "`frontend/public/`",
            "`AGENTS.md` - Section 6"
        ]
    },
    {
        "name": "accessibility-implementation",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement WCAG 2.1 AA accessibility compliance, semantic HTML landmarks, ARIA attributes, and full keyboard navigation.",
        "purpose": "Ensures the application is fully accessible to users with disabilities, screen-reader assistive technology, and keyboard-only navigation.",
        "when_to_use": [
            "Authoring or auditing any user-facing frontend component, modal, or page.",
            "Pre-release compliance audits against ADA and WCAG 2.1 standards."
        ],
        "when_not_to_use": [
            "Backend server logic or database scripts."
        ],
        "required_inputs": [
            "Frontend component source code and color palette token definitions."
        ],
        "prerequisites": [
            "Knowledge of WCAG 2.1 Level AA criteria and ARIA 1.2 authoring practices."
        ],
        "procedure": [
            ("Semantic Landmark Architecture", "Structure pages with `<header>`, `<nav>`, `<main>`, `<section>`, and `<footer>` landmarks. Provide skip-to-content links."),
            ("Keyboard Navigation & Focus Management", "Ensure all interactive elements are focusable via Tab. Implement visible focus rings (`focus-visible:ring-2`). Manage focus traps in modal dialogs."),
            ("Color Contrast & Typography Verification", "Verify text contrast ratio $\\ge 4.5:1$ against background in both Light Mode and Dark Mode ($3:1$ for large text)."),
            ("ARIA Roles & Labels", "Apply `aria-label`, `aria-describedby`, `aria-expanded`, and `aria-live` for dynamic updates (e.g. live queue counts)."),
            ("Form Accessibility", "Ensure all `<input>` elements have associated `<label>` tags with matching `htmlFor`/`id` bindings."),
            ("Screen Reader & Axe-Core Audit", "Audit pages using automated `axe-core` checks and manual keyboard navigation walkthrough.")
        ],
        "safety": [
            "Never remove outline rings with `outline: none` without providing an accessible alternative focus indicator.",
            "Do not convey information using color alone (pair colors with text badges or icons)."
        ],
        "deliverables": [
            "Accessibility-compliant Next.js pages and components.",
            "Axe-core accessibility audit report with 0 critical/serious violations."
        ],
        "acceptance_criteria": [
            "100% of interactive controls are operable via keyboard alone.",
            "Color contrast meets or exceeds WCAG AA (4.5:1) in both Light and Dark modes.",
            "Automated accessibility scans report zero critical violations."
        ],
        "error_recovery": [
            "If modal dialogs fail to trap focus, wrap modal contents in a focus-trap container component."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/accessibility-implementation`.",
            "cursor": "Select `@accessibility-implementation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `accessibility-implementation`.",
            "codex": "Reference `accessibility-implementation` in Codex context.",
            "gemini": "Invoke via `gemini run accessibility-implementation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt accessibility-implementation`.",
            "windsurf": "Activate `accessibility-implementation` in Windsurf."
        },
        "references": [
            "`.agents/skills/theme-system/SKILL.md` - Section 2",
            "`frontend/src/components/Navbar.tsx`"
        ]
    },
    {
        "name": "internationalization",
        "category_code": "C",
        "category_name": "Website & Application Development",
        "description": "Implement multi-locale message catalogs, date/currency formatting, language switching, and RTL layout compatibility.",
        "purpose": "Prepares the application for global multi-language deployment by abstracting UI text into localized message catalogs and formatting dates/numbers according to user locale.",
        "when_to_use": [
            "Adding multilingual support (e.g. Spanish, French) to the platform.",
            "Standardizing date and number formatting across international jurisdictions."
        ],
        "when_not_to_use": [
            "Strictly internal single-language backends where English is the permanent standard."
        ],
        "required_inputs": [
            "UI message strings, supported locale codes (`en-US`, `es-ES`), and translation dictionaries."
        ],
        "prerequisites": [
            "Internationalization framework (e.g. `next-intl`, `react-i18next`)."
        ],
        "procedure": [
            ("Hardcoded String Extraction", "Extract hardcoded English text strings from JSX into centralized JSON dictionary catalogs (`messages/en.json`)."),
            ("Translation Catalog Structure", "Organize messages by feature namespace (`common`, `dashboard`, `settings`, `errors`)."),
            ("Locale Provider & Hook Integration", "Wrap application in `I18nProvider`. Replace static text with translation hooks (`t('dashboard.title')`)."),
            ("Date, Time & Number Formatting", "Replace hardcoded date strings with `Intl.DateTimeFormat` and currency with `Intl.NumberFormat`."),
            ("Language Selector Component", "Implement accessible language dropdown selector in the navigation bar persisting user choice."),
            ("RTL & Layout Adaptability", "Ensure CSS layouts support bi-directional flow (`dir='rtl'`) if targeting Arabic or Hebrew locales.")
        ],
        "safety": [
            "Never translate technical system identifiers, API enum keys, or database column names.",
            "Preserve exact date conversion rules (e.g., DOL base date 1899-12-30) regardless of display locale."
        ],
        "deliverables": [
            "Localized message catalogs (`en.json`, `es.json`).",
            "Internationalized Next.js components with locale switching."
        ],
        "acceptance_criteria": [
            "Switching languages dynamically re-renders all UI text without page reload errors.",
            "Dates and numbers format according to the active locale standard.",
            "Zero missing translation key warnings in console."
        ],
        "error_recovery": [
            "If a key is missing from a secondary language catalog, fall back cleanly to the primary English string."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/internationalization`.",
            "cursor": "Select `@internationalization` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `internationalization`.",
            "codex": "Reference `internationalization` in Codex context.",
            "gemini": "Invoke via `gemini run internationalization`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt internationalization`.",
            "windsurf": "Activate `internationalization` in Windsurf."
        },
        "references": [
            "`frontend/src/types/index.ts`",
            "`AGENTS.md` - Section 3 (DOL Date Conversion)"
        ]
    }
]

