# UAIC Project Skill Registry

> **Purpose:** Single routing index mapping every task type to the exact skill identifier, supporting skills, and approval requirements.
> **AI OS Component:** Used by `project-task-router` skill to automatically select workflows.
> **Last Updated:** 2026-11-03 (`IMP-2026-1103-002`)

---

## How to Use This Registry

1. Classify the user request into one of the task categories below
2. Read the **Primary Skill** `SKILL.md` for exact execution steps
3. Invoke **Supporting Skills** as directed by the primary skill
4. Check **Approval Required** — never implement without plan approval when YES
5. After completion, update `.agent/CHANGELOG.md`

---

## Master Skill Routing Table

| # | Task Category | Primary Skill | Supporting Skills | Approval Required | Data Risk |
|---|---|---|---|---|---|
| 1 | **Requirements analysis** | `requirement-analysis` | `grill-me`, `business-process-analysis` | NO | None |
| 2 | **Architecture review** | `architecture-analysis` | `impact-analysis`, `architecture-decision-record` | NO | None |
| 3 | **Gap analysis** | `requirement-gap-analysis` | `existing-system-assessment` | NO | None |
| 4 | **Backend bug fix** | `diagnose-plan-confirm-execute` | `diagnose-issue`, `fix-runtime-errors`, `error-reproduction`, `unit-testing`, `regression-testing` | **YES** | Low |
| 5 | **Frontend bug fix** | `diagnose-plan-confirm-execute` | `fix-ui-issues`, `fix-console-errors`, `fix-build-errors` | **YES** | None |
| 6 | **API bug fix** | `diagnose-plan-confirm-execute` | `fix-api-errors`, `api-testing` | **YES** | Low |
| 7 | **Database bug fix** | `diagnose-plan-confirm-execute` | `fix-database-errors`, `database-testing` | **YES** | **HIGH** |
| 8 | **Browser automation bug fix** | `uaic-browser-automation` | `diagnose-plan-confirm-execute`, `uaic-captcha-handling`, `uaic-data-validation` | **YES** | Low |
| 9 | **New API endpoint** | `backend-development` | `api-development`, `api-testing`, `documentation-sync` | **YES** | Low |
| 10 | **New frontend route/page** | `frontend-development` | `component-development`, `theme-system`, `responsive-ui-development`, `accessibility-implementation` | **YES** | None |
| 11 | **New React component** | `component-development` | `theme-system`, `accessibility-implementation` | **YES** | None |
| 12 | **UI/UX redesign** | `frontend-development` | `theme-system`, `design-system`, `responsive-ui-development`, `accessibility-audit`, `ui-ux-testing` | **YES** | None |
| 13 | **Design system update** | `design-system` | `theme-system`, `component-development` | **YES** | None |
| 14 | **Database schema change** | `database-migration` | `database-design`, `database-testing`, `database-backup-restore` | **YES + BACKUP** | **HIGH** |
| 15 | **New database model** | `database-design` | `database-migration`, `database-testing` | **YES** | Medium |
| 16 | **Third-party API integration** | `api-integration` | `api-development`, `api-testing`, `security-audit` | **YES** | Medium |
| 17 | **Guidewire integration change** | `uaic-guidewire-integration` | `api-integration`, `api-testing` | **YES** | Medium |
| 18 | **Scraper change (portal)** | `uaic-browser-automation` | `uaic-captcha-handling`, `uaic-data-validation`, `uaic-eight-portal-validation`, `e2e-testing` | **YES** | Low |
| 19 | **CAPTCHA handling change** | `uaic-captcha-handling` | `uaic-browser-automation`, `uaic-attended-mode` | **YES** | Low |
| 20 | **Fuzzy matching change** | `uaic-fuzzy-matching` | `unit-testing`, `regression-testing` | **YES** | Low |
| 21 | **Queue/Celery change** | `uaic-queue-management` | `backend-development`, `integration-testing` | **YES** | Medium |
| 22 | **Notification system change** | `backend-development` | `api-testing`, `integration-testing` | **YES** | Low |
| 23 | **Settings system change** | `uaic-settings-validation` | `backend-development`, `integration-testing` | **YES** | Low |
| 24 | **Export/import change** | `backend-development` | `api-testing`, `database-testing` | **YES** | Medium |
| 25 | **Security fix/audit** | `security-audit` | `security-testing`, `diagnose-plan-confirm-execute` | **YES** | Varies |
| 26 | **Performance optimization** | `performance-optimization` | `root-cause-analysis`, `performance-testing` | **YES** | Low |
| 27 | **Accessibility fix** | `accessibility-implementation` | `accessibility-audit`, `accessibility-testing` | **YES** | None |
| 28 | **New unit tests** | `unit-testing` | `test-coverage-analysis` | NO | None |
| 29 | **New integration tests** | `integration-testing` | `api-testing`, `database-testing` | NO | None |
| 30 | **New E2E tests** | `e2e-testing` | `browser-testing`, `uaic-attended-mode` | NO | None |
| 31 | **Documentation update** | `documentation-sync` | `technical-documentation`, `readme-generation` | NO | None |
| 32 | **README update** | `readme-generation` | `documentation-sync` | NO | None |
| 33 | **Dependency update** | `dependency-analysis` | `dependency-cleanup`, `regression-testing` | **YES** | Medium |
| 34 | **Code refactoring** | `code-refactoring` | `code-review`, `regression-testing` | **YES** | Low |
| 35 | **Code cleanup / dead code** | `dead-code-removal` | `code-cleanup`, `regression-testing` | **YES** | Low |
| 36 | **Docker/deployment change** | `docker-setup` | `deployment-validation`, `deployment-documentation` | **YES** | Medium |
| 37 | **PowerShell script change** | `local-setup` | `environment-setup` | **YES** | Low |
| 38 | **Production deployment** | `production-deployment` | `deployment-validation`, `database-backup-restore`, `rollback-deployment` | **YES — EXPLICIT AUTH** | **HIGH** |
| 39 | **Production incident** | `agent-recovery` | `diagnose-issue`, `root-cause-analysis` | IMMEDIATE | **HIGH** |
| 40 | **New skill creation** | `workflow-skill-creator` | `skill-repair` | NO (after review) | None |
| 41 | **Skill repair** | `skill-repair` | `agy-customizations` | NO | None |
| 42 | **Multi-agent task** | `teamwork` | `subagent-delegation`, `agent-orchestration` | **YES** | Varies |
| 43 | **Context compaction** | `context-management` | — | NO | None |
| 44 | **Data loss risk detected** | `accidental-data-loss-prevention` | — | **YES — IMMEDIATE STOP** | **CRITICAL** |

