---
name: database-documentation
description: >-
  Document relational schemas, table relationships, foreign key cascades, column data types, and index strategies.
---

# Database Documentation

## 1. Purpose & Overview
Maintains an authoritative, visual, and textual specification of all database entities, relationships, constraints, indexes, and storage keys.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding or altering SQLAlchemy models in `app/models/`.
- Documenting database storage keys (`fl_jsonbody_*`, `te_jsonbody_*`).

### When NOT to Use
- Frontend-only component documentation.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- SQLAlchemy declarative models in `app/models/`.

### Prerequisites
- Complete schema definitions.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Table & Column Inventory
Catalogue all tables (`claims`, `court_cases`, `match_results`, `audit_logs`, `error_screenshots`, `system_settings`, `notifications`).

### Step 2: Data Types & Constraints Table
Document every column: Name, Type, Nullable, Primary Key, Foreign Key, Default, and Business Purpose.

### Step 3: Mermaid ERD Generation
Generate comprehensive Entity-Relationship Diagram (`erDiagram`) detailing 1-to-Many and Many-to-Many relationships.

### Step 4: Storage Key Documentation
Document exact JSON storage keys in `ClaimRecord` (`fl_jsonbody_broward`, `fl_jsonbody_hillsborough`, `fl_jsonbody_miami`, `te_jsonbody_*`).

### Step 5: Documentation Publication
Publish in `docs/STORAGE_AND_EXPORTS_GUIDE.md` and link from `README.md`.


---

## 5. Safety Considerations & Guardrails
- Never document hypothetical tables; reflect actual SQLAlchemy models and database schema.
- Highlight strict constraints (e.g. no `CaseType` for Harris JP/Clerk).

---

## 6. Expected Deliverables & Artifacts
- Comprehensive Database Schema Specification.
- Mermaid Entity-Relationship Diagram.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] 100% of tables and columns are documented with exact data types.
- [ ] Foreign key cascading behaviors are explicitly documented.
- [ ] Database storage keys match `AGENTS.md` Section 4.

---

## 8. Error Recovery & Troubleshooting
- If schema drift occurs, run database introspection to synchronize documentation with live SQLite/PG tables.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/database-documentation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@database-documentation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `database-documentation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `database-documentation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run database-documentation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt database-documentation`. | `PROMPT FILE` |
| **Windsurf** | Activate `database-documentation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/STORAGE_AND_EXPORTS_GUIDE.md`
- `AGENTS.md` - Section 4 (Database Storage Keys)
