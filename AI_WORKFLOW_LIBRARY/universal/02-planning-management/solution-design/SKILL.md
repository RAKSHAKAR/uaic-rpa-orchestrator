---
name: solution-design
description: >-
  Author high-level and low-level technical solution designs detailing data flow, module boundaries, interfaces, and alternatives.
---

# Solution Design

## 1. Purpose & Overview
Translates approved requirements into an authoritative technical design specification, detailing database schemas, API contracts, sequence diagrams, and class responsibilities.

---

## 2. When to Use & When NOT to Use

### When to Use
- Designing a major new feature, subsystem, or third-party integration.
- Standardizing architectural patterns across multiple microservices or scrapers.

### When NOT to Use
- Small bug fixes or superficial UI tweaks.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Approved functional requirements and architecture analysis.

### Prerequisites
- Completed `requirement-analysis` and `technical-feasibility`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: System Context & Scope Definition
Define system boundaries, external integrations, and primary data inputs/outputs.

### Step 2: Component & Data Flow Modeling
Design components, responsibilities, and dataflows using Mermaid sequence diagrams (`sequenceDiagram`).

### Step 3: Database Schema & Persistence Design
Specify table structures, column datatypes, primary/foreign keys, indexes, and nullability constraints.

### Step 4: API Contract & Payload Specification
Define exact REST endpoints, HTTP methods, request bodies, query parameters, response codes, and JSON schemas.

### Step 5: Error Handling & Resilience Architecture
Design timeout policies, retry exponential backoff, circuit breaking, and dead-letter queues.

### Step 6: Solution Design Document Synthesis
Publish the complete Technical Solution Design in `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never specify hardcoded secrets, API tokens, or plain-text passwords in solution designs.
- Ensure designs adhere to the project's strict dual-theme UI tokens and Python 3.14 constraints.

---

## 6. Expected Deliverables & Artifacts
- Technical Solution Design Document (SDD) in `docs/`.
- Mermaid Sequence & Class Diagrams.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Complete dataflow is documented from UI client to database and external APIs.
- [ ] Database schemas, indexes, and migrations are explicitly specified.
- [ ] API request/response payloads are documented with typed examples.

---

## 8. Error Recovery & Troubleshooting
- If review reveals architectural conflicts, update the design and log rationale in an ADR.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/solution-design`. | `CUSTOM SKILL` |
| **Cursor** | Select `@solution-design` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `solution-design`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `solution-design` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run solution-design`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt solution-design`. | `PROMPT FILE` |
| **Windsurf** | Activate `solution-design` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/APIS_AND_MATCHING_ENGINE_GUIDE.md`
- `backend/app/schemas/settings.py`
