---
name: architecture-documentation
description: >-
  Document system blueprints, Celery queue topologies, scraper pipelines, and multi-tier deployment architectures.
---

# Architecture Documentation

## 1. Purpose & Overview
Creates and maintains holistic architectural blueprints illustrating system tiers, communication protocols, worker concurrency, and external boundary integrations.

---

## 2. When to Use & When NOT to Use

### When to Use
- Updating high-level system diagrams in `README.md` or `docs/`.
- Documenting architectural refactoring or newly introduced microservices.

### When NOT to Use
- Low-level bug fix explanations.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Repository topology, service definitions, network port bindings, and queue configurations.

### Prerequisites
- Completed `architecture-analysis`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Multi-Tier Blueprint Authoring
Document physical and logical tiers: Frontend (Next.js), Backend API (FastAPI), Message Broker (Redis), Asynchronous Workers (Celery), Database (SQLite/PostgreSQL), Automation (Playwright/Chrome).

### Step 2: Mermaid Architecture Diagram
Create top-level architectural diagram using `flowchart TD` illustrating dataflow between all services.

### Step 3: Celery Queue Topology
Document dedicated queues (`scrapers`, `matcher`, `guidewire`, `ingest`, `export`, `retry`, `notifications`) and routing logic.

### Step 4: External Integration Boundaries
Detail boundary interfaces with court portals, AntiCaptcha extension, and Guidewire Insurance Cloud.

### Step 5: Archival & Linkage
Publish in `README.md` and `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never expose internal private IP addresses or production credentials in diagrams.
- Ensure diagrams adhere to supported Mermaid syntax.

---

## 6. Expected Deliverables & Artifacts
- High-Level Architecture Blueprint in `README.md`.
- Mermaid system architecture and queue topology diagrams.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All services, ports, and protocols are documented accurately.
- [ ] Queue topology illustrates all Celery queues and worker bindings.
- [ ] Mermaid diagrams render without syntax errors.

---

## 8. Error Recovery & Troubleshooting
- If Mermaid syntax fails to render, quote node labels containing parentheses or brackets.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/architecture-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@architecture-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `architecture-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `architecture-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run architecture-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt architecture-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `architecture-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `README.md` - Full Architecture Blueprint
- `docs/TASK_QUEUE_AND_ORCHESTRATOR_GUIDE.md`
