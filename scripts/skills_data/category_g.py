"""
Category G: Deployment & DevOps
Contains 14 comprehensive skills for environment setup, local launchers,
Docker containerization, CI/CD pipelines, production deployment, rollback, and monitoring.
"""

SKILLS_G = [
    {
        "name": "environment-setup",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Prepare documented development, test, and production-like environments with reproducible runtime dependencies.",
        "purpose": "Guides the provisioning of clean, reproducible Python 3.14.7 virtual environments, Node.js runtimes, Redis brokers, and Playwright browser binaries across host systems.",
        "when_to_use": [
            "Setting up a new development workstation or CI runner.",
            "Re-provisioning corrupted Python virtual environments or Node modules."
        ],
        "when_not_to_use": [
            "Day-to-day code editing."
        ],
        "required_inputs": [
            "Installed Python 3.14.7, Node.js 18+, Redis, and repository source code."
        ],
        "prerequisites": [
            "Operating system administrative privileges to install runtimes and browser drivers."
        ],
        "procedure": [
            ("Python Runtime & Virtualenv Setup", "Verify Python 3.14.7. Create virtualenv: `python -m venv backend/.venv`. Upgrade pip: `.venv\\Scripts\\python -m pip install --upgrade pip`."),
            ("Backend Dependency Installation", "Install pinned backend dependencies: `.venv\\Scripts\\pip install -r backend/requirements.txt`."),
            ("Playwright Chromium Installation", "Install Playwright browser binaries: `.venv\\Scripts\\playwright install chromium`."),
            ("Frontend Node Module Setup", "Install frontend packages: `cd frontend && npm install`."),
            ("Environment Variable Initialization", "Copy `.env.example` to `backend/.env` and `frontend/.env.local` if missing. Configure absolute database path and Redis URL."),
            ("Health Check Pass", "Run `scripts/check_ps1_syntax.ps1` and test suite to confirm operational readiness.")
        ],
        "safety": [
            "CRITICAL: Pin Python strictly to 3.14.7; avoid untested Python 3.15 alphas.",
            "Never commit active `.env` files containing live credentials."
        ],
        "deliverables": [
            "Fully provisioned, healthy local development environment.",
            "Environment readiness verification log."
        ],
        "acceptance_criteria": [
            "Python 3.14.7 virtualenv runs `pytest` cleanly.",
            "Frontend `npm run build` succeeds.",
            "Redis broker is reachable on port 6379."
        ],
        "error_recovery": [
            "If virtualenv becomes corrupted, delete `backend/.venv` and recreate from scratch."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/environment-setup`.",
            "cursor": "Select `@environment-setup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `environment-setup`.",
            "codex": "Reference `environment-setup` in Codex context.",
            "gemini": "Invoke via `gemini run environment-setup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt environment-setup`.",
            "windsurf": "Activate `environment-setup` in Windsurf."
        },
        "references": [
            "`backend/requirements.txt`",
            "`frontend/package.json`",
            "`setup_local.ps1`"
        ]
    },
    {
        "name": "local-setup",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Validate local prerequisites, startup commands, persistent launcher scripts (setup_local.ps1), and health checks.",
        "purpose": "Maintains and executes the unified local launcher script (`setup_local.ps1`), launching FastAPI, Next.js, Redis, and Celery workers in coordinated, persistent terminal windows.",
        "when_to_use": [
            "Starting up the local development stack for daily development.",
            "Updating launcher configuration or troubleshooting process startup failures."
        ],
        "when_not_to_use": [
            "Deploying to production Linux servers (use `docker-setup` or `production-deployment`)."
        ],
        "required_inputs": [
            "`setup_local.ps1`, installed dependencies, and port availability."
        ],
        "prerequisites": [
            "Completed `environment-setup`."
        ],
        "procedure": [
            ("Port Availability Pre-Flight Check", "Verify ports 8000 (FastAPI), 3000 (Next.js), and 6379 (Redis) are free from stale orphan processes."),
            ("Launcher Syntax Validation", "Run `scripts/check_ps1_syntax.ps1` to confirm `setup_local.ps1` syntax is 100% valid."),
            ("Persistent Stack Startup", "Execute `powershell -ExecutionPolicy Bypass -File setup_local.ps1`. Verify interactive terminal remains persistent and does NOT auto-exit."),
            ("Component Health Check Verification", "Wait for services to initialize. Query `http://localhost:8000/api/v1/health` and `http://localhost:3000`."),
            ("Celery Worker Registration Audit", "Verify that Celery workers register all queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`)."),
            ("Startup Summary Output", "Display URLs for Dashboard (3000), API Swagger Docs (8000/docs), and Health Check.")
        ],
        "safety": [
            "CRITICAL: PowerShell launcher must NEVER auto-exit after launching services; it must remain persistent and interactive.",
            "Ensure launcher gracefully terminates child processes on Ctrl+C."
        ],
        "deliverables": [
            "Active local running stack across all tiers.",
            "Verified health check response from all services."
        ],
        "acceptance_criteria": [
            "`setup_local.ps1` executes without errors and stays open.",
            "Both frontend (3000) and backend (8000) respond with HTTP 200.",
            "Celery workers actively consume tasks from Redis."
        ],
        "error_recovery": [
            "If launcher exits immediately, run `scripts/clean_stale_workers.py` to kill port collisions and retry."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/local-setup`.",
            "cursor": "Select `@local-setup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `local-setup`.",
            "codex": "Reference `local-setup` in Codex context.",
            "gemini": "Invoke via `gemini run local-setup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt local-setup`.",
            "windsurf": "Activate `local-setup` in Windsurf."
        },
        "references": [
            "`setup_local.ps1`",
            "`AGENTS.md` - Section 8 (Must Do)"
        ]
    },
    {
        "name": "docker-setup",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Create, repair, and orchestrate containerized environments using docker-compose.yml, volume mounts, and health checks.",
        "purpose": "Manages full-stack containerization via Docker and Docker Compose, configuring isolated containers for Backend, Celery Workers, Frontend, Redis, and PostgreSQL with persistent volumes.",
        "when_to_use": [
            "Deploying the platform via Docker containers.",
            "Troubleshooting container networking, volume mounts, or health check failures."
        ],
        "when_not_to_use": [
            "Attended GUI browser scraping requiring local Windows Chrome desktop sessions."
        ],
        "required_inputs": [
            "`docker-compose.yml`, Dockerfiles, and environment variables."
        ],
        "prerequisites": [
            "Docker Desktop or Docker Engine installed and running."
        ],
        "procedure": [
            ("Configuration Audit", "Inspect `docker-compose.yml`. Verify service definitions: `backend`, `frontend`, `redis`, `celery_worker`."),
            ("Volume & Network Configuration", "Configure persistent named volumes for database data, uploads (`uploads/`), and exports (`exports/`). Ensure shared bridge network."),
            ("Container Build Pass", "Build images using `docker compose build --no-cache` to ensure clean package resolution."),
            ("Container Startup", "Start container stack: `docker compose up -d`."),
            ("Health Check Probing", "Monitor container health status (`docker compose ps`). Verify each service transitions from starting to healthy."),
            ("Log Telemetry Inspection", "Inspect combined container logs (`docker compose logs -f --tail=100`) for startup warnings or database connection errors.")
        ],
        "safety": [
            "Ensure container volumes map to persistent storage so database state is not lost upon container destruction.",
            "Do not expose Redis or database ports directly to public untrusted networks without authentication."
        ],
        "deliverables": [
            "Production-ready `docker-compose.yml` and Dockerfiles.",
            "Healthy, running container stack."
        ],
        "acceptance_criteria": [
            "All services (`backend`, `frontend`, `redis`, `celery_worker`) report healthy status.",
            "Frontend at `http://localhost:3000` successfully queries backend via internal Docker network.",
            "Container restarts preserve database records."
        ],
        "error_recovery": [
            "If backend fails to connect to Redis, verify container service name matches `REDIS_URL` hostname."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/docker-setup`.",
            "cursor": "Select `@docker-setup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `docker-setup`.",
            "codex": "Reference `docker-setup` in Codex context.",
            "gemini": "Invoke via `gemini run docker-setup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt docker-setup`.",
            "windsurf": "Activate `docker-setup` in Windsurf."
        },
        "references": [
            "`docker-compose.yml`",
            "`DEPLOYMENT_AND_HOSTING_GUIDE.md`"
        ]
    },
    {
        "name": "ci-cd-setup",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Configure automated quality gates, linting, type-checking, and test pipelines in GitHub Actions.",
        "purpose": "Maintains continuous integration workflows (`.github/workflows/ci.yml`), enforcing automated verification on every push and pull request before code can be merged.",
        "when_to_use": [
            "Authoring or updating GitHub Actions CI pipelines.",
            "Adding automated security scanning, linting, or E2E test jobs to CI."
        ],
        "when_not_to_use": [
            "Local test execution."
        ],
        "required_inputs": [
            "GitHub Actions workflow files in `.github/workflows/`."
        ],
        "prerequisites": [
            "Git repository connected to GitHub."
        ],
        "procedure": [
            ("Workflow Trigger Configuration", "Configure triggers: `on: [push, pull_request]` targeting `main` branch."),
            ("Matrix & Environment Setup", "Set up matrix runner with Python 3.14 and Node 18+ on `ubuntu-latest` or `windows-latest`."),
            ("Backend Quality Jobs", "Configure steps: Install dependencies, run `ruff check`, execute `pytest` unit & integration test suites."),
            ("Frontend Quality Jobs", "Configure steps: `npm ci`, run `npx tsc --noEmit`, run `npm run lint`, and test `npm run build`."),
            ("Artifact & Report Archival", "Upload test coverage reports, failure logs, and lint summaries as workflow artifacts."),
            ("Local Workflow Validation", "Validate YAML syntax using schema linters or local runner (`act`).")
        ],
        "safety": [
            "Never put unmasked secrets or production credentials in CI workflow files (use GitHub Repository Secrets).",
            "Do not allow PRs to merge with failing CI gates."
        ],
        "deliverables": [
            "Hardened GitHub Actions CI pipeline in `.github/workflows/ci.yml`.",
            "Verified passing CI run status."
        ],
        "acceptance_criteria": [
            "CI pipeline executes automatically on push and pull requests.",
            "Linting, TypeScript compilation, and pytest pass cleanly.",
            "Failing tests correctly block PR merging."
        ],
        "error_recovery": [
            "If CI fails due to dependency caching corruption, add cache busting keys to workflow actions."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/ci-cd-setup`.",
            "cursor": "Select `@ci-cd-setup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `ci-cd-setup`.",
            "codex": "Reference `ci-cd-setup` in Codex context.",
            "gemini": "Invoke via `gemini run ci-cd-setup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt ci-cd-setup`.",
            "windsurf": "Activate `ci-cd-setup` in Windsurf."
        },
        "references": [
            "`.github/workflows/ci.yml`",
            "`Deploy-To-GitHub.ps1`"
        ]
    },
    {
        "name": "deployment-planning",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Define pre-release checklists, downtime requirements, stakeholder sign-offs, and step-by-step rollback procedures.",
        "purpose": "Authors comprehensive, risk-managed deployment plans detailing change windows, prerequisite backups, deployment sequencing, verification smoke tests, and rollback triggers.",
        "when_to_use": [
            "Preparing major production releases, database schema migrations, or infrastructure cutovers.",
            "Coordinating scheduled release windows with business operators."
        ],
        "when_not_to_use": [
            "Routine local development builds."
        ],
        "required_inputs": [
            "Release scope, database migrations, affected services, and target deployment date/time."
        ],
        "prerequisites": [
            "All release candidate code merged and verified by CI."
        ],
        "procedure": [
            ("Release Scope & Window Definition", "Define release version, scheduled change window, expected downtime (if any), and release coordinator."),
            ("Pre-Deployment Checklist", "Specify mandatory pre-flight checks: verified database backup, active queue drained, secret keys verified, and rollback branch tagged."),
            ("Sequential Deployment Steps", "Enumerate ordered deployment commands: maintenance banner on -> stop worker -> migrate database -> start backend -> deploy frontend -> restart worker -> maintenance banner off."),
            ("Smoke Test & Verification Protocol", "Define explicit post-deployment tests: `/health` detailed check, single portal ping, and live test claim execution."),
            ("Rollback Triggers & Protocol", "Specify exact failure conditions that trigger immediate rollback (e.g. database migration failure, > 5% error rate on health checks) and step-by-step rollback commands."),
            ("Plan Publication & Sign-Off", "Publish Deployment Plan in `docs/` and obtain stakeholder sign-off.")
        ],
        "safety": [
            "CRITICAL: Never execute a production deployment without a verified, pre-tested rollback procedure.",
            "Ensure release windows minimize disruption to operational claim discovery."
        ],
        "deliverables": [
            "Formal Deployment Plan Document (`docs/YYYY-MM-DD_deployment_plan_v<N>.md`).",
            "Signed pre-deployment checklist."
        ],
        "acceptance_criteria": [
            "Deployment plan details exact commands, owners, and time estimates.",
            "Rollback procedure is verified and documented.",
            "Smoke test protocol covers all critical business paths."
        ],
        "error_recovery": [
            "If sign-off conditions are not met, postpone the release window until blockers are resolved."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/deployment-planning`.",
            "cursor": "Select `@deployment-planning` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `deployment-planning`.",
            "codex": "Reference `deployment-planning` in Codex context.",
            "gemini": "Invoke via `gemini run deployment-planning`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt deployment-planning`.",
            "windsurf": "Activate `deployment-planning` in Windsurf."
        },
        "references": [
            "`DEPLOYMENT.md`",
            "`DEPLOYMENT_AND_HOSTING_GUIDE.md`"
        ]
    },
    {
        "name": "production-deployment",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Execute controlled production deployments with mandatory backups, health verification, and rollback safeguards.",
        "purpose": "Guides the live execution of an approved deployment plan, applying code updates, running database migrations, recycling containers, and validating production health.",
        "when_to_use": [
            "Executing authorized production software releases during scheduled change windows."
        ],
        "when_not_to_use": [
            "Deploying unapproved, untested code directly to production servers."
        ],
        "required_inputs": [
            "Approved Deployment Plan, release tag, production SSH/terminal access, and backup tools."
        ],
        "prerequisites": [
            "Completed `deployment-planning` and explicit stakeholder sign-off."
        ],
        "procedure": [
            ("Pre-Deployment State & Backup Capture", "Verify queue is drained. Take full database snapshot (`sqlite3 .backup` or `pg_dump`) and archive with release tag."),
            ("Code Pull & Dependency Build", "Fetch approved release git tag. Install locked dependencies and compile frontend production build (`npm run build`)."),
            ("Database Migration Execution", "Execute database migration scripts. Verify schema integrity check passes."),
            ("Service Restart & Worker Recycling", "Restart backend service, Celery workers, and Next.js frontend. Verify process uptime."),
            ("Post-Deployment Smoke Verification", "Execute automated smoke test: check `/api/v1/health/detailed`, verify portal reachability, and monitor error logs."),
            ("Release Sign-Off & Status Finalization", "Confirm successful deployment to stakeholders and archive deployment logs.")
        ],
        "safety": [
            "CRITICAL: Stop deployment and initiate rollback immediately if database migrations fail or error rates spike.",
            "Never bypass pre-deployment database backups."
        ],
        "deliverables": [
            "Deployed production release.",
            "Post-deployment verification log and backup archive."
        ],
        "acceptance_criteria": [
            "Production services running updated release tag.",
            "`/api/v1/health/detailed` reports all 8 components healthy.",
            "Zero elevated error rates in operational logs."
        ],
        "error_recovery": [
            "If any smoke test fails, immediately invoke `rollback-deployment`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/production-deployment`.",
            "cursor": "Select `@production-deployment` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `production-deployment`.",
            "codex": "Reference `production-deployment` in Codex context.",
            "gemini": "Invoke via `gemini run production-deployment`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt production-deployment`.",
            "windsurf": "Activate `production-deployment` in Windsurf."
        },
        "references": [
            "`DEPLOYMENT.md`",
            "`Deploy-To-GitHub.ps1`"
        ]
    },
    {
        "name": "staging-deployment",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Deploy and validate release candidates in staging environments mirroring production configurations.",
        "purpose": "Deploys release candidates to an isolated staging environment to conduct realistic pre-production qualification tests, portal reachability tests, and stakeholder demos.",
        "when_to_use": [
            "Deploying release candidates for quality assurance and operator verification.",
            "Testing database migration rollback procedures on production-like data."
        ],
        "when_not_to_use": [
            "Local dev testing."
        ],
        "required_inputs": [
            "Release candidate branch or tag, staging server credentials, and staging `.env`."
        ],
        "prerequisites": [
            "Configured staging server or staging container cluster."
        ],
        "procedure": [
            ("Staging Environment Preparation", "Ensure staging database is seeded with representative sanitized test claims."),
            ("Release Candidate Deployment", "Deploy release candidate code to staging containers using Docker Compose or CI/CD runner."),
            ("Database Migration Pass", "Run database migrations on staging. Verify schema changes succeed without data corruption."),
            ("Automated Qualification Suite", "Run full Playwright E2E test suite and portal ping probes against staging endpoints."),
            ("Operator Acceptance Testing (UAT)", "Provide staging URL to stakeholders for visual inspection and workflow review."),
            ("Staging Qualification Report", "Publish Staging Qualification Report confirming readiness for production.")
        ],
        "safety": [
            "Ensure staging environment uses isolated mock credentials for external services (Guidewire, SMTP) where appropriate.",
            "Never use unredacted customer PII in staging environments."
        ],
        "deliverables": [
            "Deployed staging environment running release candidate.",
            "Staging Qualification Report with verified test passes."
        ],
        "acceptance_criteria": [
            "All staging services operational and healthy.",
            "Full E2E test suite passes on staging environment.",
            "Operator acceptance sign-off obtained."
        ],
        "error_recovery": [
            "If staging reveals defects, fix issues on branch, rebuild release candidate, and redeploy to staging."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/staging-deployment`.",
            "cursor": "Select `@staging-deployment` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `staging-deployment`.",
            "codex": "Reference `staging-deployment` in Codex context.",
            "gemini": "Invoke via `gemini run staging-deployment`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt staging-deployment`.",
            "windsurf": "Activate `staging-deployment` in Windsurf."
        },
        "references": [
            "`DEPLOYMENT_AND_HOSTING_GUIDE.md`"
        ]
    },
    {
        "name": "environment-configuration",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Manage environment variables, Pydantic settings, secrets masking, and configuration drift securely.",
        "purpose": "Ensures runtime configuration is managed through Pydantic Settings models (`app/core/config.py`) and database-persisted settings (`SystemSettings`), preventing credential leakage and drift.",
        "when_to_use": [
            "Adding new configuration settings (timeouts, thresholds, credentials).",
            "Configuring environment variables across development, test, and production."
        ],
        "when_not_to_use": [
            "Hardcoding credentials directly in source code."
        ],
        "required_inputs": [
            "Configuration requirements, default values, and environment files (`.env`, `.env.example`)."
        ],
        "prerequisites": [
            "Pydantic Settings model architecture."
        ],
        "procedure": [
            ("Pydantic Settings Schema Extension", "Define new setting in `app/core/config.py` with type annotation, default value, and description."),
            ("Database Persistence Model Binding", "If setting is user-configurable at runtime, add field to `SystemSettings` schema in `app/schemas/settings.py`."),
            ("Environment Template Update", "Add documented entry with placeholder value to `.env.example`."),
            ("Secret Masking Implementation", "Ensure sensitive settings (passwords, API keys) are masked with `***` in API responses and logs."),
            ("Worker Synchronization Verification", "Confirm that Celery workers reload updated settings dynamically via `get_system_settings_async()`."),
            ("Configuration Test Pass", "Write pytest test in `tests/test_automation_runtime_settings.py` verifying settings persistence and masking.")
        ],
        "safety": [
            "CRITICAL: Never hardcode passwords, API keys, or database URLs in source code.",
            "Never commit `.env` containing live secrets to git."
        ],
        "deliverables": [
            "Updated `app/core/config.py` and `app/schemas/settings.py`.",
            "Synchronized `.env.example` template.",
            "Automated settings persistence test."
        ],
        "acceptance_criteria": [
            "All settings have default values and validation constraints.",
            "Settings persist to database and reload dynamically at runtime.",
            "All secrets are masked in API outputs."
        ],
        "error_recovery": [
            "If configuration values fail Pydantic validation on startup, check datatype casting and environment variable prefix."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/environment-configuration`.",
            "cursor": "Select `@environment-configuration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `environment-configuration`.",
            "codex": "Reference `environment-configuration` in Codex context.",
            "gemini": "Invoke via `gemini run environment-configuration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt environment-configuration`.",
            "windsurf": "Activate `environment-configuration` in Windsurf."
        },
        "references": [
            "`backend/app/core/config.py`",
            "`backend/app/schemas/settings.py`"
        ]
    },
    {
        "name": "database-backup-restore",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Validate database backup integrity, automated snapshot creation, and deterministic restoration procedures.",
        "purpose": "Establishes reliable, automated database backup procedures and regularly verifies that backups can be restored cleanly with zero data loss.",
        "when_to_use": [
            "Prior to executing major schema migrations or bulk data deletions.",
            "Establishing automated scheduled daily/weekly backup routines.",
            "Testing disaster recovery preparedness."
        ],
        "when_not_to_use": [
            "Routine read-only queries."
        ],
        "required_inputs": [
            "Active database path (`orchestrator.db` or PostgreSQL URL) and backup destination directory."
        ],
        "prerequisites": [
            "Filesystem write access to backup storage."
        ],
        "procedure": [
            ("Online Backup Execution", "For SQLite: execute online vacuum backup `sqlite3 orchestrator.db \".backup 'orchestrator_backup_YYYYMMDD.db'\"` to ensure atomic snapshot without table locking. For PostgreSQL: run `pg_dump`."),
            ("Backup Integrity Verification", "Verify backup file exists, is non-zero in size, and passes `PRAGMA integrity_check;` on SQLite."),
            ("Restoration Simulation on Isolated Target", "Restore backup file to an isolated test directory (`test_restore.db`)."),
            ("Data Fidelity & Count Verification", "Query restored database: compare row counts of `claims`, `court_cases`, `match_results`, and `system_settings` against original database."),
            ("Backup Archival & Retention", "Compress verified backup (`gzip`) and apply retention policy (prune backups older than 30 days)."),
            ("Disaster Recovery Runbook Update", "Document backup location and restoration commands in `docs/STORAGE_AND_EXPORTS_GUIDE.md`.")
        ],
        "safety": [
            "Never copy an active SQLite database file directly while writers are active; always use the SQLite online backup API (`.backup`).",
            "Store backup files on storage physically separate from the active database disk."
        ],
        "deliverables": [
            "Verified, compressed database backup archive.",
            "Restoration verification report confirming row count parity."
        ],
        "acceptance_criteria": [
            "Backup passes database integrity checks cleanly.",
            "Restoration simulation restores 100% of records with zero corruption.",
            "Restoration procedures are fully documented and executable."
        ],
        "error_recovery": [
            "If backup verification fails integrity check, immediately take a fresh backup and investigate disk IO errors."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/database-backup-restore`.",
            "cursor": "Select `@database-backup-restore` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `database-backup-restore`.",
            "codex": "Reference `database-backup-restore` in Codex context.",
            "gemini": "Invoke via `gemini run database-backup-restore`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt database-backup-restore`.",
            "windsurf": "Activate `database-backup-restore` in Windsurf."
        },
        "references": [
            "`docs/STORAGE_AND_EXPORTS_GUIDE.md`",
            "`scripts/sync_sqlite_to_postgres.py`"
        ]
    },
    {
        "name": "deployment-validation",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Verify system health, critical workflows, logs, and configuration immediately following a software release.",
        "purpose": "Executes immediate post-deployment smoke tests verifying service availability, database connectivity, worker queue registration, and external portal reachability.",
        "when_to_use": [
            "Immediately following any production or staging deployment.",
            "After server reboot or container infrastructure restart."
        ],
        "when_not_to_use": [
            "During code editing before deployment."
        ],
        "required_inputs": [
            "Deployed base URL (`http://localhost:8000` or production domain)."
        ],
        "prerequisites": [
            "Completed deployment execution."
        ],
        "procedure": [
            ("Basic Health Probe", "Send GET request to `/api/v1/health`. Confirm HTTP 200 and `status: ok`."),
            ("Detailed Component Health Probe", "Send GET request to `/api/v1/health/detailed`. Verify all 8 components (FastAPI, SQLite/PG, Redis, Celery, Playwright, Extension, Settings, Exports) report healthy."),
            ("Portal Reachability Ping", "Send POST request to `/api/v1/settings/test-portal` for Broward and Dallas. Confirm portal reachability latency is recorded."),
            ("Worker Queue Depth Verification", "Query `/api/v1/queue/status`. Confirm queues are active and worker concurrency is available."),
            ("Frontend Smoke Verification", "Navigate to frontend UI on port 3000. Verify dashboard loads with accurate stat card counts."),
            ("Deployment Sign-Off", "Record validation outcome in deployment log.")
        ],
        "safety": [
            "If detailed health checks fail any critical component, halt release and trigger rollback.",
            "Do not allow operational traffic until deployment validation passes 100%."
        ],
        "deliverables": [
            "Post-Deployment Smoke Test Execution Report.",
            "Detailed Health JSON response snapshot."
        ],
        "acceptance_criteria": [
            "`/api/v1/health/detailed` reports 100% components healthy.",
            "Frontend UI loads cleanly without JavaScript errors.",
            "Worker queues report active worker processes."
        ],
        "error_recovery": [
            "If any component reports unhealthy, inspect specific error details in health response and restart failed container."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/deployment-validation`.",
            "cursor": "Select `@deployment-validation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `deployment-validation`.",
            "codex": "Reference `deployment-validation` in Codex context.",
            "gemini": "Invoke via `gemini run deployment-validation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt deployment-validation`.",
            "windsurf": "Activate `deployment-validation` in Windsurf."
        },
        "references": [
            "`backend/app/api/v1/endpoints/health.py`",
            "`docs/STAGE_AND_STATUS_DEFINITIONS.md`"
        ]
    },
    {
        "name": "rollback-deployment",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Restore a known-good release, database state, and configuration safely when deployment verification criteria fail.",
        "purpose": "Executes a rapid, deterministic rollback procedure to revert failed code deployments, restore pre-deployment database snapshots, and restore stable service.",
        "when_to_use": [
            "Post-deployment validation fails critical health checks.",
            "Severe unhandled errors or data corruption detected immediately following a release."
        ],
        "when_not_to_use": [
            "Routine feature deprecation."
        ],
        "required_inputs": [
            "Previous known-good release tag/commit, pre-deployment database backup, and rollback plan."
        ],
        "prerequisites": [
            "Documented rollback procedure in Deployment Plan."
        ],
        "procedure": [
            ("Rollback Decision & Incident Declaration", "Confirm rollback criteria are met. Announce rollback initiation to stakeholders."),
            ("Service Traffic Drainage", "Pause queue runner (`POST /api/v1/queue/pause`) and drain active tasks to prevent in-flight writes."),
            ("Code & Container Reversion", "Checkout previous known-good git tag: `git checkout <prior_tag>`. Rebuild or deploy prior container images."),
            ("Database Downgrade or Restoration", "Execute migration downgrade (`downgrade()`) or restore database from pre-deployment snapshot if schema changes were non-reversible."),
            ("Service Restart", "Restart backend API, Celery workers, and frontend UI under prior release version."),
            ("Post-Rollback Health Pass", "Verify `/api/v1/health/detailed` reports healthy status under the restored version."),
            ("Post-Mortem & Incident Logging", "Document rollback cause, timeline, and actions taken in incident post-mortem report.")
        ],
        "safety": [
            "CRITICAL: Always verify database backup integrity before overwriting live database with a snapshot.",
            "Never attempt unverified in-place code hotfixes during an active production deployment failure; roll back first."
        ],
        "deliverables": [
            "Restored stable production environment.",
            "Deployment Rollback & Incident Post-Mortem Report."
        ],
        "acceptance_criteria": [
            "System restored to 100% operational status on known-good release.",
            "Database integrity verified with zero data corruption.",
            "Stakeholders notified of successful recovery."
        ],
        "error_recovery": [
            "If code rollback succeeds but database is corrupted, restore immediately from pre-deployment backup archive."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/rollback-deployment`.",
            "cursor": "Select `@rollback-deployment` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `rollback-deployment`.",
            "codex": "Reference `rollback-deployment` in Codex context.",
            "gemini": "Invoke via `gemini run rollback-deployment`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt rollback-deployment`.",
            "windsurf": "Activate `rollback-deployment` in Windsurf."
        },
        "references": [
            "`DEPLOYMENT.md`",
            "`docs/STORAGE_AND_EXPORTS_GUIDE.md`"
        ]
    },
    {
        "name": "infrastructure-as-code",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Manage reproducible container definitions, Dockerfiles, network bridges, and volumes declaratively.",
        "purpose": "Enforces version-controlled, declarative configuration for all runtime containers, reverse proxies, and background worker infrastructure, eliminating configuration drift.",
        "when_to_use": [
            "Adding new containerized services (e.g. PostgreSQL, Grafana, Nginx).",
            "Modifying container resource limits (CPU, memory), networks, or port bindings."
        ],
        "when_not_to_use": [
            "Local code editing within an existing container."
        ],
        "required_inputs": [
            "`docker-compose.yml`, Dockerfiles, and container environment variables."
        ],
        "prerequisites": [
            "Docker and Docker Compose installed."
        ],
        "procedure": [
            ("Declarative Definition Authoring", "Define container services, build contexts, and environment bindings in `docker-compose.yml`."),
            ("Resource Limits & Health Check Specification", "Specify CPU and memory limits (`deploy.resources.limits`) and explicit healthcheck probe commands."),
            ("Persistent Volume Mapping", "Define named volumes for data persistence (`db_data`, `redis_data`, `export_data`)."),
            ("Compose Configuration Validation", "Validate syntax: `docker compose config` to verify zero YAML or schema errors."),
            ("Container Convergence Test", "Run `docker compose up -d` and verify containers converge cleanly to the target state."),
            ("Documentation Update", "Update `DEPLOYMENT_AND_HOSTING_GUIDE.md` detailing new container resources.")
        ],
        "safety": [
            "Never hardcode secrets in Dockerfiles or commit unmasked production passwords to compose files.",
            "Ensure container definitions pin specific base image tags rather than using `:latest`."
        ],
        "deliverables": [
            "Declarative `docker-compose.yml` and Dockerfiles.",
            "Updated infrastructure documentation."
        ],
        "acceptance_criteria": [
            "`docker compose config` validates with 0 errors.",
            "Containers build and launch deterministically from declarative files.",
            "Persistent data survives container teardown and recreation."
        ],
        "error_recovery": [
            "If volume permission errors occur on Linux containers, configure explicit UID/GID mapping in Dockerfiles."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/infrastructure-as-code`.",
            "cursor": "Select `@infrastructure-as-code` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `infrastructure-as-code`.",
            "codex": "Reference `infrastructure-as-code` in Codex context.",
            "gemini": "Invoke via `gemini run infrastructure-as-code`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt infrastructure-as-code`.",
            "windsurf": "Activate `infrastructure-as-code` in Windsurf."
        },
        "references": [
            "`docker-compose.yml`",
            "`DEPLOYMENT_AND_HOSTING_GUIDE.md`"
        ]
    },
    {
        "name": "monitoring-setup",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Configure health check endpoints (/health/detailed), queue depth monitoring, portal reachability pings, and operational alerts.",
        "purpose": "Establishes real-time observability into application health, Celery queue processing rates, portal reachability latency, and worker error rates.",
        "when_to_use": [
            "Configuring operational monitoring dashboards or uptime alert triggers.",
            "Extending `/api/v1/health/detailed` with new subsystem health probes."
        ],
        "when_not_to_use": [
            "Internal function unit testing."
        ],
        "required_inputs": [
            "Target metrics to monitor, health check route definitions, and alert thresholds."
        ],
        "prerequisites": [
            "FastAPI monitoring endpoints in `app/api/v1/endpoints/health.py`."
        ],
        "procedure": [
            ("Detailed Health Probe Implementation", "Implement `/api/v1/health/detailed` querying status, latency, and connectivity across all 8 components and 8 portals."),
            ("Queue Depth Metric Extraction", "Query Redis queue lengths and active worker counts in Celery inspection tasks."),
            ("Portal Reachability Pinger", "Implement lightweight HTTP HEAD probe (`/api/v1/health/portals/{key}/ping`) testing court portal responsiveness."),
            ("Email & Notification Trigger Rules", "Configure automated notification rules (`NotificationRule`) dispatching alerts on worker failure or queue stall."),
            ("Frontend Monitoring View Integration", "Expose live health metrics on `/health` and real-time queue telemetry on `/monitor`."),
            ("Verification Pass", "Simulate service failure (e.g. pause Redis) and verify monitoring endpoint accurately flags degraded status.")
        ],
        "safety": [
            "Ensure health check endpoints execute with low overhead and short timeouts (< 5s) to prevent health check hangs.",
            "Never expose sensitive internal network topologies in public health checks."
        ],
        "deliverables": [
            "Comprehensive health check and telemetry endpoints.",
            "Operational monitoring view on `/health` and `/monitor`."
        ],
        "acceptance_criteria": [
            "`/api/v1/health/detailed` reports status for all components and portals.",
            "Queue depth and active worker metrics update in real time.",
            "Simulated failures trigger accurate degradation warnings."
        ],
        "error_recovery": [
            "If portal pings cause rate-limiting, cache portal health status with 60-second TTL."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/monitoring-setup`.",
            "cursor": "Select `@monitoring-setup` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `monitoring-setup`.",
            "codex": "Reference `monitoring-setup` in Codex context.",
            "gemini": "Invoke via `gemini run monitoring-setup`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt monitoring-setup`.",
            "windsurf": "Activate `monitoring-setup` in Windsurf."
        },
        "references": [
            "`backend/app/api/v1/endpoints/health.py`",
            "`frontend/src/app/health/page.tsx`"
        ]
    },
    {
        "name": "release-management",
        "category_code": "G",
        "category_name": "Deployment & DevOps",
        "description": "Manage semantic versioning, automated changelog generation, git release tagging, and distribution packages.",
        "purpose": "Governs the software release lifecycle, enforcing semantic versioning (`vMAJOR.MINOR.PATCH`), immutable git tagging, comprehensive release notes, and distribution package integrity.",
        "when_to_use": [
            "Preparing and tagging a milestone release or production delivery package.",
            "Generating release changelogs from git commit history."
        ],
        "when_not_to_use": [
            "Routine local developer commits."
        ],
        "required_inputs": [
            "Git commit history since last release tag, milestone deliverables, and test verification reports."
        ],
        "prerequisites": [
            "100% passing test baseline across all suites."
        ],
        "procedure": [
            ("Semantic Version Calculation", "Determine next version number adhering to SemVer: Increment Major for breaking changes, Minor for backward-compatible features, Patch for bug fixes."),
            ("Changelog Generation", "Parse git commits since prior tag. Group entries into: New Features, Bug Fixes, Performance Improvements, Documentation, and Breaking Changes."),
            ("Version Bump Synchronization", "Update version strings in `package.json`, `app/__init__.py`, `README.md`, and documentation."),
            ("Full Test Verification Pass", "Execute complete automated test suite (`pytest`, `tsc`, `ps1`) to confirm release candidate is 100% green."),
            ("Git Tagging & Release Notes", "Create annotated git tag (`git tag -a v1.0.0 -m 'Release v1.0.0'`). Publish release notes in `docs/` and GitHub Releases."),
            ("Release Archival", "Archive release verification package (test logs, video demonstrations) in `docs/`.")
        ],
        "safety": [
            "CRITICAL: Never tag a release if any test fails or TypeScript compilation errors exist.",
            "Ensure release tags are immutable once published."
        ],
        "deliverables": [
            "Annotated git release tag.",
            "Comprehensive Release Notes and Changelog in `docs/`.",
            "Synchronized version numbers across repository files."
        ],
        "acceptance_criteria": [
            "Version numbers are consistent across backend, frontend, and docs.",
            "Changelog accurately documents all changes since prior tag.",
            "Full automated test suite passes with 100% success rate."
        ],
        "error_recovery": [
            "If an emergency patch is required post-release, increment patch version (`v1.0.1`) and author dedicated hotfix plan."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/release-management`.",
            "cursor": "Select `@release-management` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `release-management`.",
            "codex": "Reference `release-management` in Codex context.",
            "gemini": "Invoke via `gemini run release-management`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt release-management`.",
            "windsurf": "Activate `release-management` in Windsurf."
        },
        "references": [
            "`Deploy-To-GitHub.ps1`",
            "`README.md` - Version History"
        ]
    }
]

