---
name: skill-repair
description: >-
  Diagnose and repair invalid frontmatter, broken links, conflicting triggers, or malformed skill definitions.
---

# Skill Repair

## 1. Purpose & Overview
Audits, validates, and repairs broken or non-compliant skills across `.agents/skills/` and `AI_WORKFLOW_LIBRARY/`, fixing YAML parsing errors, broken references, and overlapping trigger descriptions.

---

## 2. When to Use & When NOT to Use

### When to Use
- A skill fails to be discovered by Google Antigravity or OpenAI Codex.
- `validate_skills_framework.py` reports YAML or structural violations.
- Two skills have overlapping or conflicting trigger conditions.

### When NOT to Use
- Authoring new skills from scratch.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target skill path, error logs, and validation report.

### Prerequisites
- Access to validation script `scripts/validate_skills_framework.py`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Validation Scan Execution
Execute `python scripts/validate_skills_framework.py`. Parse error logs to identify offending skills and lines.

### Step 2: YAML Frontmatter Syntax Fix
Repair malformed YAML frontmatter: ensure valid opening/closing `---`, quote descriptions containing colons, and verify `name` is lowercase hyphenated.

### Step 3: Mandatory Section Restoration
If required sections are missing, insert standardized section headers and populate with substantive domain-specific instructions.

### Step 4: Trigger Disambiguation
If two skills share overlapping triggers, sharpen the `description` and `When to Use` sections to establish crisp boundaries.

### Step 5: Link & Reference Validation
Verify all markdown file links point to existing valid files.

### Step 6: Re-validation Pass
Rerun validation script to confirm 100% clean status.


---

## 5. Safety Considerations & Guardrails
- Never delete existing detailed instructions while repairing formatting.
- Do NOT alter the skill's core purpose or existing callers.

---

## 6. Expected Deliverables & Artifacts
- Repaired, fully compliant `SKILL.md` package.
- Clean validation scan report with 0 errors.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] YAML frontmatter parses cleanly with `yaml.safe_load`.
- [ ] All 9 mandatory sections are present with substantive content.
- [ ] Skill is successfully discovered by target AI assistants.

---

## 8. Error Recovery & Troubleshooting
- If frontmatter repair fails, re-render using `scripts/skills_data/renderer.py`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/skill-repair`. | `CUSTOM SKILL` |
| **Cursor** | Select `@skill-repair` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `skill-repair`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `skill-repair` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run skill-repair`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt skill-repair`. | `PROMPT FILE` |
| **Windsurf** | Activate `skill-repair` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `scripts/validate_skills_framework.py`
- `AI_WORKFLOW_LIBRARY/README.md`
