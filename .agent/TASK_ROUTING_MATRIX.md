# UAIC Task Routing Matrix

> **Purpose:** 27-category task classification with routing logic, intent keywords, and decision trees.
> **Used by:** `project-task-router` skill
> **Last Updated:** 2026-11-03 (`IMP-2026-1103-002`)

---

## Task Classification Decision Tree

```
User Request
    ↓
[1] Is this DESTRUCTIVE or DATA-AT-RISK?
    YES → Invoke accidental-data-loss-prevention FIRST → then route normally
    NO  → Continue
    ↓
[2] Is this an EMERGENCY / PRODUCTION INCIDENT?
    YES → agent-recovery → diagnose-issue → root-cause-analysis
    NO  → Continue
    ↓
[3] Classify into one of 27 categories (see table below)
    ↓
[4] Look up skill chain in PROJECT_SKILL_REGISTRY.md
    ↓
[5] Check approval threshold
    ↓
[6] Execute: Understand → Plan → Confirm → Implement → Test → Document
```

---

## 27-Category Routing Table

### Category 1: Requirements & Analysis

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Requirements analysis | "what should", "requirements", "user story", "acceptance criteria", "scope", "feature spec" | `requirement-analysis` → `grill-me` (if ambiguous) | NO |
| Architecture review | "how does", "architecture", "design", "structure", "diagram", "component" | `architecture-analysis` → `architecture-decision-record` | NO |
| Gap analysis | "what's missing", "what's broken", "what's incomplete", "gaps", "current state" | `requirement-gap-analysis` → `existing-system-assessment` | NO |

---

### Category 2: UI/UX

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| UI bug fix | "looks wrong", "display issue", "layout broken", "not rendering", "visual bug", "CSS", "style" | `diagnose-plan-confirm-execute` → `fix-ui-issues` → `fix-console-errors` | YES |
| UI redesign / enhancement | "redesign", "improve UI", "make it look better", "update the design", "modernize" | `frontend-development` → `theme-system` → `design-system` → `responsive-ui-development` → `accessibility-audit` | YES |
| New component | "add a component", "create a [button/table/modal/card]", "new UI element" | `component-development` → `theme-system` → `accessibility-implementation` | YES |
| Accessibility | "a11y", "accessibility", "screen reader", "keyboard nav", "WCAG", "contrast" | `accessibility-audit` → `accessibility-implementation` → `accessibility-testing` | YES |
| Responsive layout | "mobile", "tablet", "responsive", "viewport", "breakpoint" | `responsive-ui-development` → `mobile-testing` | YES |
| Theme/Design system | "dark mode", "light mode", "theme", "colors", "tokens", "branding" | `theme-system` → `design-system` | YES |

---

### Category 3: Frontend Development

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| New route/page | "add a page", "new route", "create a [page name] page" | `frontend-development` → `component-development` → `theme-system` → `responsive-ui-development` | YES |
| Frontend state/data | "state management", "API call", "data fetching", "React Query", "loading state", "error state" | `frontend-development` → `fix-runtime-errors` | YES |
| TypeScript errors | "TypeScript error", "tsc fails", "type error", "TS2xxx" | `fix-build-errors` → `coding-standards` | YES |
| Build errors | "build fails", "npm build error", "webpack", "next build" | `fix-build-errors` | YES |
| Console errors | "console error", "unhandled rejection", "React warning", "CORS" | `fix-console-errors` | YES |

---

### Category 4: Backend Development

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Backend bug fix | "API error", "500 error", "Python exception", "endpoint fails", "server crash" | `diagnose-plan-confirm-execute` → `fix-runtime-errors` → `unit-testing` | YES |
| New API endpoint | "add an endpoint", "create an API", "new route in backend", "new API method" | `backend-development` → `api-development` → `api-testing` → `documentation-sync` | YES |
| API integration | "integrate with", "connect to", "third-party API", "webhook", "external service" | `api-integration` → `api-testing` → `security-audit` | YES |
| Business logic | "business rule", "calculation", "logic change", "processing" | `backend-development` → `unit-testing` → `regression-testing` | YES |

---

### Category 5: Database

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Schema change | "add column", "new table", "migration", "schema update", "database change" | `database-migration` → `database-design` → `database-testing` → `database-backup-restore` | YES + BACKUP |
| Data issue | "data wrong", "corrupt data", "missing records", "database error", "constraint violation" | `fix-database-errors` → `root-cause-analysis` | YES |
| Performance (DB) | "slow query", "database slow", "N+1", "missing index" | `performance-optimization` → `database-design` | YES |

---

### Category 6: RPA & Browser Automation

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Scraper change | "scraper", "portal", "court website", "broward", "hillsborough", "miami", "dallas", "travis", "harris" | `uaic-browser-automation` → `uaic-data-validation` → `uaic-eight-portal-validation` | YES |
| CAPTCHA issue | "captcha", "anticaptcha", "reCAPTCHA", "turnstile", "blocked", "challenge" | `uaic-captcha-handling` → `uaic-browser-automation` | YES |
| WAF/Rate limit | "rate limited", "blocked", "WAF", "PerimeterX", "429", "cooldown" | `uaic-browser-automation` → `uaic-captcha-handling` | YES |
| Session/browser issue | "browser crash", "session expired", "popup", "modal", "timeout" | `uaic-browser-automation` → `fix-runtime-errors` | YES |
| Full bot orchestration | "run all bots", "orchestrate", "all 8 portals", "session runner" | `uaic-bot-orchestration` → `uaic-attended-mode` or `uaic-unattended-mode` | YES |

