---
name: workflow-skill-creator
description: >-
  Author new standardized, production-grade AI skills following the Universal Skills Framework structure.
---

# Workflow Skill Creator

## 1. Purpose & Overview
Distills complex engineering runbooks, scraper workflows, or operational procedures into standardized, portable `SKILL.md` packages adhering to the 9 mandatory sections of the Universal Framework.

---

## 2. When to Use & When NOT to Use

### When to Use
- Creating a new custom skill for a recurring workflow.
- Standardizing new domain automation procedures (e.g. adding a 9th court portal scraper).

### When NOT to Use
- One-off tasks that will never be repeated.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Workflow procedure, triggers, exclusions, prerequisites, safety rules, and verification criteria.

### Prerequisites
- Understanding of YAML frontmatter (`name:`, `description:`) and progressive disclosure.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Skill Directory Scaffolding
Create directory `.agents/skills/<skill-name>/` or `AI_WORKFLOW_LIBRARY/universal/<category>/<skill-name>/`.

### Step 2: YAML Frontmatter Definition
Draft valid YAML block with lowercase hyphenated `name` and third-person actionable `description` (what it does and when to use it).

### Step 3: 9-Section Standard Authoring
Author all 9 mandatory sections: 1. Purpose & Overview, 2. When to Use & When NOT to Use, 3. Required Inputs & Prerequisites, 4. Step-by-Step Procedure, 5. Safety Considerations, 6. Deliverables, 7. Acceptance Criteria, 8. Error Recovery, 9. Tool Invocation Mapping.

### Step 4: Helper Scripts & Resources
Add optional helper scripts in `scripts/` or examples in `examples/` if the skill requires automated tooling.

### Step 5: Frontmatter & Discovery Validation
Validate YAML syntax with `validate_skills_framework.py` and verify Antigravity/Codex discovery.

### Step 6: Skill Index Update
Add new skill to `AI_WORKFLOW_LIBRARY/CATALOGUE.md` and `README.md`.


---

## 5. Safety Considerations & Guardrails
- Never create empty `SKILL.md` files or generic placeholder text.
- Ensure skill names are lowercase and hyphenated without special characters.

---

## 6. Expected Deliverables & Artifacts
- Production-grade `SKILL.md` package with all 9 standard sections.
- Updated catalogue and index records.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Skill contains valid YAML frontmatter and all 9 required sections.
- [ ] Instructions are actionable, domain-specific, and fully detailed.
- [ ] Discovery script confirms the skill is discoverable by target AI tools.

---

## 8. Error Recovery & Troubleshooting
- If frontmatter YAML is malformed, use `yaml.safe_load` to identify and repair syntax errors.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/workflow-skill-creator`. | `CUSTOM SKILL` |
| **Cursor** | Select `@workflow-skill-creator` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `workflow-skill-creator`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `workflow-skill-creator` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run workflow-skill-creator`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt workflow-skill-creator`. | `PROMPT FILE` |
| **Windsurf** | Activate `workflow-skill-creator` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AI_WORKFLOW_LIBRARY/README.md` - Standard Skill Format
- `.agents/skills/diagnose-plan-confirm-execute/SKILL.md`
