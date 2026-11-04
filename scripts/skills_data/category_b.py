"""
Category B: Planning & Project Management
Contains 13 comprehensive skills for engineering governance, structured planning,
WBS creation, estimation, milestone tracking, risk assessment, and team coordination.
"""

SKILLS_B = [
    {
        "name": "diagnose-plan-confirm-execute",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Universal AI Engineering Governance Skill: Understand -> Inspect -> Diagnose -> Plan -> Confirm -> Execute -> Verify. Enforces NO APPROVAL = NO IMPLEMENTATION.",
        "purpose": "Enforces the mandatory non-negotiable engineering lifecycle across all features, bug fixes, refactorings, and infrastructure modifications. Strictly forbids jumping from prompt to code without an approved plan.",
        "when_to_use": [
            "ALL non-trivial engineering tasks, architectural changes, bug fixes, or database migrations.",
            "Any change that touches more than one file or alters system contracts."
        ],
        "when_not_to_use": [
            "Trivial questions where the user explicitly requests an immediate one-line text answer without modifying code."
        ],
        "required_inputs": [
            "User request, relevant codebase files, test suites, and documentation history in `docs/`."
        ],
        "prerequisites": [
            "Completed inspection of target modules and baseline test pass rates."
        ],
        "procedure": [
            ("Understand & Inspect", "Analyze the user prompt, inspect relevant code/configuration, review `README.md` and historical records in `docs/`."),
            ("Diagnose & Gap Analysis", "Identify root causes with concrete evidence. Compare current state against expected requirements."),
            ("Detailed Implementation Plan Authoring", "Author a comprehensive plan with Implementation ID (`IMP-YYYY-MMDD-NNN`), affected files, test plan, risks, and rollback steps. Save to `docs/` and create session artifact."),
            ("Confirmation Gate (Wait for Approval)", "Present the plan to the user. Strictly wait for explicit human approval before touching any code. NO APPROVAL = NO IMPLEMENTATION."),
            ("Execute & Document", "Implement approved changes following strict coding conventions. Update `README.md` and documentation."),
            ("Verify & Finalize", "Run automated test suites (`pytest`, `tsc`, `ruff`, `ps1`). Record visual and log evidence. Finalize documentation.")
        ],
        "safety": [
            "NEVER modify source code before presenting a plan and receiving explicit approval.",
            "Never fabricate test results, approvals, or deployment status.",
            "Do not mark documentation as Human Verified—only the human user can do that."
        ],
        "deliverables": [
            "Formal Implementation Plan in `docs/YYYY-MM-DD_uaic_<feature>_implementation_plan_v<N>.md`.",
            "Interactive Plan Artifact in brain directory.",
            "Final Verified Record and Walkthrough Document."
        ],
        "acceptance_criteria": [
            "Implementation plan approved explicitly by user before code modification.",
            "100% of planned tests pass with verifiable automated evidence.",
            "`README.md` and related docs updated to reflect changes."
        ],
        "error_recovery": [
            "If user rejects the plan, return to Step 2, incorporate feedback, and author revised plan `_v2.md`.",
            "If unexpected errors occur during execution, pause, document the gap, and seek user confirmation if scope changes."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/diagnose-plan-confirm-execute` or follow the mandatory governance rule.",
            "cursor": "Select `@diagnose-plan-confirm-execute` in Cursor chat.",
            "claude_code": "Prompt Claude Code: 'Follow the diagnose-plan-confirm-execute lifecycle.'",
            "codex": "Mandated by `AGENTS.md` in OpenAI Codex.",
            "gemini": "Invoke via `gemini run diagnose-plan-confirm-execute`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt diagnose-plan-confirm-execute`.",
            "windsurf": "Activate `diagnose-plan-confirm-execute` rule in Windsurf."
        },
        "references": [
            "`.agents/skills/diagnose-plan-confirm-execute/SKILL.md` (Authoritative Governance Skill)",
            "`AGENTS.md` - Section 8 (AI Agent Rules)"
        ]
    },
    {
        "name": "implementation-plan",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Produce structured technical implementation plans with affected files, explicit code diff previews, test strategies, and rollback plans.",
        "purpose": "Creates high-fidelity technical design documents that allow engineers and users to make informed, risk-aware decisions before any code changes occur.",
        "when_to_use": [
            "Directly following diagnosis and requirements analysis for any significant feature or bug fix.",
            "When responding to `/plan` slash command."
        ],
        "when_not_to_use": [
            "Executing pre-approved code changes."
        ],
        "required_inputs": [
            "Diagnosis findings, requirements specification, and target file paths."
        ],
        "prerequisites": [
            "Verified root cause and confirmed requirements."
        ],
        "procedure": [
            ("Metadata & Header Initialization", "Assign Implementation ID (`IMP-YYYY-MMDD-NNN`), author, date, status (Awaiting Approval), and target repository."),
            ("Goal & Background Description", "State the core problem, context, and expected business outcome concisely."),
            ("Proposed File Changes & Diffs", "Group proposed changes by component. Explicitly label files as `[NEW]`, `[MODIFY]`, or `[DELETE]`. Provide exact diff previews."),
            ("Verification Plan Specification", "Define exact automated test commands (`pytest`, `tsc`, `ruff`, Playwright) and manual verification steps."),
            ("Risk Analysis & Rollback Strategy", "Detail potential failure modes, mitigation steps, and an unambiguous rollback protocol."),
            ("Document Archival", "Save plan to `docs/` and generate the user-facing interactive artifact.")
        ],
        "safety": [
            "Always include diff previews for critical business logic to prevent subtle regressions.",
            "Never omit the rollback strategy."
        ],
        "deliverables": [
            "Standardized Implementation Plan Document in `docs/`.",
            "Session Plan Artifact with `request_feedback: true`."
        ],
        "acceptance_criteria": [
            "Plan contains all required sections (Goal, Review Required, Proposed Changes, Verification, Risks, Rollback).",
            "Every affected file is categorized and accompanied by explicit diff or code snippets.",
            "Automated test commands are exact and executable directly in PowerShell."
        ],
        "error_recovery": [
            "If user requests modifications to the plan, update the document with incremented version (`_v2.md`)."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via `/plan` or `/implementation-plan`.",
            "cursor": "Select `@implementation-plan` in Cursor.",
            "claude_code": "Prompt Claude Code: 'Create a formal implementation plan.'",
            "codex": "Reference `implementation-plan` in Codex.",
            "gemini": "Invoke via `gemini run implementation-plan`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt implementation-plan`.",
            "windsurf": "Activate `implementation-plan` workflow in Windsurf."
        },
        "references": [
            "`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "wbs-creation",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Create a hierarchical, deliverable-oriented Work Breakdown Structure decomposing complex projects into manageable work packages.",
        "purpose": "Structures complex initiatives into discrete, mutually exclusive work packages (100% Rule), establishing ownership boundaries and deliverable gates.",
        "when_to_use": [
            "Initiating large multi-week features, platform migrations, or new microservices.",
            "Coordinating complex multi-stage tasks across frontend, backend, and DevOps."
        ],
        "when_not_to_use": [
            "Single-file bug fixes or straightforward routine maintenance."
        ],
        "required_inputs": [
            "Approved project scope, functional requirements, and target architecture."
        ],
        "prerequisites": [
            "Completed `requirement-analysis` and `architecture-analysis`."
        ],
        "procedure": [
            ("Top-Level Phase Partitioning", "Partition total scope into primary chronological or architectural phases (e.g., Phase 1: Database, Phase 2: Backend API, Phase 3: Frontend UI, Phase 4: E2E Testing)."),
            ("Work Package Decomposition", "Decompose each phase into discrete Work Packages (WP-01, WP-02, ...), adhering to the 100% Rule (encompassing total scope with zero overlap)."),
            ("Deliverable & Milestone Definition", "Assign concrete, verifiable deliverables and completion gates to each work package."),
            ("Traceability Mapping", "Cross-reference each work package with specific functional requirement IDs from the Requirements Traceability Matrix."),
            ("WBS Document Generation", "Generate a structured WBS tabular breakdown and visual tree diagram (`graph TD`).")
        ],
        "safety": [
            "Ensure zero work packages are defined without concrete, verifiable acceptance criteria.",
            "Do not allow overlapping or ambiguous scope between work packages."
        ],
        "deliverables": [
            "Formal Work Breakdown Structure Document.",
            "Mermaid WBS Tree Diagram."
        ],
        "acceptance_criteria": [
            "100% of project requirements are mapped to at least one work package.",
            "Every work package has an unambiguous deliverable and objective acceptance gate.",
            "Dependencies between packages are clearly identified."
        ],
        "error_recovery": [
            "If scope creeps or changes during development, revise the WBS document and update package IDs."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/wbs-creation`.",
            "cursor": "Select `@wbs-creation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `wbs-creation`.",
            "codex": "Reference `wbs-creation` in Codex context.",
            "gemini": "Invoke via `gemini run wbs-creation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt wbs-creation`.",
            "windsurf": "Activate `wbs-creation` in Windsurf."
        },
        "references": [
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "effort-estimation",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Estimate engineering effort using structured three-point estimation (Optimistic, Most Likely, Pessimistic) with explicit assumptions.",
        "purpose": "Provides realistic, evidence-based effort estimates accounting for technical uncertainty, third-party dependencies, and testing overhead.",
        "when_to_use": [
            "Scoping feature releases, sprint planning, or roadmap formulation.",
            "Evaluating architectural alternatives where development time is a primary constraint."
        ],
        "when_not_to_use": [
            "Simple operational commands or running pre-existing scripts."
        ],
        "required_inputs": [
            "Approved WBS or task breakdown.",
            "Historical velocity and technical complexity ratings."
        ],
        "prerequisites": [
            "Completed `task-breakdown` or `wbs-creation`."
        ],
        "procedure": [
            ("Task Isolation & Complexity Rating", "Review each atomic task. Rate complexity (Low, Medium, High, Extreme) based on dependencies and novelty."),
            ("Three-Point Estimation", "For each task, estimate Optimistic (O), Most Likely (M), and Pessimistic (P) hours."),
            ("PERT Expected Value Calculation", "Compute expected effort using PERT formula: $E = (O + 4M + P) / 6$, and standard deviation: $\\sigma = (P - O) / 6$."),
            ("Assumption & Risk Listing", "Explicitly record all assumptions (e.g., third-party API availability, mock server readiness) that underpin the estimates."),
            ("Estimation Report Synthesis", "Produce an Effort Estimation Summary with total expected effort, confidence intervals, and contingency recommendations.")
        ],
        "safety": [
            "Never present a single-point estimate for high-uncertainty tasks.",
            "Always include automated testing and documentation time in task estimates."
        ],
        "deliverables": [
            "Three-Point Effort Estimation Table.",
            "Documented Technical Assumptions & Contingency Buffer."
        ],
        "acceptance_criteria": [
            "All tasks in scope have O, M, and P estimates with calculated PERT values.",
            "Underlying assumptions are explicitly stated.",
            "Testing and verification effort is explicitly budgeted."
        ],
        "error_recovery": [
            "If an assumption is invalidated during implementation, re-estimate affected tasks immediately."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/effort-estimation`.",
            "cursor": "Select `@effort-estimation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `effort-estimation`.",
            "codex": "Reference `effort-estimation` in Codex prompt.",
            "gemini": "Invoke via `gemini run effort-estimation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt effort-estimation`.",
            "windsurf": "Activate `effort-estimation` in Windsurf."
        },
        "references": [
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "milestone-planning",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Define project milestones, sequencing constraints, critical paths, and unambiguous exit criteria for each development stage.",
        "purpose": "Establishes clear, objective checkpoint milestones along the development timeline to maintain momentum, validate progress, and catch regressions early.",
        "when_to_use": [
            "Structuring multi-phase delivery cycles.",
            "Coordinating integration deadlines between frontend and backend teams."
        ],
        "when_not_to_use": [
            "Day-to-day atomic task execution."
        ],
        "required_inputs": [
            "WBS, effort estimates, and external deadline constraints."
        ],
        "prerequisites": [
            "Completed `wbs-creation` and `dependency-planning`."
        ],
        "procedure": [
            ("Milestone Identification", "Define 3-5 major project milestones (e.g., M1: Core Engine & DB Verified, M2: APIs & Workers Operational, M3: Frontend & End-to-End Complete, M4: Release Ready)."),
            ("Critical Path Mapping", "Identify sequence of dependent tasks that determines the minimum total project duration."),
            ("Exit Criteria Formulation", "Define measurable, non-negotiable exit criteria for each milestone (e.g., 100% unit tests pass, zero lint errors, verified staging run)."),
            ("Sign-Off & Gatekeeper Definition", "Assign verification authority (Human Operator, Automated Test Suite) for each milestone gate."),
            ("Milestone Schedule Synthesis", "Publish the Milestone Schedule with target completion windows and dependency triggers.")
        ],
        "safety": [
            "Never advance past a milestone if exit criteria are not 100% satisfied.",
            "Do not compress testing windows on the critical path to meet deadlines."
        ],
        "deliverables": [
            "Project Milestone Schedule and Critical Path Map.",
            "Milestone Exit Verification Checklist."
        ],
        "acceptance_criteria": [
            "All milestones have distinct, measurable technical exit criteria.",
            "Critical path dependencies are explicitly mapped.",
            "Gate review protocols are defined for each stage transition."
        ],
        "error_recovery": [
            "If a milestone gate fails, trigger an immediate diagnosis pass and adjust subsequent milestone schedules."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/milestone-planning`.",
            "cursor": "Select `@milestone-planning` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `milestone-planning`.",
            "codex": "Reference `milestone-planning` in Codex prompt.",
            "gemini": "Invoke via `gemini run milestone-planning`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt milestone-planning`.",
            "windsurf": "Activate `milestone-planning` in Windsurf."
        },
        "references": [
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "task-breakdown",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Split work packages or user stories into small, atomic, testable, and independently verifiable implementation tasks.",
        "purpose": "Converts broad feature objectives into atomic engineering tasks that can be implemented and verified within focused coding sessions without context loss.",
        "when_to_use": [
            "Translating an approved implementation plan or WBS into executable steps.",
            "Prior to starting a complex coding turn."
        ],
        "when_not_to_use": [
            "When executing an already itemized task list."
        ],
        "required_inputs": [
            "Approved implementation plan or feature specification."
        ],
        "prerequisites": [
            "Clear understanding of affected files and technical design."
        ],
        "procedure": [
            ("Atomicity Scoping", "Decompose work packages such that each task modifies 1-3 related files and takes < 2 hours of focused effort."),
            ("Sequential Dependency Ordering", "Order tasks logically: Data Model/Migration -> Service/Business Logic -> API Endpoints -> Frontend UI -> E2E Tests."),
            ("Verification Command Assignment", "Assign an exact automated test or verification command to each individual task."),
            ("Checkpoint & Commit Mapping", "Define logical git commit points and state checkpoints between tasks."),
            ("Task Checklist Generation", "Generate an interactive markdown task list (`- [ ] Task Description`).")
        ],
        "safety": [
            "Never create tasks that leave the repository in a broken build state across checkpoints.",
            "Ensure database migrations are isolated into dedicated pre-deployment tasks."
        ],
        "deliverables": [
            "Itemized Task Checklist with file paths and verification commands.",
            "Sequential Execution Roadmap."
        ],
        "acceptance_criteria": [
            "Every task is atomic, testable, and assigned specific file targets.",
            "Each task includes an exact PowerShell verification command.",
            "Dependencies between tasks are strictly respected in ordering."
        ],
        "error_recovery": [
            "If a task proves too complex during implementation, pause and split it into two sub-tasks."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/task-breakdown`.",
            "cursor": "Select `@task-breakdown` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `task-breakdown`.",
            "codex": "Reference `task-breakdown` in Codex context.",
            "gemini": "Invoke via `gemini run task-breakdown`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt task-breakdown`.",
            "windsurf": "Activate `task-breakdown` in Windsurf."
        },
        "references": [
            "`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`"
        ]
    },
    {
        "name": "dependency-planning",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Identify sequencing constraints, critical paths, blockers, and external dependencies before initiating development.",
        "purpose": "Prevents pipeline stalls, merge conflicts, and rework by mapping architectural and team dependencies before writing code.",
        "when_to_use": [
            "Planning multi-service or cross-functional development sprints.",
            "Coordinating changes that touch shared database tables or core configuration."
        ],
        "when_not_to_use": [
            "Isolated tasks with zero external dependencies."
        ],
        "required_inputs": [
            "Task breakdown and architecture component map."
        ],
        "prerequisites": [
            "Completed `task-breakdown`."
        ],
        "procedure": [
            ("Dependency Identification", "For every task, enumerate mandatory prerequisites (e.g. Task C requires Task A DB migration and Task B API schema)."),
            ("Dependency Graph Construction", "Construct a directed acyclic graph (DAG) of task dependencies using Mermaid (`graph LR`)."),
            ("Cycle Detection & Decoupling", "Detect and resolve circular dependencies using interface abstraction or mock adapters."),
            ("Critical Path Identification", "Highlight tasks on the critical path that directly impact final delivery date."),
            ("Parallel Workstream Tagging", "Identify independent tasks that can be safely executed concurrently by parallel agents.")
        ],
        "safety": [
            "Do NOT run tasks in parallel if they modify the same shared files.",
            "Ensure database schema changes are strictly sequenced before code that depends on new columns."
        ],
        "deliverables": [
            "Task Dependency DAG & Critical Path Map.",
            "Parallel Workstream Matrix."
        ],
        "acceptance_criteria": [
            "Zero circular dependencies exist in the execution plan.",
            "All parallel workstreams operate on strictly disjoint file sets.",
            "Prerequisites for every critical task are verified before execution begins."
        ],
        "error_recovery": [
            "If a blocking dependency is delayed, pivot to an independent workstream or implement a stub interface."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/dependency-planning`.",
            "cursor": "Select `@dependency-planning` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `dependency-planning`.",
            "codex": "Reference `dependency-planning` in Codex prompt.",
            "gemini": "Invoke via `gemini run dependency-planning`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt dependency-planning`.",
            "windsurf": "Activate `dependency-planning` in Windsurf."
        },
        "references": [
            "`docs/DEVELOPMENT_WORKFLOW.md`"
        ]
    },
    {
        "name": "risk-assessment",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Construct comprehensive risk registers recording likelihood, impact severity, mitigation strategies, and contingency triggers.",
        "purpose": "Proactively identifies technical, operational, and compliance risks, formulating concrete prevention and recovery procedures before issues occur.",
        "when_to_use": [
            "Pre-implementation planning for high-impact or irreversible changes.",
            "Integrating with external production APIs (Guidewire) or court portals.",
            "Automating web scrapers subject to CAPTCHA or anti-bot protections."
        ],
        "when_not_to_use": [
            "Low-risk documentation updates."
        ],
        "required_inputs": [
            "Technical architecture, external service contracts, and deployment plan."
        ],
        "prerequisites": [
            "Completed `architecture-analysis` and `technical-feasibility`."
        ],
        "procedure": [
            ("Risk Brainstorming & Identification", "Enumerate potential failure modes across Technical, Operational, Compliance, and Security categories."),
            ("Likelihood & Impact Scoring", "Score each risk on Likelihood (1-5) and Impact (1-5). Compute Risk Exposure Score ($R = L \\times I$)."),
            ("Mitigation Strategy Formulation", "Develop preventive controls to reduce Likelihood for all risks scoring $\\ge 10$."),
            ("Contingency & Trigger Definition", "Define specific observable triggers and recovery procedures if a risk manifests."),
            ("Risk Register Documentation", "Format findings into a formal Risk Register table with assigned risk owners.")
        ],
        "safety": [
            "Any risk involving customer data loss, credential exposure, or portal IP blocking must be treated as Critical.",
            "Ensure rollback contingencies are verified before deploying high-risk changes."
        ],
        "deliverables": [
            "Comprehensive Risk Register Matrix.",
            "Contingency Action Runbook."
        ],
        "acceptance_criteria": [
            "All identified risks have quantified likelihood and impact ratings.",
            "High and Critical risks have documented preventive mitigations and contingency triggers.",
            "Data loss and external blocking risks are fully addressed."
        ],
        "error_recovery": [
            "If an unforeseen risk manifests during execution, pause immediately and initiate the contingency protocol."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/risk-assessment`.",
            "cursor": "Select `@risk-assessment` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `risk-assessment`.",
            "codex": "Reference `risk-assessment` in Codex context.",
            "gemini": "Invoke via `gemini run risk-assessment`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt risk-assessment`.",
            "windsurf": "Activate `risk-assessment` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (AI Agent Rules)",
            "`docs/PROXY_NETWORK_GUIDE.md`"
        ]
    },
    {
        "name": "solution-design",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Author high-level and low-level technical solution designs detailing data flow, module boundaries, interfaces, and alternatives.",
        "purpose": "Translates approved requirements into an authoritative technical design specification, detailing database schemas, API contracts, sequence diagrams, and class responsibilities.",
        "when_to_use": [
            "Designing a major new feature, subsystem, or third-party integration.",
            "Standardizing architectural patterns across multiple microservices or scrapers."
        ],
        "when_not_to_use": [
            "Small bug fixes or superficial UI tweaks."
        ],
        "required_inputs": [
            "Approved functional requirements and architecture analysis."
        ],
        "prerequisites": [
            "Completed `requirement-analysis` and `technical-feasibility`."
        ],
        "procedure": [
            ("System Context & Scope Definition", "Define system boundaries, external integrations, and primary data inputs/outputs."),
            ("Component & Data Flow Modeling", "Design components, responsibilities, and dataflows using Mermaid sequence diagrams (`sequenceDiagram`)."),
            ("Database Schema & Persistence Design", "Specify table structures, column datatypes, primary/foreign keys, indexes, and nullability constraints."),
            ("API Contract & Payload Specification", "Define exact REST endpoints, HTTP methods, request bodies, query parameters, response codes, and JSON schemas."),
            ("Error Handling & Resilience Architecture", "Design timeout policies, retry exponential backoff, circuit breaking, and dead-letter queues."),
            ("Solution Design Document Synthesis", "Publish the complete Technical Solution Design in `docs/`.")
        ],
        "safety": [
            "Never specify hardcoded secrets, API tokens, or plain-text passwords in solution designs.",
            "Ensure designs adhere to the project's strict dual-theme UI tokens and Python 3.14 constraints."
        ],
        "deliverables": [
            "Technical Solution Design Document (SDD) in `docs/`.",
            "Mermaid Sequence & Class Diagrams."
        ],
        "acceptance_criteria": [
            "Complete dataflow is documented from UI client to database and external APIs.",
            "Database schemas, indexes, and migrations are explicitly specified.",
            "API request/response payloads are documented with typed examples."
        ],
        "error_recovery": [
            "If review reveals architectural conflicts, update the design and log rationale in an ADR."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/solution-design`.",
            "cursor": "Select `@solution-design` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `solution-design`.",
            "codex": "Reference `solution-design` in Codex context.",
            "gemini": "Invoke via `gemini run solution-design`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt solution-design`.",
            "windsurf": "Activate `solution-design` in Windsurf."
        },
        "references": [
            "`docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`",
            "`backend/app/schemas/settings.py`"
        ]
    },
    {
        "name": "architecture-decision-record",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Record significant architecture decisions, rationale, context, consequences, and evaluated alternatives in immutable ADRs.",
        "purpose": "Maintains an immutable historical record of major technical decisions, preserving architectural context and preventing future regressions or circular debates.",
        "when_to_use": [
            "Adopting or retiring a core technology, framework, database, or library.",
            "Choosing an architectural style (e.g. monolithic FastAPI + Celery vs microservices).",
            "Establishing significant technical conventions (e.g., synchronous Playwright for AntiCaptcha stability)."
        ],
        "when_not_to_use": [
            "Routine implementation choices that follow established conventions."
        ],
        "required_inputs": [
            "Context of the decision, evaluated options, trade-offs, and final consensus."
        ],
        "prerequisites": [
            "Completed `technical-feasibility` or team consensus."
        ],
        "procedure": [
            ("ADR Numbering & Titling", "Assign sequential ID: `ADR-NNN: <Short Decision Title>`. Status: Proposed, Accepted, Deprecated, or Superseded."),
            ("Context Statement Formulation", "Describe the engineering context, business drivers, constraints, and forces at play."),
            ("Decision Statement", "State clearly: 'We will ...' with unambiguous commitment to the chosen architecture."),
            ("Consequences & Trade-Offs", "Detail positive consequences, negative trade-offs, risks, and follow-up maintenance overhead."),
            ("Alternatives Considered", "Document rejected alternatives with explicit reasons for rejection."),
            ("Archival & Linkage", "Save to `docs/adr/` or `docs/` and cross-reference in `README.md`.")
        ],
        "safety": [
            "Never overwrite an existing ADR; create a new ADR that explicitly supersedes the older one.",
            "Ensure ADRs reflect verified reality, not aspirational theories."
        ],
        "deliverables": [
            "Formal Architecture Decision Record (`docs/ADR-NNN_<title>.md`).",
            "Updated ADR Index in project documentation."
        ],
        "acceptance_criteria": [
            "ADR adheres to standard Michael Nygard format (Title, Status, Context, Decision, Consequences, Alternatives).",
            "Both positive and negative consequences are objectively documented.",
            "Cross-referenced in repository documentation."
        ],
        "error_recovery": [
            "If an approved ADR proves unworkable in practice, author a new superseding ADR documenting lessons learned."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/architecture-decision-record`.",
            "cursor": "Select `@architecture-decision-record` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `architecture-decision-record`.",
            "codex": "Reference `architecture-decision-record` in Codex context.",
            "gemini": "Invoke via `gemini run architecture-decision-record`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt architecture-decision-record`.",
            "windsurf": "Activate `architecture-decision-record` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 1 (Project Identity) & Section 3 (Critical Business Rules)",
            "`README.md`"
        ]
    },
    {
        "name": "execution-tracking",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Track ongoing implementation tasks against the approved plan and update progress with verifiable automated evidence.",
        "purpose": "Provides continuous visibility into implementation progress, ensuring every completed task is backed by actual test evidence and preventing drift from the approved plan.",
        "when_to_use": [
            "During active execution of multi-step implementation plans.",
            "Following completion of individual work packages or checkpoints."
        ],
        "when_not_to_use": [
            "Initial planning phase before work has commenced."
        ],
        "required_inputs": [
            "Approved Implementation Plan and task checklist.",
            "Automated test run outputs and verification artifacts."
        ],
        "prerequisites": [
            "Active execution of approved implementation plan."
        ],
        "procedure": [
            ("Task Progress Inspection", "Check current state against the task checklist. Verify which tasks are Pending, In Progress, or Complete."),
            ("Evidence Verification Audit", "For completed tasks, inspect test outputs (`pytest` logs, `tsc` exits, browser recordings) to confirm genuine completion."),
            ("Checklist State Mutation", "Update task checkboxes (`[x]`) and timestamp verified milestones."),
            ("Deviation & Blocker Detection", "Identify any unexpected scope additions, test failures, or performance regressions."),
            ("Progress Snapshot Generation", "Publish a concise Execution Tracking Snapshot detailing completed tasks, active task, and next steps.")
        ],
        "safety": [
            "CRITICAL: Never mark a task as completed without verified automated evidence.",
            "Do NOT silently bypass failing tests; log them as blockers."
        ],
        "deliverables": [
            "Updated Task Progress Checklist.",
            "Execution Progress Summary with test verification logs."
        ],
        "acceptance_criteria": [
            "Every completed task is accompanied by verifiable terminal or test evidence.",
            "Discrepancies between plan and actual implementation are documented.",
            "Remaining tasks and blockers are clearly identified."
        ],
        "error_recovery": [
            "If an execution blocker halts progress, invoke `diagnose-issue` and document the roadblock."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/execution-tracking`.",
            "cursor": "Select `@execution-tracking` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `execution-tracking`.",
            "codex": "Reference `execution-tracking` in Codex prompt.",
            "gemini": "Invoke via `gemini run execution-tracking`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt execution-tracking`.",
            "windsurf": "Activate `execution-tracking` in Windsurf."
        },
        "references": [
            "`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`"
        ]
    },
    {
        "name": "teamwork",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Coordinate multi-agent and parallel workstreams with clear ownership boundaries, interface contracts, and serialized file modifications.",
        "purpose": "Orchestrates concurrent agent execution (e.g. Frontend Agent, Backend Agent, Testing Agent) while preventing file overwrite collisions, race conditions, and merge conflicts.",
        "when_to_use": [
            "Dividing large multi-service tasks across independent AI subagents.",
            "Running parallel research, linting, or testing alongside active implementation.",
            "Responding to `/teamwork` slash command."
        ],
        "when_not_to_use": [
            "Single-agent sequential tasks or tasks editing the same shared files."
        ],
        "required_inputs": [
            "Approved project scope partitioned into independent, decoupled domains."
        ],
        "prerequisites": [
            "Tool support for subagent invocation (`invoke_subagent`)."
        ],
        "procedure": [
            ("Domain Boundary Partitioning", "Partition work into strictly disjoint domains (e.g. Agent A: `backend/app/api/`, Agent B: `frontend/src/app/`, Agent C: `tests/`)."),
            ("Interface Contract Freezing", "Freeze TypeScript types, REST endpoint paths, and database schemas before launching parallel subagents."),
            ("Subagent Launch & Role Assignment", "Launch subagents with dedicated prompts, specific role titles ('Backend Architect', 'Frontend Developer'), and isolated workspace modes."),
            ("Inter-Agent Communication & Synchronization", "Monitor subagent completion messages. Coordinate integration handoffs sequentially."),
            ("Integration Validation & Synthesis", "Execute full-stack integration tests (`pytest`, `tsc`) to verify combined output.")
        ],
        "safety": [
            "CRITICAL: Never allow two parallel agents to modify the same file concurrently.",
            "Do NOT run parallel agents without frozen interface contracts."
        ],
        "deliverables": [
            "Multi-Agent Coordination Plan.",
            "Consolidated Integration Test Report."
        ],
        "acceptance_criteria": [
            "All subagents operate on strictly non-overlapping file sets.",
            "Interface contracts are respected across all subagent deliverables.",
            "Combined code passes all integration test suites without regressions."
        ],
        "error_recovery": [
            "If subagents generate conflicting code, serialize modifications and resolve interface discrepancies immediately."
        ],
        "tool_invocations": {
            "antigravity": "Invoke native slash command `/teamwork` or use `invoke_subagent`.",
            "cursor": "Coordinate via separate Cursor chat sessions.",
            "claude_code": "Use Claude Code subagents with explicit file boundaries.",
            "codex": "Reference `teamwork` in Codex multi-agent context.",
            "gemini": "Invoke via `gemini run teamwork`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt teamwork`.",
            "windsurf": "Activate `teamwork` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)"
        ]
    },
    {
        "name": "project-status-report",
        "category_code": "B",
        "category_name": "Planning & Project Management",
        "description": "Produce concise, high-signal project status reports detailing progress, blockers, active risks, and next steps for stakeholders.",
        "purpose": "Generates executive and engineering status summaries communicating progress against plan, milestone achievements, test pass metrics, and active blockers.",
        "when_to_use": [
            "Completing a development cycle or milestone.",
            "Providing daily or weekly stakeholder progress updates.",
            "Reporting major roadblocks or unexpected discoveries."
        ],
        "when_not_to_use": [
            "Internal atomic code commit messages."
        ],
        "required_inputs": [
            "Current task progress, test results, git log, and blocker notes."
        ],
        "prerequisites": [
            "Verified test suite execution data."
        ],
        "procedure": [
            ("Executive Summary Formulation", "Summarize high-level progress in 2-3 concise sentences."),
            ("Key Achievements Cataloguing", "List completed milestones and implemented features with bulleted highlights."),
            ("Metric & Test Evidence Summary", "Report quantifiable metrics: test pass rates (e.g. 556/556 passing), code coverage, lint status, and build time."),
            ("Blockers & Active Risks", "Highlight unresolved technical blockers, external API dependencies, or timeline risks with proposed remediations."),
            ("Next Steps & Upcoming Milestones", "Detail immediate priorities and next actionable deliverables for the upcoming cycle.")
        ],
        "safety": [
            "Always report test failures and blockers transparently; never conceal technical debt.",
            "Do not include speculative delivery dates without confidence ranges."
        ],
        "deliverables": [
            "Project Status Report Document (`docs/YYYY-MM-DD_project_status_report.md`).",
            "Executive Summary briefing."
        ],
        "acceptance_criteria": [
            "Report clearly distinguishes Completed, In Progress, and Blocked work packages.",
            "Test pass rates and build status are quantified with concrete numbers.",
            "Next steps are explicitly enumerated with owners and target timeframes."
        ],
        "error_recovery": [
            "If metrics cannot be gathered, run `pytest` and `tsc` immediately to establish live status."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/project-status-report`.",
            "cursor": "Select `@project-status-report` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `project-status-report`.",
            "codex": "Reference `project-status-report` in Codex context.",
            "gemini": "Invoke via `gemini run project-status-report`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt project-status-report`.",
            "windsurf": "Activate `project-status-report` in Windsurf."
        },
        "references": [
            "`docs/WALKTHROUGH.md`",
            "`AGENTS.md` - Section 8"
        ]
    }
]

