# AI Tool Compatibility Matrix

**Version:** 1.0  
**Audit Date:** 31 October 2026  
**Evaluated AI Coding Tools:**
1. **Google Antigravity** (Active Tool)
2. **Cursor**
3. **Claude Code**
4. **OpenAI Codex**
5. **Gemini CLI**
6. **GitHub Copilot**
7. **Windsurf**

---

## Tool-Wise Mechanism & Discovery Summary

| AI Tool | Native Instruction File | Skills Discovery Location | Invocation Syntax | Progressive Disclosure Support |
|---|---|---|---|---|
| **Google Antigravity** | `AGENTS.md`, `GEMINI.md`, `.agents/rules/*.md` | `.agents/skills/<name>/SKILL.md` | Slash command or skill name mention | **Full native support** (Name + Desc injected; body loaded on demand) |
| **Cursor** | `.cursorrules`, `.cursor/rules/*.mdc` | `.cursor/rules/`, `.cursor/skills/` | `@skill-name` or rule match | Rule-based activation |
| **Claude Code** | `CLAUDE.md` | `CLAUDE.md`, `.claude/` | Direct prompt reference | Prompt-level progressive loading |
| **OpenAI Codex** | `AGENTS.md` | `.agents/skills/<name>/SKILL.md` | Repository context injection | Directory traversal |
| **Gemini CLI** | `GEMINI.md` | `.gemini/`, `.agents/skills/` | `gemini run <skill>` or prompt | Markdown context |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/prompts/*.prompt.md` | `/prompt <name>` in Copilot Chat | Reusable prompt files |
| **Windsurf** | `.windsurfrules` | `.windsurf/workflows/` | Cascade rule or workflow prompt | Cascade context |

---

## Complete 145-Skill Compatibility & Classification Matrix

Legend:
- `[NATIVE]`: Capability implemented natively by the AI product itself.
- `[CUSTOM SKILL]`: Installed as a portable `SKILL.md` runbook package.
- `[PROJECT RULE]`: Enforced via persistent repository instruction file (`AGENTS.md`, `CLAUDE.md`, etc.).
- `[ADAPTER]`: Product-specific wrapper or translation mapping.
- `[NOT SUPPORTED]`: Feature not natively present in the target tool (manual fallback documented).

| Skill Identifier | Google Antigravity | Cursor | Claude Code | OpenAI Codex | Gemini CLI | GitHub Copilot | Windsurf |
|---|---|---|---|---|---|---|---|
| `project-discovery` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `project-deep-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `requirement-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `requirement-gap-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `grill-me` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `business-process-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `existing-system-assessment` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `architecture-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `dependency-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `impact-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `technical-feasibility` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `project-documentation-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `diagnose-plan-confirm-execute` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `implementation-plan` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `wbs-creation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `effort-estimation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `milestone-planning` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `task-breakdown` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `dependency-planning` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `risk-assessment` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `solution-design` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `architecture-decision-record` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `execution-tracking` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `teamwork` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `project-status-report` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `website-creation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `full-stack-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `frontend-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `backend-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `database-design` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `database-migration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `api-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `api-integration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `authentication-authorization` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `multi-tenant-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `responsive-ui-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `design-system` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `theme-system` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `component-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `form-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `dashboard-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `admin-panel-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `mobile-app-development` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `accessibility-implementation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `internationalization` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `code-review` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `code-refactoring` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `code-cleanup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `duplicate-code-detection` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `technical-debt-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `performance-optimization` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `memory-optimization` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `error-handling` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `logging-observability` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `security-audit` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `accessibility-audit` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `dead-code-removal` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `dependency-cleanup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `code-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `coding-standards` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `test-strategy` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `unit-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `integration-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `e2e-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `browser-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `ui-ux-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `api-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `database-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `regression-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `cross-browser-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `mobile-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `accessibility-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `performance-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `load-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `security-testing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `bug-hunting` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `test-coverage-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `full-application-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `diagnose-issue` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `debug-application` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-build-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-runtime-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-console-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-terminal-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-api-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-database-errors` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-ui-issues` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fix-integration-issues` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `root-cause-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `error-reproduction` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `automated-bug-fixing` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `environment-setup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `local-setup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `docker-setup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `ci-cd-setup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `deployment-planning` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `production-deployment` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `staging-deployment` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `environment-configuration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `database-backup-restore` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `deployment-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `rollback-deployment` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `infrastructure-as-code` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `monitoring-setup` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `release-management` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `readme-generation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `technical-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `api-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `database-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `architecture-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `deployment-documentation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `developer-onboarding` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `project-booklet` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `knowledge-capture` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `learn` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `documentation-sync` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `agent-orchestration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `subagent-delegation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `parallel-execution` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `agent-self-review` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `agent-recovery` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `context-management` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `workflow-skill-creator` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `workflow-migration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `skill-repair` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `agy-customizations` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `automation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `accidental-data-loss-prevention` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `final-delivery-audit` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-orchestrator-context` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-project-analysis` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-requirement-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-bot-orchestration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-browser-automation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-attended-mode` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-unattended-mode` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-captcha-handling` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-fuzzy-matching` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-guidewire-integration` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-data-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-queue-management` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-settings-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-eight-portal-validation` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `uaic-recording-management` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `fl-broward-workflow` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
| `managing-python-dependencies` | `CUSTOM SKILL` | `CUSTOM RULE` | `INSTRUCTION` | `CUSTOM SKILL` | `CUSTOM SKILL` | `PROMPT FILE` | `WORKFLOW` |
