---
name: knowledge-capture
description: >-
  Capture reusable discoveries, court portal DOM quirks, AntiCaptcha behaviors, and lessons learned into permanent knowledge bases.
---

# Knowledge Capture

## 1. Purpose & Overview
Extracts non-obvious engineering discoveries (e.g. court portal DOM quirks, Cloudflare Turnstile token thresholds, anti-detection flags) into reusable knowledge assets.

---

## 2. When to Use & When NOT to Use

### When to Use
- Discovering undocumented court portal behaviors or DOM idiosyncrasies.
- Overcoming complex CAPTCHA, browser automation, or concurrency challenges.

### When NOT to Use
- Documenting standard well-known library features.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Discovery details, reproduction steps, workaround code, and technical explanation.

### Prerequisites
- Verified solution to a non-obvious problem.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Discovery Context Isolation
Document the symptom, the unexpected platform behavior, and why standard approaches failed.

### Step 2: Technical Mechanism Explanation
Explain the underlying technical mechanism (e.g. Broward County glossary rows having no digits, Turnstile response token length threshold > 20).

### Step 3: Reusable Pattern / Recipe Formulation
Provide the exact, tested code snippet or configuration that resolves the quirk.

### Step 4: Knowledge Base Archival
Save to `docs/` or update corresponding subsystem guide (`COURT_PORTALS_GUIDE.md`).

### Step 5: Agent Skill Update
If applicable, incorporate the recipe into the relevant skill runbook (e.g. `fl-broward-workflow`).


---

## 5. Safety Considerations & Guardrails
- Never record speculative theories; only record verified, tested discoveries.
- Ensure sensitive endpoints or internal IPs are excluded from knowledge notes.

---

## 6. Expected Deliverables & Artifacts
- Technical Knowledge Note in `docs/`.
- Updated scraper runbook or skill reference.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Quirk and verified solution are documented with exact code snippets.
- [ ] Future engineers or AI assistants can reuse the pattern directly.
- [ ] Cross-referenced in relevant subsystem documentation.

---

## 8. Error Recovery & Troubleshooting
- If an external portal alters its behavior again, update the knowledge note with the new observed behavior and date.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/knowledge-capture`. | `CUSTOM SKILL` |
| **Cursor** | Select `@knowledge-capture` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `knowledge-capture`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `knowledge-capture` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run knowledge-capture`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt knowledge-capture`. | `PROMPT FILE` |
| **Windsurf** | Activate `knowledge-capture` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/COURT_PORTALS_GUIDE.md`
- `.agents/skills/fl-broward-workflow/SKILL.md`
