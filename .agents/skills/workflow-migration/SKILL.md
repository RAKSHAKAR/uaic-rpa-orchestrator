---
name: workflow-migration
description: >-
  Migrate legacy Robin desktop flows, custom instructions, or older prompts into portable SKILL.md packages.
---

# Workflow Migration

## 1. Purpose & Overview
Transforms legacy automation formats (such as Power Automate Desktop Robin scripts, unstructured prompt templates, or deprecated IDE rules) into modern, standardized `SKILL.md` runbooks.

---

## 2. When to Use & When NOT to Use

### When to Use
- Porting legacy desktop automation subflows (`v4_subflows/`) into Python/Playwright skill specifications.
- Migrating deprecated prompt files into portable Agent Skills.

### When NOT to Use
- Authoring new skills from scratch.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Legacy flow scripts (`v4_subflows/*.robin`, prompt files) and target workflow objectives.

### Prerequisites
- Completed `workflow-skill-creator`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Legacy Flow Inspection
Parse legacy flow syntax (e.g. Robin actions: `WebAutomation.LaunchChrome`, `UIAutomation.Click`). Extract business rules, selector strategies, and wait intervals.

### Step 2: Behavioral Extraction
Identify critical behaviors (e.g. DOM token checks, glossary filtering, date normalization) that must be preserved.

### Step 3: Modern Skill Scaffolding
Scaffold standardized `SKILL.md` following the 9-section framework.

### Step 4: Procedure Modernization
Translate legacy actions into modern Python Playwright procedures with explicit locators, error handlers, and timeouts.

### Step 5: Verification & Parity Pass
Verify that modernized skill retains 100% behavioral equivalence with legacy flow.

### Step 6: Legacy Archival
Archive legacy source in reference directory without deleting historical records.


---

## 5. Safety Considerations & Guardrails
- Never discard subtle timing delays or verification checks present in legacy flows without understanding their purpose.
- Ensure output schemas remain identical to legacy specifications.

---

## 6. Expected Deliverables & Artifacts
- Modernized `SKILL.md` package.
- Legacy-to-Modern Parity Matrix in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All functional actions from legacy flow are mapped to modern procedures.
- [ ] Critical business invariants and error handling are preserved.
- [ ] Modernized skill passes automated validation.

---

## 8. Error Recovery & Troubleshooting
- If legacy flow contains undocumented proprietary actions, inspect runtime logs or annotated flow text (`v4_all_8_subflows_annotated.txt`).

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/workflow-migration`. | `CUSTOM SKILL` |
| **Cursor** | Select `@workflow-migration` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `workflow-migration`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `workflow-migration` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run workflow-migration`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt workflow-migration`. | `PROMPT FILE` |
| **Windsurf** | Activate `workflow-migration` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `v4_subflows/` - Power Automate V4 Robin Scripts
- `docs/v4_all_8_subflows_annotated.txt`
