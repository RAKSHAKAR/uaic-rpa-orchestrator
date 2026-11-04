---
name: risk-assessment
description: >-
  Construct comprehensive risk registers recording likelihood, impact severity, mitigation strategies, and contingency triggers.
---

# Risk Assessment

## 1. Purpose & Overview
Proactively identifies technical, operational, and compliance risks, formulating concrete prevention and recovery procedures before issues occur.

---

## 2. When to Use & When NOT to Use

### When to Use
- Pre-implementation planning for high-impact or irreversible changes.
- Integrating with external production APIs (Guidewire) or court portals.
- Automating web scrapers subject to CAPTCHA or anti-bot protections.

### When NOT to Use
- Low-risk documentation updates.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Technical architecture, external service contracts, and deployment plan.

### Prerequisites
- Completed `architecture-analysis` and `technical-feasibility`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Risk Brainstorming & Identification
Enumerate potential failure modes across Technical, Operational, Compliance, and Security categories.

### Step 2: Likelihood & Impact Scoring
Score each risk on Likelihood (1-5) and Impact (1-5). Compute Risk Exposure Score ($R = L \times I$).

### Step 3: Mitigation Strategy Formulation
Develop preventive controls to reduce Likelihood for all risks scoring $\ge 10$.

### Step 4: Contingency & Trigger Definition
Define specific observable triggers and recovery procedures if a risk manifests.

### Step 5: Risk Register Documentation
Format findings into a formal Risk Register table with assigned risk owners.


---

## 5. Safety Considerations & Guardrails
- Any risk involving customer data loss, credential exposure, or portal IP blocking must be treated as Critical.
- Ensure rollback contingencies are verified before deploying high-risk changes.

---

## 6. Expected Deliverables & Artifacts
- Comprehensive Risk Register Matrix.
- Contingency Action Runbook.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All identified risks have quantified likelihood and impact ratings.
- [ ] High and Critical risks have documented preventive mitigations and contingency triggers.
- [ ] Data loss and external blocking risks are fully addressed.

---

## 8. Error Recovery & Troubleshooting
- If an unforeseen risk manifests during execution, pause immediately and initiate the contingency protocol.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/risk-assessment`. | `CUSTOM SKILL` |
| **Cursor** | Select `@risk-assessment` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `risk-assessment`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `risk-assessment` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run risk-assessment`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt risk-assessment`. | `PROMPT FILE` |
| **Windsurf** | Activate `risk-assessment` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (AI Agent Rules)
- `docs/PROXY_NETWORK_GUIDE.md`