---

## UAIC-Specific Skill Quick Reference

| Skill ID | Purpose | When to Use |
|---|---|---|
| `uaic-orchestrator-context` | Full UAIC architectural context | Starting any UAIC-specific session |
| `uaic-browser-automation` | Playwright scraper development | Any scraper modification |
| `uaic-captcha-handling` | CAPTCHA + AntiCaptcha extension | CAPTCHA resolution issues |
| `uaic-data-validation` | Portal output schema validation | Checking extracted court case data |
| `uaic-fuzzy-matching` | RapidFuzz cascade validation | Fuzzy match logic changes |
| `uaic-guidewire-integration` | Guidewire payload construction | Guidewire integration changes |
| `uaic-queue-management` | Celery queue operations | Queue/worker issues |
| `uaic-eight-portal-validation` | All 8 portal test harness | Full portal regression |
| `uaic-attended-mode` | Visible Chrome browser execution | Live browser testing with recording |
| `uaic-unattended-mode` | Headless browser execution | Background headless testing |
| `uaic-settings-validation` | Settings → runtime validation | Settings page changes |
| `uaic-requirement-validation` | V4 Robin behavioral compliance | Any scraper behavior change |
| `uaic-recording-management` | Browser recording organization | Managing docs/recordings/ |
| `uaic-project-analysis` | Deep codebase analysis | Major architectural changes |
| `fl-broward-workflow` | Broward-specific workflow | Broward scraper work |
| `uaic-bot-orchestration` | Multi-tab Chrome orchestration | Session runner changes |

---

## Skill Location Index

All 147 installed skills are in: `d:\scratch\Bot_UAIC\.agents\skills\<skill-name>\SKILL.md`

Additional reference documentation: `d:\scratch\Bot_UAIC\AI_WORKFLOW_LIBRARY\CATALOGUE.md`

System-level Antigravity skills: `C:\Users\priyer\.gemini\config\`

