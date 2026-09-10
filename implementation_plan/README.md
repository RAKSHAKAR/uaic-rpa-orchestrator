# implementation_plan/ — Documentation System Guide

This directory is the **permanent implementation audit and history record** for the UAIC Claim & RPA Orchestrator project.

It answers: *"What did we plan, change, test, validate, and verify for each piece of work?"*

> **This is different from `README.md` (which is the living technical booklet of the entire project).**

---

## Purpose

Every substantial engineering task leaves behind enough documentation that, months later, another engineer can understand:

- What was requested
- What was investigated
- What was diagnosed
- What gaps were found
- What was planned
- What the user approved
- What was actually implemented
- What changed from the original plan
- What files were modified
- What tests were executed
- What passed / failed
- What remains unresolved
- When the work occurred
- Which version/revision of the plan was used
- Whether the implementation was verified by the user

---

## Directory Structure

```text
implementation_plan/
│
├── 2026-09-06_uaic_multi-concurrency-live-queue-and-dashboard-overhaul_implementation-plan_v1.md
├── 2026-09-06_uaic_multi-concurrency-live-queue-and-dashboard-overhaul_implementation-record_v1.md
├── 2026-09-06_uaic_multi-concurrency-live-queue-and-dashboard-overhaul_walkthrough_v1.md
├── 2026-09-06_uaic_dashboard-live-queue-and-order-orchestration_implementation-plan_v1.md
├── 2026-09-06_uaic_dashboard-live-queue-and-order-orchestration_implementation-record_v1.md
├── 2026-09-06_uaic_dashboard-live-queue-and-order-orchestration_walkthrough_v1.md
├── 2026-09-05_uaic_consolidated-issues-and-validation_implementation-plan_v1.md
├── 2026-09-05_uaic_consolidated-issues-and-validation_implementation-record_v1.md
├── 2026-09-05_uaic_consolidated-issues-and-validation_walkthrough_v1.md
├── ...
│
├── Recording/                             ← Mandatory repository home for all browser session videos (.webp)
│   ├── dashboard_fleet_demo_*.webp
│   ├── dashboard_live_queue_demo_*.webp
│   └── ...
│
├── Images/                                ← Mandatory repository home for all UI verification screenshots (.png)
│   ├── parallel_concurrency_settings_*.png
│   ├── dashboard_live_queue_*.png
│   ├── claims_register_tabs_*.png
│   └── ...
│
├── implementation_plan.md                 ← Current Active Plan (IDE quick access)
├── walkthrough.md                         ← Current Active Walkthrough (IDE quick access)
│
├── ChatGPT_Prompt/                        ← Protected original user prompt requirements
│   ├── ManualPrompt.txt
│   ├── MASTER IMPLEMENTATION PROMPT_1.md
│   ├── MASTER IMPLEMENTATION, CORRECTION, VALIDATION & PRODUCTIONIZATION PROMPT.md
│   ├── MANDATORY RESPONSIVE UI-UX REDESIGN & FULL-VIEWPORT IMPLEMENTATION.md
│   ├── PYTHON 3.14.7 — RUNTIME, LIBRARY, PERFORMANCE & MODERNIZATION UPDATE.md
│   ├── Scraped Public Court Cases — Data Format Validation, Guidewire Compatibility & UI-UX Redesign.md
│   └── UAIC Claim & RPA Orchestrator — Final Production Readiness, Bug Elimination & Hardening Directive.md
│
└── README.md                              ← THIS FILE — documentation system guide
```

---

## Documentation Lifecycle

All engineering documentation (Implementation Plans, Gap Analyses, Walkthroughs, Implementation Records) is stored **directly in `implementation_plan/`** in the repository workspace.

```text
AI Generated & Proposed
     ↓
User Approval & Confirmation
     ↓
Implementation & Comprehensive Automated Testing
     ↓
Walkthrough & Implementation Record saved in implementation_plan/
     ↓
Human Verification
```

---

## Naming Convention

```text
YYYY-MM-DD_<project-or-module>_<feature-or-task>_<document-type>_v<version>.md
```

**Examples:**
```
2026-09-05_uaic_directory-restructure_implementation-plan_v1.md
2026-09-05_uaic_branding-page_gap-analysis_v1.md
2026-09-05_uaic_fuzzy-engine-fix_test-report_v1.md
2026-09-05_uaic_guidewire-auth_walkthrough_v1.md
2026-09-05_uaic_portal-broward_change-log_v1.md
2026-09-05_uaic_setup-scripts_validation_v1.md
```

**Avoid:** `plan.md`, `notes.md`, `final.md`, `temp.md`, `updated.md`, `new.md`

---

## Implementation ID Convention

Every substantial implementation must have a unique identifier:

```text
IMP-YYYY-MMDD-NNN
```

