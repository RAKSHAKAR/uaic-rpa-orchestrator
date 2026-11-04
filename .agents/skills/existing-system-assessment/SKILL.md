---
name: existing-system-assessment
description: >-
  Assess an existing solution before proposing changes; guarantee preservation of valid functionality, active data, and test baselines.
---

# Existing System Assessment

## 1. Purpose & Overview
Conducts a rigorous pre-modification audit of an operational system to capture existing behavior, quantify baseline metrics, identify critical invariants, and prevent accidental regression or architectural damage.

---

## 2. When to Use & When NOT to Use

### When to Use
- Prior to refactoring or upgrading existing backend services, scrapers, or database models.
- Inheriting legacy components with existing test suites.
- Modifying core shared utilities utilized by multiple downstream services.

### When NOT to Use
- Completely greenfield modules with zero existing dependencies or callers.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target module/service file paths.
- Existing test suites covering the target area.
- Runtime logs or production telemetry.

### Prerequisites
- Passing test suite baseline (`pytest`, `tsc`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Caller & Dependency Discovery
Identify all upstream callers and downstream dependencies of the target module using AST search or symbol references.

### Step 2: Behavioral Contract Audit
Document the existing function signatures, input parameters, return types, raised exceptions, and side-effects.

### Step 3: Test Coverage Baseline Verification
Execute the existing test suite for the component. Verify current pass rates and record baseline execution latency.

### Step 4: Invariant & Business Rule Identification
Identify non-negotiable rules embedded in the component (e.g. 1899-12-30 date conversion base, 9-digit ClaimNumber '0' prefix).

### Step 5: Assessment & Preservation Summary
Author an assessment summary defining which behaviors must remain 100% invariant during any upcoming refactoring.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never remove existing methods or alter public contracts without backward-compatibility wrappers.
- Do NOT assume an undocumented behavior is a bug; verify business intent before altering.

---

## 6. Expected Deliverables & Artifacts
- System Assessment & Contract Inventory Document.
- Baseline Test Report documenting pre-change behavior and metrics.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All public methods, parameters, and return types of the existing system are catalogued.
- [ ] Baseline test pass rate is established and recorded.
- [ ] Invariants and non-negotiable business rules are explicitly flagged for preservation.

---

## 8. Error Recovery & Troubleshooting
- If existing tests fail before changes begin, document pre-existing failures in the assessment before touching code.
- If dependencies cannot be fully traced, write characterization tests to capture existing behavior.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/existing-system-assessment`. | `CUSTOM SKILL` |
| **Cursor** | Select `@existing-system-assessment` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `existing-system-assessment`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `existing-system-assessment` in Codex prompt. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run existing-system-assessment`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt existing-system-assessment`. | `PROMPT FILE` |
| **Windsurf** | Activate `existing-system-assessment` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Critical Business Rules)
- `backend/app/services/fuzzy_engine.py`
