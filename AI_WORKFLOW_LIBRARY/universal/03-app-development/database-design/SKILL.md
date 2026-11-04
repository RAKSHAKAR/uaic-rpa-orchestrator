---
name: database-design
description: >-
  Design normalized relational entities, relationships, constraints, indexes, and soft-delete conventions.
---

# Database Design

## 1. Purpose & Overview
Establishes sound, scalable relational database architectures ensuring data integrity, foreign key cascading safety, query index efficiency, and multi-tenant isolation.

---

## 2. When to Use & When NOT to Use

### When to Use
- Designing new data models or extending existing entities in `app/models/`.
- Optimizing slow database queries with targeted composite or partial indexes.

### When NOT to Use
- Executing ad-hoc SQL queries or running tests.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Domain entity specifications, relationship cardinality, and query access patterns.

### Prerequisites
- Understanding of SQLAlchemy 2.0 declarative models and SQLite/PostgreSQL differences.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Entity & Attribute Normalization
Define entities to Third Normal Form (3NF). Choose appropriate column types (UUID, String, Integer, DateTime with UTC timezone, JSONB/Text).

### Step 2: Relationship & Constraint Modeling
Specify primary keys, foreign keys, unique constraints, and check constraints. Define explicit `ondelete` cascading behavior (`CASCADE`, `SET NULL`, `RESTRICT`).

### Step 3: Index Strategy Formulation
Design B-tree indexes for foreign keys, filter predicates, and sorting columns. Formulate composite indexes for frequent multi-column queries.

### Step 4: SQLAlchemy Model Implementation
Implement declarative models in `app/models/` inheriting from `Base`. Use `Mapped` and `mapped_column` type annotations.

### Step 5: Schema Documentation & ERD Generation
Generate Mermaid Entity-Relationship Diagrams (`erDiagram`) documenting table relationships.


---

## 5. Safety Considerations & Guardrails
- Never create unbounded text or JSON columns for fields requiring strict validation or indexing.
- Ensure SQLite and PostgreSQL compatibility parity across all column definitions.

---

## 6. Expected Deliverables & Artifacts
- SQLAlchemy model class definitions in `app/models/`.
- Mermaid Entity-Relationship Diagram (ERD).

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All models define explicit primary keys, column types, and foreign key constraints.
- [ ] Foreign key columns and common query filter columns are indexed.
- [ ] Models pass all SQLAlchemy initialization tests without mapping warnings.

---

## 8. Error Recovery & Troubleshooting
- If circular foreign key dependencies occur, utilize `use_alter=True` or decouple relationships via associative tables.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/database-design`. | `CUSTOM SKILL` |
| **Cursor** | Select `@database-design` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `database-design`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `database-design` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run database-design`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt database-design`. | `PROMPT FILE` |
| **Windsurf** | Activate `database-design` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `backend/app/models/claim.py`
- `backend/app/core/database.py`
