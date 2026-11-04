---
name: release-management
description: >-
  Manage semantic versioning, automated changelog generation, git release tagging, and distribution packages.
---

# Release Management

## 1. Purpose & Overview
Governs the software release lifecycle, enforcing semantic versioning (`vMAJOR.MINOR.PATCH`), immutable git tagging, comprehensive release notes, and distribution package integrity.

---

## 2. When to Use & When NOT to Use

### When to Use
- Preparing and tagging a milestone release or production delivery package.
- Generating release changelogs from git commit history.

### When NOT to Use
- Routine local developer commits.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Git commit history since last release tag, milestone deliverables, and test verification reports.

### Prerequisites
- 100% passing test baseline across all suites.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Semantic Version Calculation
Determine next version number adhering to SemVer: Increment Major for breaking changes, Minor for backward-compatible features, Patch for bug fixes.

### Step 2: Changelog Generation
Parse git commits since prior tag. Group entries into: New Features, Bug Fixes, Performance Improvements, Documentation, and Breaking Changes.

### Step 3: Version Bump Synchronization
Update version strings in `package.json`, `app/__init__.py`, `README.md`, and documentation.

### Step 4: Full Test Verification Pass
Execute complete automated test suite (`pytest`, `tsc`, `ps1`) to confirm release candidate is 100% green.

### Step 5: Git Tagging & Release Notes
Create annotated git tag (`git tag -a v1.0.0 -m 'Release v1.0.0'`). Publish release notes in `docs/` and GitHub Releases.

### Step 6: Release Archival
Archive release verification package (test logs, video demonstrations) in `docs/`.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never tag a release if any test fails or TypeScript compilation errors exist.
- Ensure release tags are immutable once published.

---

## 6. Expected Deliverables & Artifacts
- Annotated git release tag.
- Comprehensive Release Notes and Changelog in `docs/`.
- Synchronized version numbers across repository files.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Version numbers are consistent across backend, frontend, and docs.
- [ ] Changelog accurately documents all changes since prior tag.
- [ ] Full automated test suite passes with 100% success rate.

---

## 8. Error Recovery & Troubleshooting
- If an emergency patch is required post-release, increment patch version (`v1.0.1`) and author dedicated hotfix plan.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/release-management`. | `CUSTOM SKILL` |
| **Cursor** | Select `@release-management` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `release-management`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `release-management` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run release-management`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt release-management`. | `PROMPT FILE` |
| **Windsurf** | Activate `release-management` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `Deploy-To-GitHub.ps1`
- `README.md` - Version History
