"""
Category H: Documentation & Knowledge
Contains 11 comprehensive skills for README maintenance, API/DB/Architecture docs,
developer onboarding, project booklets, lessons learned, and documentation synchronization.
"""

SKILLS_H = [
    {
        "name": "readme-generation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Maintain and enhance the authoritative single-source README.md master booklet without losing existing operational details.",
        "purpose": "Governs the maintenance and continuous synchronization of `README.md`, ensuring it serves as an exhaustive, single-source booklet covering architecture, directory layout, business rules, API endpoints, setup, and testing.",
        "when_to_use": [
            "Adding new API endpoints, scripts, environment variables, or frontend routes.",
            "Updating repository directory layout or test command documentation."
        ],
        "when_not_to_use": [
            "Replacing a comprehensive README with a simplified summary (STRICTLY PROHIBITED)."
        ],
        "required_inputs": [
            "Current `README.md` (136+ KB), recent code changes, and new features."
        ],
        "prerequisites": [
            "Thorough review of existing `README.md` structure to preserve all sections."
        ],
        "procedure": [
            ("Existing Content Audit", "Read existing `README.md` fully. Identify all existing sections: Identity, Architecture, Directory Tree, Business Rules, API Table, UI Routes, Test Suite, Power Automate Parity."),
            ("Change Integration", "Insert new information into the exact matching section without deleting or condensing surrounding details."),
            ("Directory Tree Synchronization", "Update ASCII directory tree representation to reflect newly added directories or files."),
            ("API & Route Table Updates", "Add new API endpoints and Next.js frontend routes to their respective tables."),
            ("Test Command & Pass Rate Update", "Update test suite statistics (e.g. 556 passing tests across 67 suites)."),
            ("Formatting & Link Verification", "Verify all markdown tables, code blocks, and internal anchor links render cleanly.")
        ],
        "safety": [
            "CRITICAL NON-NEGOTIABLE: NEVER replace a comprehensive `README.md` with a simplified or abbreviated version.",
            "Preserve all existing historical context, Power Automate V4 behavioral mappings, and business rules."
        ],
        "deliverables": [
            "Synchronized, comprehensive `README.md` master booklet."
        ],
        "acceptance_criteria": [
            "`README.md` remains an exhaustive, book-length reference document.",
            "All new endpoints, routes, scripts, and skills are accurately documented.",
            "Zero pre-existing sections or operational guides are lost."
        ],
        "error_recovery": [
            "If `README.md` is accidentally truncated, immediately restore from git and re-apply changes incrementally."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/readme-generation`.",
            "cursor": "Select `@readme-generation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `readme-generation`.",
            "codex": "Reference `readme-generation` in Codex context.",
            "gemini": "Invoke via `gemini run readme-generation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt readme-generation`.",
            "windsurf": "Activate `readme-generation` in Windsurf."
        },
        "references": [
            "`README.md` - Master Architectural Booklet",
            "`AGENTS.md` - Section 8 (MUST DO: Maintain README.md)"
        ]
    },
    {
        "name": "technical-documentation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Author comprehensive subsystem guides, architectural deep-dives, and technical specifications in docs/.",
        "purpose": "Creates clear, rigorous technical reference manuals detailing subsystem architectures, operational runbooks, and protocol specifications.",
        "when_to_use": [
            "Documenting a major subsystem (e.g. Proxy Network, Task Queue, Storage & Exports).",
            "Authoring technical specifications for newly implemented features."
        ],
        "when_not_to_use": [
            "Writing quick inline code comments."
        ],
        "required_inputs": [
            "Subsystem implementation details, architecture diagrams, and operational procedures."
        ],
        "prerequisites": [
            "Complete code-level understanding of the target subsystem."
        ],
        "procedure": [
            ("Structure & Scope Definition", "Define document scope in `docs/<SUBSYSTEM>_GUIDE.md`. Establish sections: Overview, Architecture, Data Contracts, Configuration, Error Recovery, and Verification."),
            ("Diagram Generation", "Create Mermaid diagrams visualizing data flow, state transitions, or component interactions."),
            ("Code Snippet & Contract Embedding", "Embed concrete, copy-pasteable code examples, API requests, and configuration JSON schemas."),
            ("Operational Runbook Procedures", "Detail step-by-step procedures for operators: troubleshooting, clearing queues, rotating proxies, or repairing stuck claims."),
            ("Review & Linkage", "Cross-reference new guide in `README.md` and `AGENTS.md`.")
        ],
        "safety": [
            "Save all long-form technical guides in `docs/` (never loose in the root directory).",
            "Mask all credentials, passwords, and API keys in documentation examples."
        ],
        "deliverables": [
            "Authoritative Subsystem Guide in `docs/`.",
            "Mermaid architectural diagrams and operational runbooks."
        ],
        "acceptance_criteria": [
            "Guide provides complete, standalone reference for the subsystem.",
            "All commands and code snippets are accurate and tested.",
            "Document is linked from `README.md` table of contents."
        ],
        "error_recovery": [
            "If technical details diverge from implementation, review code AST and update documentation to match reality."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/technical-documentation`.",
            "cursor": "Select `@technical-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `technical-documentation`.",
            "codex": "Reference `technical-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run technical-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt technical-documentation`.",
            "windsurf": "Activate `technical-documentation` in Windsurf."
        },
        "references": [
            "`docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`",
            "`docs/COURT_PORTALS_GUIDE.md`"
        ]
    },
    {
        "name": "api-documentation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Document REST endpoints, OpenAPI schemas, query parameters, authentication, and curl/Python invocation examples.",
        "purpose": "Maintains exhaustive, developer-friendly REST API documentation, including OpenAPI schema descriptions, request/response examples, status codes, and curl snippets.",
        "when_to_use": [
            "Exposing new REST endpoints or modifying request/response schemas in `app/api/v1/endpoints/`.",
            "Updating API reference guides (`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`)."
        ],
        "when_not_to_use": [
            "Internal helper functions not exposed over HTTP."
        ],
        "required_inputs": [
            "FastAPI endpoint definitions, Pydantic schemas, and HTTP method parameters."
        ],
        "prerequisites": [
            "FastAPI OpenAPI generator active."
        ],
        "procedure": [
            ("Pydantic Schema Documentation", "Add `Field(description=..., examples=[...])` annotations to all request and response schemas in `app/schemas/`."),
            ("FastAPI Route Docstrings", "Add comprehensive docstrings to route functions with markdown summaries and status code descriptions."),
            ("API Guide Documentation", "Document endpoint in `docs/APIS_AND_MATCHING_ENGINE_GUIDE.md` with curl example, Python `httpx` example, and JSON response payload."),
            ("OpenAPI Spec Generation & Validation", "Verify `/docs` (Swagger UI) and `/openapi.json` render accurately without schema warnings."),
            ("API Table Synchronization", "Update API Summary table in `AGENTS.md` and `README.md`.")
        ],
        "safety": [
            "Never expose internal database passwords or tokens in API schema examples.",
            "Ensure documented status codes match actual endpoint behavior."
        ],
        "deliverables": [
            "Updated OpenAPI schemas and Swagger documentation.",
            "Exhaustive REST API guide in `docs/`."
        ],
        "acceptance_criteria": [
            "All endpoints have complete descriptions, request bodies, and typed responses in OpenAPI.",
            "Curl and Python invocation examples are tested and verified.",
            "`AGENTS.md` API summary table is fully synchronized."
        ],
        "error_recovery": [
            "If Swagger UI fails to render schema, inspect Pydantic models for cyclic references or invalid types."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/api-documentation`.",
            "cursor": "Select `@api-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `api-documentation`.",
            "codex": "Reference `api-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run api-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt api-documentation`.",
            "windsurf": "Activate `api-documentation` in Windsurf."
        },
        "references": [
            "`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`",
            "`AGENTS.md` - Section 5 (API Endpoints Summary)"
        ]
    },
    {
        "name": "database-documentation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Document relational schemas, table relationships, foreign key cascades, column data types, and index strategies.",
        "purpose": "Maintains an authoritative, visual, and textual specification of all database entities, relationships, constraints, indexes, and storage keys.",
        "when_to_use": [
            "Adding or altering SQLAlchemy models in `app/models/`.",
            "Documenting database storage keys (`fl_jsonbody_*`, `te_jsonbody_*`)."
        ],
        "when_not_to_use": [
            "Frontend-only component documentation."
        ],
        "required_inputs": [
            "SQLAlchemy declarative models in `app/models/`."
        ],
        "prerequisites": [
            "Complete schema definitions."
        ],
        "procedure": [
            ("Table & Column Inventory", "Catalogue all tables (`claims`, `court_cases`, `match_results`, `audit_logs`, `error_screenshots`, `system_settings`, `notifications`)."),
            ("Data Types & Constraints Table", "Document every column: Name, Type, Nullable, Primary Key, Foreign Key, Default, and Business Purpose."),
            ("Mermaid ERD Generation", "Generate comprehensive Entity-Relationship Diagram (`erDiagram`) detailing 1-to-Many and Many-to-Many relationships."),
            ("Storage Key Documentation", "Document exact JSON storage keys in `ClaimRecord` (`fl_jsonbody_broward`, `fl_jsonbody_hillsborough`, `fl_jsonbody_miami`, `te_jsonbody_*`)."),
            ("Documentation Publication", "Publish in `docs/STORAGE_AND_EXPORTS_GUIDE.md` and link from `README.md`.")
        ],
        "safety": [
            "Never document hypothetical tables; reflect actual SQLAlchemy models and database schema.",
            "Highlight strict constraints (e.g. no `CaseType` for Harris JP/Clerk)."
        ],
        "deliverables": [
            "Comprehensive Database Schema Specification.",
            "Mermaid Entity-Relationship Diagram."
        ],
        "acceptance_criteria": [
            "100% of tables and columns are documented with exact data types.",
            "Foreign key cascading behaviors are explicitly documented.",
            "Database storage keys match `AGENTS.md` Section 4."
        ],
        "error_recovery": [
            "If schema drift occurs, run database introspection to synchronize documentation with live SQLite/PG tables."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/database-documentation`.",
            "cursor": "Select `@database-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `database-documentation`.",
            "codex": "Reference `database-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run database-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt database-documentation`.",
            "windsurf": "Activate `database-documentation` in Windsurf."
        },
        "references": [
            "`docs/STORAGE_AND_EXPORTS_GUIDE.md`",
            "`AGENTS.md` - Section 4 (Database Storage Keys)"
        ]
    },
    {
        "name": "architecture-documentation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Document system blueprints, Celery queue topologies, scraper pipelines, and multi-tier deployment architectures.",
        "purpose": "Creates and maintains holistic architectural blueprints illustrating system tiers, communication protocols, worker concurrency, and external boundary integrations.",
        "when_to_use": [
            "Updating high-level system diagrams in `README.md` or `docs/`.",
            "Documenting architectural refactoring or newly introduced microservices."
        ],
        "when_not_to_use": [
            "Low-level bug fix explanations."
        ],
        "required_inputs": [
            "Repository topology, service definitions, network port bindings, and queue configurations."
        ],
        "prerequisites": [
            "Completed `architecture-analysis`."
        ],
        "procedure": [
            ("Multi-Tier Blueprint Authoring", "Document physical and logical tiers: Frontend (Next.js), Backend API (FastAPI), Message Broker (Redis), Asynchronous Workers (Celery), Database (SQLite/PostgreSQL), Automation (Playwright/Chrome)."),
            ("Mermaid Architecture Diagram", "Create top-level architectural diagram using `flowchart TD` illustrating dataflow between all services."),
            ("Celery Queue Topology", "Document dedicated queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`) and routing logic."),
            ("External Integration Boundaries", "Detail boundary interfaces with court portals, AntiCaptcha extension, and Guidewire Insurance Cloud."),
            ("Archival & Linkage", "Publish in `README.md` and `docs/`.")
        ],
        "safety": [
            "Never expose internal private IP addresses or production credentials in diagrams.",
            "Ensure diagrams adhere to supported Mermaid syntax."
        ],
        "deliverables": [
            "High-Level Architecture Blueprint in `README.md`.",
            "Mermaid system architecture and queue topology diagrams."
        ],
        "acceptance_criteria": [
            "All services, ports, and protocols are documented accurately.",
            "Queue topology illustrates all Celery queues and worker bindings.",
            "Mermaid diagrams render without syntax errors."
        ],
        "error_recovery": [
            "If Mermaid syntax fails to render, quote node labels containing parentheses or brackets."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/architecture-documentation`.",
            "cursor": "Select `@architecture-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `architecture-documentation`.",
            "codex": "Reference `architecture-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run architecture-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt architecture-documentation`.",
            "windsurf": "Activate `architecture-documentation` in Windsurf."
        },
        "references": [
            "`README.md` - Full Architecture Blueprint",
            "`docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`"
        ]
    },
    {
        "name": "deployment-documentation",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Document repeatable local setup, Docker deployment, and production hosting instructions step-by-step.",
        "purpose": "Maintains comprehensive, copy-pasteable deployment guides covering Windows local development (`setup_local.ps1`), Docker container orchestration, and cloud hosting.",
        "when_to_use": [
            "Updating deployment guides (`DEPLOYMENT.md`, `DEPLOYMENT_AND_HOSTING_GUIDE.md`).",
            "Changing port configurations, environment variables, or container definitions."
        ],
        "when_not_to_use": [
            "Daily coding."
        ],
        "required_inputs": [
            "Deployment scripts (`setup_local.ps1`, `docker-compose.yml`), environment prerequisites, and hosting configurations."
        ],
        "prerequisites": [
            "Verified working deployment on local and containerized environments."
        ],
        "procedure": [
            ("Local Windows Setup Instructions", "Document exact PowerShell commands for cloning, virtualenv setup, dependency installation, and running `setup_local.ps1`."),
            ("Docker Deployment Instructions", "Document `docker compose up -d` workflow, volume mappings, and container health check verification."),
            ("Production Hosting Architecture", "Document production Linux hosting: Nginx reverse proxy, systemd service units, SSL certificates, and PostgreSQL migration."),
            ("Troubleshooting Section", "Provide actionable troubleshooting guidance for port collisions, permission errors, and container crashes."),
            ("Review & Sync", "Reconcile `DEPLOYMENT.md` with `README.md`.")
        ],
        "safety": [
            "Test every documented command on a fresh workstation to confirm copy-paste accuracy.",
            "Never include production API keys or database passwords in deployment guides."
        ],
        "deliverables": [
            "Updated `DEPLOYMENT.md` and `DEPLOYMENT_AND_HOSTING_GUIDE.md`.",
            "Verified setup runbooks."
        ],
        "acceptance_criteria": [
            "Step-by-step commands allow a new developer to bring up the stack within 15 minutes.",
            "Local, Docker, and Production hosting modes are thoroughly covered.",
            "Troubleshooting section resolves common port and permission issues."
        ],
        "error_recovery": [
            "If a command fails on a clean machine, revise the script or document missing prerequisites."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/deployment-documentation`.",
            "cursor": "Select `@deployment-documentation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `deployment-documentation`.",
            "codex": "Reference `deployment-documentation` in Codex context.",
            "gemini": "Invoke via `gemini run deployment-documentation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt deployment-documentation`.",
            "windsurf": "Activate `deployment-documentation` in Windsurf."
        },
        "references": [
            "`DEPLOYMENT.md`",
            "`DEPLOYMENT_AND_HOSTING_GUIDE.md`"
        ]
    },
    {
        "name": "developer-onboarding",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Create a practical, streamlined onboarding path for new developers with prerequisites and initial verification tests.",
        "purpose": "Provides a comprehensive, friction-free onboarding guide enabling new software engineers to clone the repository, install dependencies, launch services, and run their first green test pass within 15 minutes.",
        "when_to_use": [
            "Onboarding new team members or AI coding agents.",
            "Re-verifying workstation setup prerequisites after major dependency upgrades."
        ],
        "when_not_to_use": [
            "Advanced production operations."
        ],
        "required_inputs": [
            "Workstation prerequisites (Python 3.14.7, Node.js 18+, Redis, Git, Chrome) and repo setup commands."
        ],
        "prerequisites": [
            "Working local development environment."
        ],
        "procedure": [
            ("Prerequisites Checklist", "Enumerate required tooling with download links and exact verified versions: Python 3.14.7, Node 18+, Git, Redis for Windows, Google Chrome."),
            ("Step-by-Step Repository Setup", "Provide ordered shell commands: clone repository, run virtualenv setup, install pip requirements, install npm packages, and install Playwright Chromium."),
            ("First Green Test Pass", "Instruct developer to run `backend\\.venv\\Scripts\\pytest -q` to confirm all 556 tests pass out of the box."),
            ("Local Service Launch", "Instruct developer to execute `setup_local.ps1` and verify UI opens at `http://localhost:3000`."),
            ("Key Architectural Pointers", "Highlight critical files to read first: `AGENTS.md`, `README.md`, `backend/app/main.py`, and `frontend/src/app/page.tsx`."),
            ("Publish Onboarding Manual", "Publish in `docs/DEVELOPMENT_WORKFLOW.md`.")
        ],
        "safety": [
            "Ensure onboarding steps do not require administrator privileges where avoidable.",
            "Never instruct developers to edit `.env` with live production secrets."
        ],
        "deliverables": [
            "Streamlined Developer Onboarding Guide in `docs/DEVELOPMENT_WORKFLOW.md`.",
            "Prerequisite verification script."
        ],
        "acceptance_criteria": [
            "A new developer can set up and run the full stack within 15 minutes.",
            "First test pass executes cleanly with 556 passing tests.",
            "Core architectural rules and conventions are clearly communicated."
        ],
        "error_recovery": [
            "If new developers encounter Windows execution policy blocks, include `-ExecutionPolicy Bypass` in launcher instructions."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/developer-onboarding`.",
            "cursor": "Select `@developer-onboarding` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `developer-onboarding`.",
            "codex": "Reference `developer-onboarding` in Codex context.",
            "gemini": "Invoke via `gemini run developer-onboarding`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt developer-onboarding`.",
            "windsurf": "Activate `developer-onboarding` in Windsurf."
        },
        "references": [
            "`docs/DEVELOPMENT_WORKFLOW.md`",
            "`AGENTS.md` - Section 2 (Repository Layout)"
        ]
    },
    {
        "name": "project-booklet",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Create and maintain complete, book-length project reference booklets synthesizing all operational and engineering knowledge.",
        "purpose": "Consolidates all architectural blueprints, API catalogs, operational runbooks, database schemas, and court portal scraping guides into a comprehensive, single-volume reference booklet.",
        "when_to_use": [
            "Preparing client handover documentation packages.",
            "Synthesizing major platform revisions into an authoritative book-length manual."
        ],
        "when_not_to_use": [
            "Minor isolated code fixes."
        ],
        "required_inputs": [
            "All subsystem guides in `docs/`, `README.md`, `AGENTS.md`, and test verification records."
        ],
        "prerequisites": [
            "Complete platform stability."
        ],
        "procedure": [
            ("Booklet Table of Contents Formulation", "Organize chapters: 1. Executive Summary, 2. Platform Architecture, 3. Repository Layout, 4. Business Rules & Deduplication, 5. The 8 Court Portals, 6. API Reference, 7. Database Schemas, 8. Operator Manual, 9. Deployment & DevOps, 10. AI Governance & Skills."),
            ("Content Synthesis & Chapter Integration", "Synthesize detailed subsystem guides into coherent chapters with consistent voice, formatting, and high-resolution diagrams."),
            ("Visual Evidence Embedding", "Embed verified screenshots and diagrams illustrating every frontend route and scraper workflow."),
            ("Cross-Reference Validation", "Verify all internal chapter links, code references, and tables of contents."),
            ("Publication & Archival", "Publish the Master Project Booklet in `README.md` or dedicated `docs/PROJECT_BOOKLET.md`.")
        ],
        "safety": [
            "Never omit critical operational safeguards or business rules during synthesis.",
            "Ensure booklet is completely self-contained."
        ],
        "deliverables": [
            "Comprehensive, book-length Project Reference Booklet.",
            "Complete chapter index and verified diagram package."
        ],
        "acceptance_criteria": [
            "Booklet covers 100% of platform architecture, operations, and business rules.",
            "All chapters are thoroughly detailed without missing sections or placeholder text.",
            "Embedded diagrams and tables render cleanly."
        ],
        "error_recovery": [
            "If booklet size causes markdown rendering lag, optimize embedded image formats (use WebP or compressed PNG)."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/project-booklet`.",
            "cursor": "Select `@project-booklet` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `project-booklet`.",
            "codex": "Reference `project-booklet` in Codex context.",
            "gemini": "Invoke via `gemini run project-booklet`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt project-booklet`.",
            "windsurf": "Activate `project-booklet` in Windsurf."
        },
        "references": [
            "`README.md` - Master Architectural Booklet",
            "`docs/`"
        ]
    },
    {
        "name": "knowledge-capture",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Capture reusable discoveries, court portal DOM quirks, AntiCaptcha behaviors, and lessons learned into permanent knowledge bases.",
        "purpose": "Extracts non-obvious engineering discoveries (e.g. court portal DOM quirks, Cloudflare Turnstile token thresholds, anti-detection flags) into reusable knowledge assets.",
        "when_to_use": [
            "Discovering undocumented court portal behaviors or DOM idiosyncrasies.",
            "Overcoming complex CAPTCHA, browser automation, or concurrency challenges."
        ],
        "when_not_to_use": [
            "Documenting standard well-known library features."
        ],
        "required_inputs": [
            "Discovery details, reproduction steps, workaround code, and technical explanation."
        ],
        "prerequisites": [
            "Verified solution to a non-obvious problem."
        ],
        "procedure": [
            ("Discovery Context Isolation", "Document the symptom, the unexpected platform behavior, and why standard approaches failed."),
            ("Technical Mechanism Explanation", "Explain the underlying technical mechanism (e.g. Broward County glossary rows having no digits, Turnstile response token length threshold > 20)."),
            ("Reusable Pattern / Recipe Formulation", "Provide the exact, tested code snippet or configuration that resolves the quirk."),
            ("Knowledge Base Archival", "Save to `docs/` or update corresponding subsystem guide (`COURT_PORTALS_GUIDE.md`)."),
            ("Agent Skill Update", "If applicable, incorporate the recipe into the relevant skill runbook (e.g. `fl-broward-workflow`).")
        ],
        "safety": [
            "Never record speculative theories; only record verified, tested discoveries.",
            "Ensure sensitive endpoints or internal IPs are excluded from knowledge notes."
        ],
        "deliverables": [
            "Technical Knowledge Note in `docs/`.",
            "Updated scraper runbook or skill reference."
        ],
        "acceptance_criteria": [
            "Quirk and verified solution are documented with exact code snippets.",
            "Future engineers or AI assistants can reuse the pattern directly.",
            "Cross-referenced in relevant subsystem documentation."
        ],
        "error_recovery": [
            "If an external portal alters its behavior again, update the knowledge note with the new observed behavior and date."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/knowledge-capture`.",
            "cursor": "Select `@knowledge-capture` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `knowledge-capture`.",
            "codex": "Reference `knowledge-capture` in Codex context.",
            "gemini": "Invoke via `gemini run knowledge-capture`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt knowledge-capture`.",
            "windsurf": "Activate `knowledge-capture` in Windsurf."
        },
        "references": [
            "`docs/COURT_PORTALS_GUIDE.md`",
            "`.agents/skills/fl-broward-workflow/SKILL.md`"
        ]
    },
    {
        "name": "learn",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Convert confirmed user corrections, preferences, and architectural rules into permanent project governance guidelines.",
        "purpose": "Persists confirmed user corrections, architectural mandates, and preference decisions into permanent project rules (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`), preventing repeated mistakes across sessions.",
        "when_to_use": [
            "User explicitly corrects an agent mistake or establishes a new project rule.",
            "Responding to `/learn` slash command.",
            "Following successful resolution of a complex architectural decision."
        ],
        "when_not_to_use": [
            "Transient session-specific instructions."
        ],
        "required_inputs": [
            "User correction text, confirmed rule, and target rule files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`)."
        ],
        "prerequisites": [
            "Explicit user confirmation of the rule."
        ],
        "procedure": [
            ("Correction & Rule Analysis", "Analyze the user correction. Extract the underlying rule and scope of applicability."),
            ("Rule Formulation", "Draft a concise, unambiguous rule statement with explicit DO and DON'T examples."),
            ("Permanent Rule File Update", "Add the rule to `AGENTS.md` (Section 8), `GEMINI.md`, `CLAUDE.md`, and `.cursorrules`."),
            ("Deduplication & Conflict Check", "Ensure the new rule does not contradict existing governance guidelines."),
            ("User Confirmation", "Confirm to the user that the lesson has been codified into permanent project memory.")
        ],
        "safety": [
            "Never encode rules that violate core safety invariants (data loss prevention, security).",
            "Keep global rule files concise; place lengthy procedures into dedicated skills."
        ],
        "deliverables": [
            "Updated rule files (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`, `.cursorrules`).",
            "Confirmation summary to the user."
        ],
        "acceptance_criteria": [
            "Confirmed rule is persisted across all primary AI rule files.",
            "Rule phrasing is unambiguous, testable, and actionable.",
            "No conflicting rules exist in project memory."
        ],
        "error_recovery": [
            "If user refines or withdraws a rule later, update rule files immediately to reflect the revised directive."
        ],
        "tool_invocations": {
            "antigravity": "Invoke native slash command `/learn` or ask agent to learn this rule.",
            "cursor": "Select `@learn` in Cursor chat.",
            "claude_code": "Prompt Claude Code: 'Update CLAUDE.md with this confirmed lesson.'",
            "codex": "Reference `learn` workflow in Codex context.",
            "gemini": "Invoke via `gemini run learn`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt learn`.",
            "windsurf": "Activate `learn` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)",
            "`CLAUDE.md`",
            "`GEMINI.md`"
        ]
    },
    {
        "name": "documentation-sync",
        "category_code": "H",
        "category_name": "Documentation & Knowledge",
        "description": "Audit and synchronize documentation across README.md, docs/, and AGENTS.md automatically following code modifications.",
        "purpose": "Guarantees that project documentation never desynchronizes from codebase reality, updating API catalogs, schemas, endpoints, and test commands whenever code changes.",
        "when_to_use": [
            "Following ANY implementation task that touches APIs, routes, models, or configuration.",
            "Pre-release documentation synchronization passes."
        ],
        "when_not_to_use": [
            "Pure documentation edits."
        ],
        "required_inputs": [
            "List of modified code files, new endpoints, and existing documentation."
        ],
        "prerequisites": [
            "Passing test suite baseline."
        ],
        "procedure": [
            ("Code Diff Review", "Inspect all modified files in git working tree. Identify new routes, modified models, new settings, or changed scripts."),
            ("README.md Synchronization", "Update `README.md` tables, directory tree, and test metrics to reflect changes."),
            ("AGENTS.md Synchronization", "Update `AGENTS.md` API endpoints summary (Section 5) and frontend routes (Section 6)."),
            ("Subsystem Guide Updates", "Update corresponding guides in `docs/` (e.g. `COURT_PORTALS_GUIDE.md` for scraper changes)."),
            ("Verification Pass", "Verify all updated markdown files render cleanly without broken links or formatting defects.")
        ],
        "safety": [
            "Never delete existing documentation sections during a sync pass.",
            "Ensure all documented commands and file paths are verified against reality."
        ],
        "deliverables": [
            "Fully synchronized `README.md`, `AGENTS.md`, and subsystem guides in `docs/`."
        ],
        "acceptance_criteria": [
            "100% of newly added endpoints, routes, and scripts are documented.",
            "Test pass rates and suite counts reflect current reality.",
            "Zero documentation drift exists between code and docs."
        ],
        "error_recovery": [
            "If git diff shows accidental documentation deletions, restore deleted blocks from git history."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/documentation-sync`.",
            "cursor": "Select `@documentation-sync` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `documentation-sync`.",
            "codex": "Reference `documentation-sync` in Codex context.",
            "gemini": "Invoke via `gemini run documentation-sync`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt documentation-sync`.",
            "windsurf": "Activate `documentation-sync` in Windsurf."
        },
        "references": [
            "`README.md`",
            "`AGENTS.md`"
        ]
    }
]

