# CLAUDE.md — Project Instructions for Claude Code
# UAIC Claim & RPA Orchestrator

## 1. Project Overview
Production-grade Next.js 14 + Python 3.14.7 FastAPI + Celery + Playwright orchestrator automating court-case discovery across 8 Florida and Texas county court portals.

## 2. Mandatory Engineering Governance
Follow the Universal AI Development Workflow & Skills Framework:
- **NO APPROVAL = NO IMPLEMENTATION**: Present a detailed implementation plan and wait for user confirmation before editing code.
- **Test Commands**:
  - Backend unit & integration tests: `cd backend && .venv\Scripts\pytest -q` (556 passing tests)
  - Backend lint: `cd backend && .venv\Scripts\ruff check app tests` (0 errors)
  - Frontend TypeScript: `cd frontend && npx tsc --noEmit` (0 errors)
  - PowerShell syntax: `powershell -File scripts/check_ps1_syntax.ps1` (0 errors)
- **Critical Business Rules**:
  - State Routing: FL policy & loss -> [broward, hillsborough, miami]; TX -> [harris_cclerk, dallas, harris_jp, harris_district, travis]; Cross-state -> ALL 8.
  - DOL Date Base: 1899-12-30 base date, strict MM/dd/yyyy format.
  - ClaimNumber Prefix: 9-digit gets leading '0' prefix in Guidewire payload.
  - Fuzzy Match Cascade: Claimant -> Insured -> Driver at RapidFuzz 0.60 threshold.
  - Portal Schemas: 5 fields for 6 portals; strictly NO CaseType for Harris JP and Harris County Clerk.
  - Protected Directories: Never delete `anticaptcha-plugin_v0.83/` or `.agents/`.

## 3. Skills Library Access
All 145 executable skills are located in `.agents/skills/<skill-name>/SKILL.md` and `AI_WORKFLOW_LIBRARY/`.
Read the corresponding `SKILL.md` before executing any workflow.
