---
name: agy-customizations
description: >-
  Inspect and maintain Google Antigravity-specific customizations, skills loading priority, rules, plugins, and hooks.
---

# Agy Customizations

## 1. Purpose & Overview
Manages Google Antigravity IDE customizations, understanding discovery precedence (Workspace `.agents/` > Global `~/.gemini/config/` > Built-in), progressive disclosure, and hook triggers.

---

## 2. When to Use & When NOT to Use

### When to Use
- Configuring or troubleshooting Antigravity workspace customizations.
- Verifying skill discovery priority or resolving conflicts between workspace and global skills.

### When NOT to Use
- Configuring non-Antigravity tools (use respective adapter).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Workspace `.agents/` configuration and global Antigravity config paths.

### Prerequisites
- Running in Google Antigravity IDE.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Discovery Precedence Audit
Verify loading priority: 1. Workspace (`.agents/skills/`), 2. Declared (`skills.json`), 3. Global (`~/.gemini/config/`), 4. Built-in skills.

### Step 2: Progressive Disclosure Check
Verify that skills in `.agents/skills/<name>/SKILL.md` expose concise YAML frontmatter `name:` and `description:` for light prompt injection.

### Step 3: Project Rules Verification
Confirm project rules in `AGENTS.md`, `GEMINI.md`, and `.agents/rules/*.md` load hierarchically.

### Step 4: MCP Server & Tool Integration
Inspect configured MCP servers (dak, notebooks) and verify tool schema registration.

### Step 5: Hook & Plugin Auditing
Audit `hooks.json` and plugin configurations if present.

### Step 6: Verification & Discovery Pass
Confirm active Antigravity session recognizes workspace skills.


---

## 5. Safety Considerations & Guardrails
- Never overwrite built-in Antigravity tools unless deliberately shadowing with an approved workspace custom skill.
- Do NOT bloat the system prompt with massive un-gated rules.

---

## 6. Expected Deliverables & Artifacts
- Antigravity Customization Audit Report.
- Verified workspace skill registration.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Workspace skills override global/built-in counterparts predictably.
- [ ] Progressive disclosure injects only names and descriptions into context.
- [ ] Rules load hierarchically without duplication.

---

## 8. Error Recovery & Troubleshooting
- If Antigravity fails to discover a workspace skill, verify path is exactly `.agents/skills/<name>/SKILL.md`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/agy-customizations` or follow built-in guide. | `CUSTOM SKILL` |
| **Cursor** | Not applicable (Antigravity-specific). | `CUSTOM RULE / SKILL` |
| **Claude Code** | Not applicable. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Shares `.agents/` discovery root. | `CUSTOM SKILL` |
| **Gemini CLI** | Shares `GEMINI.md` rules. | `CUSTOM SKILL` |
| **GitHub Copilot** | Not applicable. | `PROMPT FILE` |
| **Windsurf** | Not applicable. | `WORKFLOW RULE` |


### Authoritative References
- `C:\Users\priyer\.gemini\antigravity\builtin\skills\agy-customizations\SKILL.md`
- `AGENTS.md` - Section 8
