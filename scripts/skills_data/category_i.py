"""
Category I: Agent Management & Automation
Contains 13 comprehensive skills for subagent orchestration, delegation, parallel execution,
recovery, context management, skill creation/repair, Antigravity customizations, and delivery audits.
"""

SKILLS_I = [
    {
        "name": "agent-orchestration",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Coordinate multi-agent workflows, specialist roles, interface contracts, and cross-agent communication channels.",
        "purpose": "Coordinates complex, multi-agent software engineering workstreams, establishing clean division of labor between specialized agents (e.g. Research, Architecture, Implementation, QA) while managing communication and shared state.",
        "when_to_use": [
            "Orchestrating complex, multi-faceted engineering projects across specialized agents.",
            "Managing independent research or verification streams concurrently."
        ],
        "when_not_to_use": [
            "Simple single-file edits."
        ],
        "required_inputs": [
            "Project objective, decoupled workstream definitions, and subagent tool grants."
        ],
        "prerequisites": [
            "Agent framework supporting subagent delegation (`invoke_subagent`, `send_message`)."
        ],
        "procedure": [
            ("Role & Responsibility Partitioning", "Define specialist agent roles: Lead Architect (governance/planning), Scraper Specialist (Playwright/Chrome), API Specialist (FastAPI/DB), Frontend Specialist (Next.js/UI), and QA Specialist (pytest/verification)."),
            ("Interface Contract Freezing", "Establish frozen interface contracts (Pydantic schemas, TypeScript types, database schemas) before launching agents."),
            ("Subagent Lifecycle Management", "Launch specialist subagents using `invoke_subagent` with explicit task prompts, required deliverables, and appropriate workspace modes (`inherit`, `branch`)."),
            ("Message Routing & Synchronization", "Monitor subagent completion messages. Route intermediate findings between subagents via `send_message`."),
            ("Convergence & Integration Pass", "Integrate subagent deliverables sequentially, resolve interface discrepancies, and execute full-stack regression tests."),
            ("Audit & Teardown", "Terminate finished subagents via `manage_subagents` and archive logs.")
        ],
        "safety": [
            "Never allow two subagents to modify the same file concurrently.",
            "Ensure the Lead Agent maintains ultimate governance authority and verifies all subagent deliverables."
        ],
        "deliverables": [
            "Multi-Agent Orchestration Log.",
            "Integrated, tested software deliverables."
        ],
        "acceptance_criteria": [
            "Each subagent operates within strictly defined file and tool boundaries.",
            "All subagent deliverables integrate cleanly without merge conflicts.",
            "Full regression test suite passes."
        ],
        "error_recovery": [
            "If a subagent fails or times out, inspect subagent task logs, kill the stuck agent, and re-launch with refined prompt."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/agent-orchestration` or slash command `/teamwork`.",
            "cursor": "Coordinate via separate Cursor chat windows.",
            "claude_code": "Use Claude Code subagents with clear roles.",
            "codex": "Reference `agent-orchestration` in Codex context.",
            "gemini": "Invoke via `gemini run agent-orchestration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt agent-orchestration`.",
            "windsurf": "Activate `agent-orchestration` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8",
            "`.agents/skills/diagnose-plan-confirm-execute/SKILL.md`"
        ]
    },
    {
        "name": "subagent-delegation",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Delegate bounded, well-specified tasks to independent subagents with explicit inputs, tools, and acceptance criteria.",
        "purpose": "Enables primary coding agents to delegate isolated, time-consuming tasks (e.g. codebase research, log auditing, documentation drafting) to subagents, preserving primary context window and focus.",
        "when_to_use": [
            "Performing broad codebase searches or documentation surveys that would clutter primary context.",
            "Executing isolated test passes or independent script generation."
        ],
        "when_not_to_use": [
            "Architectural decision-making or critical governance approvals."
        ],
        "required_inputs": [
            "Task description, explicit inputs, allowed tool scope, and expected deliverables."
        ],
        "prerequisites": [
            "`invoke_subagent` tool availability."
        ],
        "procedure": [
            ("Task Boundary Definition", "Scope delegated task to a single, well-defined objective with unambiguous inputs and outputs."),
            ("Tool & Workspace Mode Selection", "Select subagent type (`research` for read-only codebase search, `self` for full tools). Choose workspace mode (`inherit` or `branch`)."),
            ("Structured Prompt Formulation", "Draft actionable subagent prompt detailing: Role, Background Context, Specific Steps, Prohibited Actions, and Deliverable Format."),
            ("Subagent Launch", "Invoke subagent via `invoke_subagent`. Capture returned `conversationId`."),
            ("Reactive Wakeup & Result Ingestion", "Allow background execution. Upon subagent message arrival, ingest findings into primary task context."),
            ("Deliverable Verification", "Verify subagent output against acceptance criteria before incorporating into primary plan.")
        ],
        "safety": [
            "Never delegate tasks that require unconfirmed destructive operations.",
            "Do NOT poll subagent status in a tight loop; rely on reactive wakeup."
        ],
        "deliverables": [
            "Subagent execution result and verified deliverable."
        ],
        "acceptance_criteria": [
            "Subagent prompt is specific, actionable, and bounded.",
            "Subagent returns all requested deliverables without errors.",
            "Primary context remains clean and uncluttered."
        ],
        "error_recovery": [
            "If subagent produces incomplete output, send clarifying message via `send_message`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via `invoke_subagent` or `/subagent-delegation`.",
            "cursor": "Delegate via secondary Cursor composer.",
            "claude_code": "Use Claude Code `/subagent` if supported.",
            "codex": "Reference `subagent-delegation` in Codex context.",
            "gemini": "Invoke via `gemini run subagent-delegation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt subagent-delegation`.",
            "windsurf": "Activate `subagent-delegation` in Windsurf."
        },
        "references": [
            "Antigravity Subagent System Documentation",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "parallel-execution",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Run independent verification, linting, or research tasks concurrently while strictly serializing shared file modifications.",
        "purpose": "Maximizes engineering throughput by executing non-conflicting background tasks (e.g. running pytest while compiling frontend TypeScript) in parallel while preventing file write collisions.",
        "when_to_use": [
            "Running multiple independent test suites or linters simultaneously.",
            "Conducting multi-source codebase research across decoupled modules."
        ],
        "when_not_to_use": [
            "Modifying the same files or shared database records concurrently."
        ],
        "required_inputs": [
            "List of independent, non-conflicting tasks."
        ],
        "prerequisites": [
            "Background task execution capabilities (`run_command` with async support)."
        ],
        "procedure": [
            ("Independence & Conflict Analysis", "Verify tasks have zero shared mutable state, touch disjoint file sets, and do not compete for the same network ports."),
            ("Concurrent Task Launch", "Launch independent tasks concurrently (e.g. Task A: `pytest`, Task B: `tsc --noEmit`)."),
            ("Background Task Monitoring", "Allow tasks to run in background. Rely on reactive completion notifications."),
            ("Serialized File Write Handoff", "If tasks generate file updates, serialize file writes sequentially: apply Task A changes, verify, then apply Task B changes."),
            ("Consolidated Result Synthesis", "Combine outputs and report unified completion status.")
        ],
        "safety": [
            "CRITICAL: Never run concurrent tasks that modify the same source file.",
            "Do NOT run concurrent scraper tests against the same court portal to avoid IP blocking."
        ],
        "deliverables": [
            "Consolidated results from parallel task executions.",
            "Reduced total execution duration."
        ],
        "acceptance_criteria": [
            "All parallel tasks execute without port collisions or file locks.",
            "Combined results are synthesized accurately.",
            "Total execution time is significantly lower than sequential execution."
        ],
        "error_recovery": [
            "If parallel tasks collide on database access, serialize their execution immediately."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/parallel-execution`.",
            "cursor": "Run concurrent terminal processes in Cursor.",
            "claude_code": "Execute background tasks in Claude Code.",
            "codex": "Reference `parallel-execution` in Codex context.",
            "gemini": "Invoke via `gemini run parallel-execution`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt parallel-execution`.",
            "windsurf": "Activate `parallel-execution` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Do / Must Not Do)"
        ]
    },
    {
        "name": "agent-self-review",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Require an independent, objective self-audit of code changes against requirements prior to presenting results to the user.",
        "purpose": "Mandates that AI agents audit their own code modifications against the approved plan and requirements before presenting completion, catching omitted edge cases and unintended side-effects.",
        "when_to_use": [
            "Immediately following code implementation and before notifying the user of completion.",
            "Prior to submitting an implementation plan for review."
        ],
        "when_not_to_use": [
            "During initial discovery before code exists."
        ],
        "required_inputs": [
            "Approved implementation plan, requirements checklist, git working tree diff, and test outputs."
        ],
        "prerequisites": [
            "Completed code modifications."
        ],
        "procedure": [
            ("Working Tree Diff Audit", "Run `git diff` or inspect all modified files. Verify every changed line is intentional and directly related to the approved plan."),
            ("Requirements Cross-Check", "Step through the approved plan's acceptance criteria one by one. Confirm concrete implementation and test evidence for each."),
            ("Unintended Modification Check", "Check for accidental whitespace bloat, unintended file renames, or modifications to untouched legacy code."),
            ("Error Left Behind Audit", "Check browser console, terminal logs, and linter output. Confirm zero unhandled errors or warnings remain."),
            ("Self-Correction Pass", "If any omission or discrepancy is detected, correct it immediately before user presentation."),
            ("Self-Review Certification", "Certify in the final response that the self-audit passed with 100% verification evidence.")
        ],
        "safety": [
            "CRITICAL: Never declare completion without verified test evidence.",
            "Do NOT conceal unverified items; explicitly report known limitations."
        ],
        "deliverables": [
            "Self-Review Audit Checklist with verified assertions.",
            "Clean git diff matching approved scope exactly."
        ],
        "acceptance_criteria": [
            "100% of approved plan requirements are verified in code.",
            "Git diff contains zero extraneous or accidental modifications.",
            "All linters and test suites report clean green status."
        ],
        "error_recovery": [
            "If self-review reveals an unfulfilled requirement, complete it before presenting work to the user."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/agent-self-review`.",
            "cursor": "Select `@agent-self-review` in Cursor chat.",
            "claude_code": "Prompt Claude Code: 'Conduct an objective self-review of your changes.'",
            "codex": "Reference `agent-self-review` in Codex context.",
            "gemini": "Invoke via `gemini run agent-self-review`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt agent-self-review`.",
            "windsurf": "Activate `agent-self-review` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Definition of Done & AI Agent Rules)"
        ]
    },
    {
        "name": "agent-recovery",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Resume execution safely from verified checkpoints following crashes, timeouts, context limits, or interruptions.",
        "purpose": "Provides deterministic checkpointing and gap-analysis protocols allowing an agent to resume long-running tasks seamlessly following tool timeouts, crashes, or session restarts without re-doing completed work.",
        "when_to_use": [
            "Resuming a session following an interruption, crash, or context compaction.",
            "Recovering from Celery worker or Playwright browser automation timeouts."
        ],
        "when_not_to_use": [
            "Starting a fresh project from scratch."
        ],
        "required_inputs": [
            "Approved Implementation Plan in `docs/`, git commit history, and session transcript."
        ],
        "prerequisites": [
            "Documented task checklist with checkpoint markers."
        ],
        "procedure": [
            ("State & Checkpoint Introspection", "Inspect git status and recent commits (`git log -n 5`). Determine which files were successfully committed or modified before interruption."),
            ("Implementation Plan Re-read", "Read the approved implementation plan in `docs/`. Check task checklist to identify the last verified checkpoint."),
            ("Gap Analysis & Parity Verification", "Execute test suites (`pytest`, `tsc`) on current code to confirm which previous tasks remain green and functional."),
            ("Resume Point Identification", "Identify the exact first incomplete or unverified task on the checklist."),
            ("Seamless Continuation", "Resume execution from the identified task without repeating verified steps or losing context."),
            ("Checklist State Synchronization", "Update plan checklist with current status and proceed toward completion.")
        ],
        "safety": [
            "Never assume partially modified files are complete; re-verify them before continuing.",
            "Do NOT skip ahead past incomplete tasks to make up time."
        ],
        "deliverables": [
            "Interruption Gap Analysis & Recovery Log.",
            "Resumed execution roadmap leading to completion."
        ],
        "acceptance_criteria": [
            "Exact last verified checkpoint is proven with git and test evidence.",
            "Execution resumes from the correct sequential task without lost work.",
            "Final deliverables achieve 100% of approved plan scope."
        ],
        "error_recovery": [
            "If an interrupted step left partially written corrupted files, revert the uncommitted changes and restart that single step."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/agent-recovery` or follow interruption recovery rule.",
            "cursor": "Select `@agent-recovery` in Cursor chat.",
            "claude_code": "Prompt Claude Code: 'Resume from the last verified checkpoint.'",
            "codex": "Reference `agent-recovery` in Codex context.",
            "gemini": "Invoke via `gemini run agent-recovery`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt agent-recovery`.",
            "windsurf": "Activate `agent-recovery` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Interruption Recovery)",
            "`docs/2026-10-31_uaic_universal_ai_development_workflow_skills_framework_implementation_plan_v1.md`"
        ]
    },
    {
        "name": "context-management",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Preserve critical architectural decisions, business rules, and constraints across long-running tasks while pruning transient dumps.",
        "purpose": "Curates conversational and token context during long-running tasks, pruning transient verbose terminal outputs while ensuring critical architectural decisions, invariants, and file paths are permanently retained.",
        "when_to_use": [
            "During long multi-turn sessions where context window limits approach.",
            "Responding to `/compact` slash command.",
            "Archiving large research dumps into permanent documentation in `docs/`."
        ],
        "when_not_to_use": [
            "Short 1-2 turn conversations."
        ],
        "required_inputs": [
            "Current conversational state, active task checklist, and project rule files."
        ],
        "prerequisites": [
            "Knowledge of progressive disclosure and artifact storage."
        ],
        "procedure": [
            ("Transient Dump Identification", "Identify bulky transient content (raw compiler outputs, large terminal dumps, multi-page logs) in context."),
            ("Critical Invariant Extraction", "Extract and preserve essential invariants: Implementation ID, active approved plan path, verified test counts, and pending task list."),
            ("External File Archival", "Offload bulky logs, research findings, or diagnostic dumps into persistent files in `docs/` or `scripts/`."),
            ("Context Summarization & Compaction", "Synthesize conversation context into a high-signal state brief retaining key decisions, assumptions, and next steps."),
            ("Prompt Continuity Check", "Confirm that following compaction, the agent can continue executing the active plan without loss of direction.")
        ],
        "safety": [
            "CRITICAL: Never discard approved implementation plan details, non-negotiable rules, or user constraints during compaction.",
            "Ensure file paths to all relevant documents are preserved."
        ],
        "deliverables": [
            "Compacted context brief.",
            "Persistent documentation files in `docs/` capturing offloaded data."
        ],
        "acceptance_criteria": [
            "Token footprint is significantly reduced.",
            "All critical decisions, constraints, and pending tasks are preserved.",
            "Agent continues execution with full continuity."
        ],
        "error_recovery": [
            "If context compaction loses a critical detail, re-read the approved implementation plan from `docs/`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke native slash command `/compact` or `/context-management`.",
            "cursor": "Summarize context in Cursor chat.",
            "claude_code": "Use Claude Code `/compact`.",
            "codex": "Reference `context-management` in Codex context.",
            "gemini": "Invoke via `gemini run context-management`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt context-management`.",
            "windsurf": "Activate `context-management` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8",
            "`docs/`"
        ]
    },
    {
        "name": "workflow-skill-creator",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Author new standardized, production-grade AI skills following the Universal Skills Framework structure.",
        "purpose": "Distills complex engineering runbooks, scraper workflows, or operational procedures into standardized, portable `SKILL.md` packages adhering to the 9 mandatory sections of the Universal Framework.",
        "when_to_use": [
            "Creating a new custom skill for a recurring workflow.",
            "Standardizing new domain automation procedures (e.g. adding a 9th court portal scraper)."
        ],
        "when_not_to_use": [
            "One-off tasks that will never be repeated."
        ],
        "required_inputs": [
            "Workflow procedure, triggers, exclusions, prerequisites, safety rules, and verification criteria."
        ],
        "prerequisites": [
            "Understanding of YAML frontmatter (`name:`, `description:`) and progressive disclosure."
        ],
        "procedure": [
            ("Skill Directory Scaffolding", "Create directory `.agents/skills/<skill-name>/` or `AI_WORKFLOW_LIBRARY/universal/<category>/<skill-name>/`."),
            ("YAML Frontmatter Definition", "Draft valid YAML block with lowercase hyphenated `name` and third-person actionable `description` (what it does and when to use it)."),
            ("9-Section Standard Authoring", "Author all 9 mandatory sections: 1. Purpose & Overview, 2. When to Use & When NOT to Use, 3. Required Inputs & Prerequisites, 4. Step-by-Step Procedure, 5. Safety Considerations, 6. Deliverables, 7. Acceptance Criteria, 8. Error Recovery, 9. Tool Invocation Mapping."),
            ("Helper Scripts & Resources", "Add optional helper scripts in `scripts/` or examples in `examples/` if the skill requires automated tooling."),
            ("Frontmatter & Discovery Validation", "Validate YAML syntax with `validate_skills_framework.py` and verify Antigravity/Codex discovery."),
            ("Skill Index Update", "Add new skill to `AI_WORKFLOW_LIBRARY/CATALOGUE.md` and `README.md`.")
        ],
        "safety": [
            "Never create empty `SKILL.md` files or generic placeholder text.",
            "Ensure skill names are lowercase and hyphenated without special characters."
        ],
        "deliverables": [
            "Production-grade `SKILL.md` package with all 9 standard sections.",
            "Updated catalogue and index records."
        ],
        "acceptance_criteria": [
            "Skill contains valid YAML frontmatter and all 9 required sections.",
            "Instructions are actionable, domain-specific, and fully detailed.",
            "Discovery script confirms the skill is discoverable by target AI tools."
        ],
        "error_recovery": [
            "If frontmatter YAML is malformed, use `yaml.safe_load` to identify and repair syntax errors."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/workflow-skill-creator`.",
            "cursor": "Select `@workflow-skill-creator` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `workflow-skill-creator`.",
            "codex": "Reference `workflow-skill-creator` in Codex context.",
            "gemini": "Invoke via `gemini run workflow-skill-creator`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt workflow-skill-creator`.",
            "windsurf": "Activate `workflow-skill-creator` in Windsurf."
        },
        "references": [
            "`AI_WORKFLOW_LIBRARY/README.md` - Standard Skill Format",
            "`.agents/skills/diagnose-plan-confirm-execute/SKILL.md`"
        ]
    },
    {
        "name": "workflow-migration",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Migrate legacy Robin desktop flows, custom instructions, or older prompts into portable SKILL.md packages.",
        "purpose": "Transforms legacy automation formats (such as Power Automate Desktop Robin scripts, unstructured prompt templates, or deprecated IDE rules) into modern, standardized `SKILL.md` runbooks.",
        "when_to_use": [
            "Porting legacy desktop automation subflows (`v4_subflows/`) into Python/Playwright skill specifications.",
            "Migrating deprecated prompt files into portable Agent Skills."
        ],
        "when_not_to_use": [
            "Authoring new skills from scratch."
        ],
        "required_inputs": [
            "Legacy flow scripts (`v4_subflows/*.robin`, prompt files) and target workflow objectives."
        ],
        "prerequisites": [
            "Completed `workflow-skill-creator`."
        ],
        "procedure": [
            ("Legacy Flow Inspection", "Parse legacy flow syntax (e.g. Robin actions: `WebAutomation.LaunchChrome`, `UIAutomation.Click`). Extract business rules, selector strategies, and wait intervals."),
            ("Behavioral Extraction", "Identify critical behaviors (e.g. DOM token checks, glossary filtering, date normalization) that must be preserved."),
            ("Modern Skill Scaffolding", "Scaffold standardized `SKILL.md` following the 9-section framework."),
            ("Procedure Modernization", "Translate legacy actions into modern Python Playwright procedures with explicit locators, error handlers, and timeouts."),
            ("Verification & Parity Pass", "Verify that modernized skill retains 100% behavioral equivalence with legacy flow."),
            ("Legacy Archival", "Archive legacy source in reference directory without deleting historical records.")
        ],
        "safety": [
            "Never discard subtle timing delays or verification checks present in legacy flows without understanding their purpose.",
            "Ensure output schemas remain identical to legacy specifications."
        ],
        "deliverables": [
            "Modernized `SKILL.md` package.",
            "Legacy-to-Modern Parity Matrix in `docs/`."
        ],
        "acceptance_criteria": [
            "All functional actions from legacy flow are mapped to modern procedures.",
            "Critical business invariants and error handling are preserved.",
            "Modernized skill passes automated validation."
        ],
        "error_recovery": [
            "If legacy flow contains undocumented proprietary actions, inspect runtime logs or annotated flow text (`v4_all_8_subflows_annotated.txt`)."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/workflow-migration`.",
            "cursor": "Select `@workflow-migration` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `workflow-migration`.",
            "codex": "Reference `workflow-migration` in Codex context.",
            "gemini": "Invoke via `gemini run workflow-migration`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt workflow-migration`.",
            "windsurf": "Activate `workflow-migration` in Windsurf."
        },
        "references": [
            "`v4_subflows/` - Power Automate V4 Robin Scripts",
            "`docs/v4_all_8_subflows_annotated.txt`"
        ]
    },
    {
        "name": "skill-repair",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Diagnose and repair invalid frontmatter, broken links, conflicting triggers, or malformed skill definitions.",
        "purpose": "Audits, validates, and repairs broken or non-compliant skills across `.agents/skills/` and `AI_WORKFLOW_LIBRARY/`, fixing YAML parsing errors, broken references, and overlapping trigger descriptions.",
        "when_to_use": [
            "A skill fails to be discovered by Google Antigravity or OpenAI Codex.",
            "`validate_skills_framework.py` reports YAML or structural violations.",
            "Two skills have overlapping or conflicting trigger conditions."
        ],
        "when_not_to_use": [
            "Authoring new skills from scratch."
        ],
        "required_inputs": [
            "Target skill path, error logs, and validation report."
        ],
        "prerequisites": [
            "Access to validation script `scripts/validate_skills_framework.py`."
        ],
        "procedure": [
            ("Validation Scan Execution", "Execute `python scripts/validate_skills_framework.py`. Parse error logs to identify offending skills and lines."),
            ("YAML Frontmatter Syntax Fix", "Repair malformed YAML frontmatter: ensure valid opening/closing `---`, quote descriptions containing colons, and verify `name` is lowercase hyphenated."),
            ("Mandatory Section Restoration", "If required sections are missing, insert standardized section headers and populate with substantive domain-specific instructions."),
            ("Trigger Disambiguation", "If two skills share overlapping triggers, sharpen the `description` and `When to Use` sections to establish crisp boundaries."),
            ("Link & Reference Validation", "Verify all markdown file links point to existing valid files."),
            ("Re-validation Pass", "Rerun validation script to confirm 100% clean status.")
        ],
        "safety": [
            "Never delete existing detailed instructions while repairing formatting.",
            "Do NOT alter the skill's core purpose or existing callers."
        ],
        "deliverables": [
            "Repaired, fully compliant `SKILL.md` package.",
            "Clean validation scan report with 0 errors."
        ],
        "acceptance_criteria": [
            "YAML frontmatter parses cleanly with `yaml.safe_load`.",
            "All 9 mandatory sections are present with substantive content.",
            "Skill is successfully discovered by target AI assistants."
        ],
        "error_recovery": [
            "If frontmatter repair fails, re-render using `scripts/skills_data/renderer.py`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/skill-repair`.",
            "cursor": "Select `@skill-repair` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `skill-repair`.",
            "codex": "Reference `skill-repair` in Codex context.",
            "gemini": "Invoke via `gemini run skill-repair`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt skill-repair`.",
            "windsurf": "Activate `skill-repair` in Windsurf."
        },
        "references": [
            "`scripts/validate_skills_framework.py`",
            "`AI_WORKFLOW_LIBRARY/README.md`"
        ]
    },
    {
        "name": "agy-customizations",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Inspect and maintain Google Antigravity-specific customizations, skills loading priority, rules, plugins, and hooks.",
        "purpose": "Manages Google Antigravity IDE customizations, understanding discovery precedence (Workspace `.agents/` > Global `~/.gemini/config/` > Built-in), progressive disclosure, and hook triggers.",
        "when_to_use": [
            "Configuring or troubleshooting Antigravity workspace customizations.",
            "Verifying skill discovery priority or resolving conflicts between workspace and global skills."
        ],
        "when_not_to_use": [
            "Configuring non-Antigravity tools (use respective adapter)."
        ],
        "required_inputs": [
            "Workspace `.agents/` configuration and global Antigravity config paths."
        ],
        "prerequisites": [
            "Running in Google Antigravity IDE."
        ],
        "procedure": [
            ("Discovery Precedence Audit", "Verify loading priority: 1. Workspace (`.agents/skills/`), 2. Declared (`skills.json`), 3. Global (`~/.gemini/config/`), 4. Built-in skills."),
            ("Progressive Disclosure Check", "Verify that skills in `.agents/skills/<name>/SKILL.md` expose concise YAML frontmatter `name:` and `description:` for light prompt injection."),
            ("Project Rules Verification", "Confirm project rules in `AGENTS.md`, `GEMINI.md`, and `.agents/rules/*.md` load hierarchically."),
            ("MCP Server & Tool Integration", "Inspect configured MCP servers (dak, notebooks) and verify tool schema registration."),
            ("Hook & Plugin Auditing", "Audit `hooks.json` and plugin configurations if present."),
            ("Verification & Discovery Pass", "Confirm active Antigravity session recognizes workspace skills.")
        ],
        "safety": [
            "Never overwrite built-in Antigravity tools unless deliberately shadowing with an approved workspace custom skill.",
            "Do NOT bloat the system prompt with massive un-gated rules."
        ],
        "deliverables": [
            "Antigravity Customization Audit Report.",
            "Verified workspace skill registration."
        ],
        "acceptance_criteria": [
            "Workspace skills override global/built-in counterparts predictably.",
            "Progressive disclosure injects only names and descriptions into context.",
            "Rules load hierarchically without duplication."
        ],
        "error_recovery": [
            "If Antigravity fails to discover a workspace skill, verify path is exactly `.agents/skills/<name>/SKILL.md`."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/agy-customizations` or follow built-in guide.",
            "cursor": "Not applicable (Antigravity-specific).",
            "claude_code": "Not applicable.",
            "codex": "Shares `.agents/` discovery root.",
            "gemini": "Shares `GEMINI.md` rules.",
            "github_copilot": "Not applicable.",
            "windsurf": "Not applicable."
        },
        "references": [
            "`C:\\Users\\priyer\\.gemini\\antigravity\\builtin\\skills\\agy-customizations\\SKILL.md`",
            "`AGENTS.md` - Section 8"
        ]
    },
    {
        "name": "automation",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Design, schedule, and validate recurring automated background jobs, Celery beats, and cron schedules safely.",
        "purpose": "Guides the authoring and monitoring of scheduled background tasks, recurring cron routines, and automated queue runners with safeguards against runaway loops and data corruption.",
        "when_to_use": [
            "Configuring recurring queue runners (`queue_runner.py`), retry monitors, or periodic cleanup tasks.",
            "Responding to `/schedule` or `/automation` slash commands."
        ],
        "when_not_to_use": [
            "One-time interactive commands."
        ],
        "required_inputs": [
            "Task function, schedule interval/cron expression, concurrency limits, and retry policy."
        ],
        "prerequisites": [
            "Celery Beat or scheduler capability."
        ],
        "procedure": [
            ("Schedule Specification", "Define execution cadence using cron syntax or interval (e.g. `schedule(CronExpression='*/5 * * * *')`). Avoid shell sleep commands."),
            ("Idempotency & Lock Guard", "Implement distributed Redis lock (`redis.lock`) ensuring only one instance of the automated task runs at any time."),
            ("Task Implementation", "Implement async task in `backend/app/tasks/` with bounded execution timeouts and structured logging."),
            ("Failure & Retry Handling", "Configure exponential backoff and maximum retry limits (`max_retries=3`). Route dead-letter items to alert queue."),
            ("Monitoring & Telemetry", "Expose automation health status on `/api/v1/queue/auto-mode` and `/health`."),
            ("Verification Pass", "Simulate schedule execution; verify task executes, acquires lock, commits state, and releases lock.")
        ],
        "safety": [
            "CRITICAL: Never use shell `sleep` loops as long-running schedulers.",
            "Always enforce distributed locks to prevent overlapping duplicate runs of automated tasks."
        ],
        "deliverables": [
            "Scheduled automation task with distributed lock protection.",
            "Schedule configuration in Celery Beat or scheduler service."
        ],
        "acceptance_criteria": [
            "Task triggers reliably at configured interval.",
            "Distributed locks prevent concurrent duplicate execution.",
            "Failure handling and alert dispatch function predictably."
        ],
        "error_recovery": [
            "If automated task stalls, release stale Redis lock after TTL expiration and log timeout error."
        ],
        "tool_invocations": {
            "antigravity": "Invoke native slash command `/schedule` or `/automation`.",
            "cursor": "Select `@automation` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `automation`.",
            "codex": "Reference `automation` in Codex context.",
            "gemini": "Invoke via `gemini run automation`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt automation`.",
            "windsurf": "Activate `automation` in Windsurf."
        },
        "references": [
            "`backend/app/tasks/queue_runner.py`",
            "`backend/app/core/celery_app.py`"
        ]
    },
    {
        "name": "accidental-data-loss-prevention",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "STOP AND VERIFY: Mandatory safety protocol requiring explicit user consent before running irreversible destructive actions.",
        "purpose": "Enforces a strict, non-bypassable safety gate halting any operation that could cause irreversible data loss (SQL `DROP`/`TRUNCATE`/broad `DELETE`, recursive file deletions, branch purges, cloud resource destructions) until explicit human authorization is obtained.",
        "when_to_use": [
            "BEFORE running any SQL command with `DROP`, `TRUNCATE`, or unconstrained `DELETE`.",
            "BEFORE running filesystem commands that delete directories (`rmdir /s`, `rm -rf`).",
            "BEFORE running git commands that discard work (`git reset --hard`, `git clean -fd`).",
            "BEFORE running cloud resource destructions."
        ],
        "when_not_to_use": [
            "Non-destructive read-only queries or additive file writes."
        ],
        "required_inputs": [
            "Target operation command, affected tables/files, estimated blast radius, and verified backup location."
        ],
        "prerequisites": [
            "Verified pre-operation backup exists."
        ],
        "procedure": [
            ("STOP AND VERIFY Trigger", "Immediately halt execution when an irreversible destructive action is identified."),
            ("Blast Radius Assessment", "Quantify affected records, files, or resources. Confirm whether data can be recovered."),
            ("Pre-Destruction Backup Verification", "Verify that an atomic database backup or git branch backup exists before proceeding."),
            ("Explicit User Confirmation Prompt", "Present exact command, affected target, and blast radius to the user in plain text. Ask: 'Do you authorize this irreversible deletion? [Yes/No]'."),
            ("Wait for Explicit Consent", "Wait for user confirmation. If user declines or does not confirm, abort operation immediately."),
            ("Guarded Execution & Logging", "Upon explicit confirmation, execute with strict boundaries and log action to audit trail.")
        ],
        "safety": [
            "CRITICAL NON-NEGOTIABLE: NEVER execute destructive commands without explicit user consent.",
            "Never bypass this check under any circumstances, even when running under automated goals."
        ],
        "deliverables": [
            "Authorization request and verified consent record.",
            "Audit log capturing destructive execution."
        ],
        "acceptance_criteria": [
            "Zero irreversible deletions occur without prior explicit user consent.",
            "Verified backup exists before destructive action executes.",
            "All actions logged with user consent timestamp."
        ],
        "error_recovery": [
            "If accidental deletion occurs, halt all activity immediately and restore from pre-destruction backup."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/accidental-data-loss-prevention` or follow global safety rule.",
            "cursor": "Select `@accidental-data-loss-prevention` in Cursor.",
            "claude_code": "Mandated by `CLAUDE.md` safety guidelines.",
            "codex": "Mandated by `AGENTS.md` safety rules.",
            "gemini": "Mandated by `GEMINI.md` guidelines.",
            "github_copilot": "Invoke via Copilot Chat `/prompt accidental-data-loss-prevention`.",
            "windsurf": "Activate `accidental-data-loss-prevention` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Must Not Do)",
            "`C:\\Users\\priyer\\.gemini\\config\\skills\\accidental-data-loss-prevention\\SKILL.md`"
        ]
    },
    {
        "name": "final-delivery-audit",
        "category_code": "I",
        "category_name": "Agent Management & Automation",
        "description": "Conduct comprehensive pre-handover verification: automated test evidence, documentation sync, limitation logs, and rollback instructions.",
        "purpose": "Governs the final delivery audit of an engineering task or release, ensuring that all acceptance criteria are met, test suites pass with 100% success rate, documentation is synchronized, and known limitations are transparently reported.",
        "when_to_use": [
            "Concluding any substantial engineering implementation task.",
            "Preparing the final delivery report for the user."
        ],
        "when_not_to_use": [
            "Mid-flight execution of intermediate work packages."
        ],
        "required_inputs": [
            "Approved implementation plan, all test outputs (`pytest`, `tsc`, `ps1`), git diff, and updated documentation."
        ],
        "prerequisites": [
            "All code changes implemented and tested."
        ],
        "procedure": [
            ("Acceptance Criteria Audit", "Compare final codebase against every single requirement in the approved plan. Confirm 100% completion."),
            ("Full Test Suite Verification", "Run full test suite: `pytest -q`, `tsc --noEmit`, `check_ps1_syntax.ps1`, `ruff check`. Confirm 0 errors."),
            ("Documentation Synchronization Audit", "Verify `README.md`, `AGENTS.md`, and relevant subsystem guides reflect all newly added components."),
            ("Known Limitations & Gaps Cataloguing", "Document any deliberate scope boundaries, environment-specific limitations, or future recommendations."),
            ("Rollback Instructions Verification", "Provide explicit, copy-pasteable rollback instructions in the final report."),
            ("Final Delivery Report Generation", "Publish comprehensive Final Delivery Report summarizing accomplishments, test evidence, and handover instructions.")
        ],
        "safety": [
            "CRITICAL: Never claim completion without actual automated test evidence.",
            "Always report limitations honestly; never conceal unverified paths."
        ],
        "deliverables": [
            "Comprehensive Final Delivery Report in conversation output and `docs/`.",
            "Verified green test suite logs."
        ],
        "acceptance_criteria": [
            "All planned deliverables are confirmed complete with evidence.",
            "100% of test suites pass cleanly.",
            "Documentation is fully synchronized and rollback instructions provided."
        ],
        "error_recovery": [
            "If any requirement is found incomplete during final audit, resume implementation before declaring completion."
        ],
        "tool_invocations": {
            "antigravity": "Invoke via chat: `/final-delivery-audit`.",
            "cursor": "Select `@final-delivery-audit` in Cursor chat.",
            "claude_code": "Prompt Claude Code with `final-delivery-audit`.",
            "codex": "Reference `final-delivery-audit` in Codex context.",
            "gemini": "Invoke via `gemini run final-delivery-audit`.",
            "github_copilot": "Invoke via Copilot Chat `/prompt final-delivery-audit`.",
            "windsurf": "Activate `final-delivery-audit` in Windsurf."
        },
        "references": [
            "`AGENTS.md` - Section 8 (Definition of Done)",
            "`docs/WALKTHROUGH.md`"
        ]
    }
]

