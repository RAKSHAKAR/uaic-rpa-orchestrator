---
name: accidental-data-loss-prevention
description: >-
  STOP AND VERIFY: Mandatory safety protocol requiring explicit user consent before running irreversible destructive actions.
---

# Accidental Data Loss Prevention

## 1. Purpose & Overview
Enforces a strict, non-bypassable safety gate halting any operation that could cause irreversible data loss (SQL `DROP`/`TRUNCATE`/broad `DELETE`, recursive file deletions, branch purges, cloud resource destructions) until explicit human authorization is obtained.

---

## 2. When to Use & When NOT to Use

### When to Use
- BEFORE running any SQL command with `DROP`, `TRUNCATE`, or unconstrained `DELETE`.
- BEFORE running filesystem commands that delete directories (`rmdir /s`, `rm -rf`).
- BEFORE running git commands that discard work (`git reset --hard`, `git clean -fd`).
- BEFORE running cloud resource destructions.

### When NOT to Use
- Non-destructive read-only queries or additive file writes.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target operation command, affected tables/files, estimated blast radius, and verified backup location.

### Prerequisites
- Verified pre-operation backup exists.

---

## 4. Step-by-Step Execution Procedure

### Step 1: STOP AND VERIFY Trigger
Immediately halt execution when an irreversible destructive action is identified.

### Step 2: Blast Radius Assessment
Quantify affected records, files, or resources. Confirm whether data can be recovered.

### Step 3: Pre-Destruction Backup Verification
Verify that an atomic database backup or git branch backup exists before proceeding.

### Step 4: Explicit User Confirmation Prompt
Present exact command, affected target, and blast radius to the user in plain text. Ask: 'Do you authorize this irreversible deletion? [Yes/No]'.

### Step 5: Wait for Explicit Consent
Wait for user confirmation. If user declines or does not confirm, abort operation immediately.

### Step 6: Guarded Execution & Logging
Upon explicit confirmation, execute with strict boundaries and log action to audit trail.


---

## 5. Safety Considerations & Guardrails
- CRITICAL NON-NEGOTIABLE: NEVER execute destructive commands without explicit user consent.
- Never bypass this check under any circumstances, even when running under automated goals.

---

## 6. Expected Deliverables & Artifacts
- Authorization request and verified consent record.
- Audit log capturing destructive execution.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero irreversible deletions occur without prior explicit user consent.
- [ ] Verified backup exists before destructive action executes.
- [ ] All actions logged with user consent timestamp.

---

## 8. Error Recovery & Troubleshooting
- If accidental deletion occurs, halt all activity immediately and restore from pre-destruction backup.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/accidental-data-loss-prevention` or follow global safety rule. | `CUSTOM SKILL` |
| **Cursor** | Select `@accidental-data-loss-prevention` in Cursor. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Mandated by `CLAUDE.md` safety guidelines. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Mandated by `AGENTS.md` safety rules. | `CUSTOM SKILL` |
| **Gemini CLI** | Mandated by `GEMINI.md` guidelines. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt accidental-data-loss-prevention`. | `PROMPT FILE` |
| **Windsurf** | Activate `accidental-data-loss-prevention` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (Must Not Do)
- `C:\Users\priyer\.gemini\config\skills\accidental-data-loss-prevention\SKILL.md`
