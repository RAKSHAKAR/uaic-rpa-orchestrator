---
name: requirement-analysis
description: >-
  Convert raw client inputs, feature requests, and legacy specifications into clear, unambiguous functional and non-functional requirements.
---

# Requirement Analysis

## 1. Purpose & Overview
Bridges the gap between ambiguous user requests or legacy specifications (such as RPA Robin scripts) and rigorous, actionable engineering requirements with objective acceptance criteria.

---

## 2. When to Use & When NOT to Use

### When to Use
- Receiving a new client feature brief or problem statement.
- Porting legacy desktop flows (e.g. Power Automate Desktop V4) to modern services.
- Refactoring complex business logic where business rules must be preserved.

### When NOT to Use
- Fixing straightforward runtime syntax errors or lint warnings.
- Executing pre-approved, well-specified tasks from an existing WBS.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Client request text, ticket descriptions, or reference workflow scripts.
- Existing business rules documentation (`AGENTS.md`, `docs/`).

### Prerequisites
- Understanding of existing domain terms and business models.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Source Material Ingestion
Read and parse the raw requirements document, prompt, or legacy automation flow. Extract business objectives, explicit constraints, and user personas.

### Step 2: Functional Decomposition
Break down stated requirements into discrete functional capabilities (inputs, state transformations, outputs, persistence, and external events).

### Step 3: Non-Functional Requirement Specification
Define performance latency targets, concurrency thresholds, availability constraints, accessibility standards (WCAG 2.1 AA), and data retention rules.

### Step 4: Edge Case & Boundary Identification
Identify boundary conditions, exception states, missing fields, timeout behaviors, and human-in-the-loop fallback scenarios.

### Step 5: Requirements Traceability Matrix (RTM) Formulation
Map every functional requirement to an ID (REQ-XXX), source reference, and preliminary acceptance test scenario.


---

## 5. Safety Considerations & Guardrails
- Do NOT invent or assume business rules when specifications are ambiguous; flag them for `grill-me` clarification.
- Do NOT discard legacy safety constraints (e.g. CAPTCHA verification delays or state routing logic).

---

## 6. Expected Deliverables & Artifacts
- Structured Functional & Non-Functional Requirements Specification (FRS).
- Requirements Traceability Matrix (RTM).

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All functional requirements have unique identifiers and unambiguous descriptions.
- [ ] Non-functional constraints specify measurable thresholds (latency, throughput, availability).
- [ ] Edge cases and error states are documented with explicit fallback behavior.

---

## 8. Error Recovery & Troubleshooting
- If user requirements conflict with core architectural rules, raise an explicit warning and invoke `grill-me`.
- If legacy flow code is incomplete, cross-reference annotated flow documentation (`docs/v4_all_8_subflows_annotated.txt`).

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/requirement-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@requirement-analysis` rule in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `requirement-analysis` workflow. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `requirement-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run requirement-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt requirement-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `requirement-analysis` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 3 (Critical Business Rules)
- `docs/STAGE_AND_STATUS_DEFINITIONS.md`
