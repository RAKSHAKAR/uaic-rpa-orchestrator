---
name: architecture-analysis
description: >-
  Inspect frontend, backend, database, APIs, background queues, integrations, and deployment topology across the entire platform.
---

# Architecture Analysis

## 1. Purpose & Overview
Evaluates architectural patterns, component coupling, cohesion, scalability bottlenecks, deployment topology, and security perimeters across the full stack.

---

## 2. When to Use & When NOT to Use

### When to Use
- Planning architectural evolutions (e.g., SQLite to PostgreSQL, monorepo reorganization).
- Evaluating platform scalability under increased concurrency or data volume.
- Reviewing multi-service integration boundaries and protocol consistency.

### When NOT to Use
- Localized bug fixing within an isolated function.
- Adding standard UI components that follow existing patterns.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Full codebase access across frontend, backend, and infrastructure definitions.
- `docker-compose.yml`, configuration schemas, and network port bindings.

### Prerequisites
- Understanding of modern distributed architecture patterns (FastAPI, Next.js, Celery, Redis).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Topology & Boundary Mapping
Map physical and logical tiers: Browser Client -> Next.js Frontend (Port 3000) -> FastAPI Backend (Port 8000) -> Redis Broker (Port 6379) -> Celery Workers -> Relational Database.

### Step 2: Communication Protocols & Data Formats
Examine inter-service protocols (HTTP/REST JSON, Redis Pub/Sub, Celery AMQP task messages, Playwright CDP).

### Step 3: Persistence Architecture Audit
Analyze database schema design, connection pooling (`AsyncSessionMaker`), transaction scopes, and SQLite/PostgreSQL parity.

### Step 4: Asynchronous Queue & Concurrency Topology
Analyze Celery queue partition strategy, prefetch multipliers, concurrency limits, and worker thread safety.

### Step 5: Architectural Health & Scalability Report
Synthesize findings into an Architecture Blueprint highlighting architectural strengths, technical debt, and scaling limits.


---

## 5. Safety Considerations & Guardrails
- Do NOT initiate live performance benchmarks that overload local Redis or database instances.
- Do NOT expose internal network credentials or connection strings in architecture diagrams.

---

## 6. Expected Deliverables & Artifacts
- Holistic Architectural Blueprint and Topology Map.
- Mermaid Component Diagram (`flowchart TD`) illustrating inter-service communication.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All network ports, protocols, and data payloads between services are documented.
- [ ] Database connection pooling and transaction lifecycle patterns are evaluated.
- [ ] Worker concurrency and semaphore bottlenecks are identified and documented.

---

## 8. Error Recovery & Troubleshooting
- If port bindings conflict or service addresses are ambiguous, inspect `backend/app/core/config.py` and `docker-compose.yml`.
- If worker concurrency behaviors are unclear, inspect `backend/app/core/celery_app.py`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/architecture-analysis`. | `CUSTOM SKILL` |
| **Cursor** | Select `@architecture-analysis` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `architecture-analysis`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `architecture-analysis` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run architecture-analysis`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt architecture-analysis`. | `PROMPT FILE` |
| **Windsurf** | Activate `architecture-analysis` rule in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 2 (Repository Layout)
- `docker-compose.yml` - Multi-Container Service Definitions