**Examples:**
```
IMP-2026-0905-001   ← First task on September 5, 2026
IMP-2026-0905-002   ← Second task on same day
IMP-2026-0906-001   ← First task on September 6, 2026
```

This identifier appears in **all related documents** to create traceability.

---

## Required Document Metadata

Every implementation document must contain this header:

```markdown
# [Document Title]

Implementation ID:   IMP-YYYY-MMDD-NNN
Project:             UAIC Claim & RPA Orchestrator
Module:              [backend | frontend | automation | database | scripts | config]
Feature / Issue:     [Short description]
Document Type:       Implementation Plan | Gap Analysis | Walkthrough | Change Log | Test Report | Validation
Version:             v1
Status:              Awaiting Approval | Approved | In Progress | Implemented | Testing | Completed | Blocked
Created:             YYYY-MM-DD
Last Updated:        YYYY-MM-DD
AI Agent:            [Antigravity / Claude / Gemini]
Approval Status:     Pending | Approved | Rejected
Approved By:         Pending | User
Approval Date:       Pending | YYYY-MM-DD
Verification Status: AI Generated — Awaiting Human Verification | Human Verified | Rejected | Superseded | Archived
```

---

## Document Types

| Type | Purpose |
|------|---------|
| `implementation-plan` | Requirement, diagnosis, proposed solution, tasks, files, dependencies, testing plan, acceptance criteria, risks |
| `gap-analysis` | Current state vs expected state, missing/broken functionality, architectural/security/testing gaps |
| `walkthrough` | Actual implemented workflow — user journey, API flow, backend flow, database flow, UI flow |
| `change-log` | Original plan vs actual implementation, deviations, files changed, reasons |
| `test-report` | Tests executed, commands, results, failures, fixes, retest results |
| `validation` | Acceptance criteria evidence, manual/automated validation, regression validation, unresolved items |

---

## Document Status Values

```text
AI Generated                 ← Just created by AI
Awaiting Approval            ← Shown to user, waiting for go-ahead
Approved                     ← User explicitly approved
In Progress                  ← Implementation underway
Implemented                  ← Code changes complete
Testing                      ← Tests being executed
Validated                    ← Acceptance criteria verified
Awaiting Human Verification  ← Implementation done, docs pending human review
Human Verified               ← User has explicitly verified (only user can set this)
Rejected                     ← User rejected the plan
Superseded                   ← A newer version replaced this
Corrected                    ← Errors were fixed in a new version
Archived                     ← Historical record, no longer active
```

> **The AI MUST NEVER mark a document `Human Verified` itself.**

---

## Versioning

When a plan materially changes, create a new version file:

```
2026-09-05_uaic_feature_implementation-plan_v1.md   ← Initial
2026-09-05_uaic_feature_implementation-plan_v2.md   ← After scope change
2026-09-05_uaic_feature_implementation-plan_v3.md   ← Final approved
```

For minor corrections, update in-place with a Revision History section:

```markdown
## Revision History

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1 | 2026-09-05 | Initial plan | Initial diagnosis |
| v2 | 2026-09-05 | Added auth | Security gap found |
```

---

## Legacy Files (Pre-Governance)

The files directly in `implementation_plan/` and in `New folder/` were created before this governance system existed. They use the old naming style (`implementation_plan_N.md`, `gap_analysis_N.md`, etc.).

**These files must not be deleted.** They are part of the project's historical record.

When looking at historical context, check both legacy and new governance documents.

---

## One Source of Truth

For each implementation, maintain a clear relationship between documents using the Implementation ID:

```text
Implementation Plan (IMP-YYYY-MMDD-NNN)
       ↓
Gap Analysis (IMP-YYYY-MMDD-NNN)
       ↓
Approved Plan (IMP-YYYY-MMDD-NNN)
       ↓
Implementation (IMP-YYYY-MMDD-NNN)
       ↓
Change Log (IMP-YYYY-MMDD-NNN)
       ↓
Test Report (IMP-YYYY-MMDD-NNN)
       ↓
Validation (IMP-YYYY-MMDD-NNN)
       ↓
Final Status (IMP-YYYY-MMDD-NNN)
```

All documents sharing the same `IMP-YYYY-MMDD-NNN` form one complete implementation record.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Harmful |
|---|---|
| `final.md`, `new.md`, `temp.md` | Unmaintainable, unsearchable |
| Overwriting historical versions | Destroys audit trail |
| Deleting failed plans | Hides mistakes; history is valuable |
| Modifying code without user approval | Violates governance protocol |
| Marking `Human Verified` without user confirmation | Fabricates quality assurance |
| Creating duplicate plans without checking history | Wastes effort, creates conflicts |
| Silently fixing unrelated issues | Expands scope without approval |

---

*Last updated: 2026-09-05 | By: Antigravity AI*
*Governance Skill: `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`*