---

### Category 7: Queue & Workers

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Celery issue | "celery", "worker", "task queue", "stuck task", "failed task", "queue" | `uaic-queue-management` → `fix-runtime-errors` | YES |
| Retry logic | "retry", "re-queue", "re-run", "failed claims" | `uaic-queue-management` → `backend-development` | YES |

---

### Category 8: Integrations

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Guidewire | "guidewire", "push to guidewire", "CaseItems", "guidewire payload" | `uaic-guidewire-integration` → `api-testing` | YES |
| Email/Notifications | "email", "SMTP", "notification", "alert", "MailDev" | `backend-development` → `api-testing` | YES |
| Settings | "settings", "configuration", "headless mode", "timeout", "threshold" | `uaic-settings-validation` → `backend-development` | YES |

---

### Category 9: Testing & QA

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Run tests | "run tests", "pytest", "test suite", "test results" | Execute test commands directly (no skill needed) | NO |
| Add unit tests | "add tests", "write tests", "test coverage", "untested" | `unit-testing` → `test-coverage-analysis` | NO |
| Add E2E tests | "end-to-end test", "E2E", "browser test", "Playwright test" | `e2e-testing` → `browser-testing` | NO |
| Fix failing tests | "test fails", "broken test", "test error" | `diagnose-plan-confirm-execute` → `error-reproduction` | YES |
| Regression testing | "regression", "make sure nothing broke", "verify baseline" | `regression-testing` | NO |

---

### Category 10: Security

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Security audit | "security", "vulnerability", "OWASP", "injection", "XSS", "auth", "credentials exposed" | `security-audit` → `security-testing` | YES |
| Credential leak | "API key exposed", "password in code", "secret in log" | `accidental-data-loss-prevention` → `security-audit` | **IMMEDIATE STOP** |

---

### Category 11: Performance

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Performance profiling | "slow", "latency", "performance", "benchmark", "memory leak", "CPU" | `performance-optimization` → `root-cause-analysis` → `performance-testing` | YES |
| Load testing | "load test", "concurrent users", "stress test" | `load-testing` → `performance-testing` | YES |

---

### Category 12: Deployment & DevOps

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Docker change | "docker", "docker-compose", "container", "image", "noVNC" | `docker-setup` → `deployment-validation` | YES |
| Local setup | "setup_local.ps1", "launcher", "startup", "services not starting" | `local-setup` → `environment-setup` | YES |
| Production deployment | "deploy to production", "release", "go live" | `production-deployment` → `deployment-validation` → `rollback-deployment` | **YES — EXPLICIT AUTH** |

---

### Category 13: Documentation

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| Documentation update | "update docs", "document this", "add to README", "write guide" | `documentation-sync` → `technical-documentation` | NO |
| README update | "update README", "README is outdated" | `readme-generation` → `documentation-sync` | NO |
| Architecture docs | "architecture diagram", "document the design", "flowchart" | `architecture-documentation` | NO |

---

### Category 14: Agent & Skill Engineering

| Category | Intent Keywords | Skill Chain | Plan Required |
|---|---|---|---|
| New skill | "create a skill", "add a workflow", "new skill for" | `workflow-skill-creator` | NO (after review) |
| Repair skill | "skill is broken", "skill not working", "fix the skill" | `skill-repair` → `agy-customizations` | NO |
| Multi-agent work | "teamwork", "parallel agents", "coordinate agents" | `teamwork` → `subagent-delegation` → `agent-orchestration` | YES |

---

## Routing Escalation Rules

| Situation | Action |
|---|---|
| Request is ambiguous | Use `grill-me` to clarify before routing |
| Multiple categories apply | Use the most specific category; invoke supporting skills from all relevant categories |
| Task affects 3+ modules | Use `impact-analysis` first |
| Task involves production data | Invoke `accidental-data-loss-prevention` first, then route |
| Production incident | Skip planning phase → immediate `agent-recovery` + `diagnose-issue` |
| Skill not found for task | Check `AI_WORKFLOW_LIBRARY/CATALOGUE.md` for alternatives; create new skill only if justified |

---

## Quality Gate Enforcement

Every task — regardless of category — must complete this quality gate before declaring Done:

```
[ ] ruff check — 0 errors        (if Python changed)
[ ] pytest — 0 failed            (if Python changed)
[ ] tsc --noEmit — 0 errors      (if TypeScript changed)
[ ] npm run lint — 0 warnings    (if TypeScript changed)
[ ] ps1 syntax check — 0 errors  (if .ps1 changed)
[ ] Documentation updated
[ ] .agent/CHANGELOG.md updated
[ ] No stale task status (no "In Progress" left behind)
```

