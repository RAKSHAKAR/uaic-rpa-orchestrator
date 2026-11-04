---
name: fix-build-errors
description: >-
  Resolve TypeScript compilation failures (tsc), Next.js build errors, and package resolution bugs.
---

# Fix Build Errors

## 1. Purpose & Overview
Systematically diagnoses and resolves TypeScript type errors, Next.js page generation failures, and bundler resolution issues to restore a clean build baseline.

---

## 2. When to Use & When NOT to Use

### When to Use
- `npx tsc --noEmit` fails with type errors.
- `npm run build` fails during static page optimization or bundling.
- Upgraded frontend packages introduce broken types.

### When NOT to Use
- Backend Python exceptions (use `fix-runtime-errors`).

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- `tsc` compiler error output, error file paths, and line numbers.

### Prerequisites
- Node.js and npm installed in `frontend/`.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Compiler Error Extraction
Run `npx tsc --noEmit` in `frontend/`. Parse error codes (`TS2322`, `TS2339`), file locations, and offending line numbers.

### Step 2: Type Discrepancy Diagnosis
Compare expected type vs actual type. Determine whether interface in `types/index.ts` is outdated or component is passing incorrect props.

### Step 3: Type Contract Correction
Update type definitions in `types/index.ts` to reflect valid API contracts, or correct component prop passing.

### Step 4: SSR & Dynamic Import Resolution
If build fails on SSR window/document access, wrap browser-only code in `useEffect` or dynamic `ssr: false` import.

### Step 5: Compiler Re-verification
Rerun `npx tsc --noEmit`. Verify 0 errors.

### Step 6: Production Build Pass
Run `npm run build` to confirm all static and dynamic routes generate cleanly.


---

## 5. Safety Considerations & Guardrails
- NEVER use `// @ts-ignore` or `any` type casts merely to bypass compiler checks.
- Ensure type fixes preserve backward compatibility with backend API schemas.

---

## 6. Expected Deliverables & Artifacts
- Corrected TypeScript source files and interface contracts.
- Clean compiler output with 0 errors.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `cd frontend && npx tsc --noEmit` exits with code 0.
- [ ] `cd frontend && npm run build` completes successfully.
- [ ] Zero `@ts-ignore` suppressions introduced.

---

## 8. Error Recovery & Troubleshooting
- If Next.js cache becomes corrupted (`.next/`), purge `.next` directory and rebuild.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-build-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-build-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-build-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-build-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-build-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-build-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-build-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/types/index.ts`
- `frontend/tsconfig.json`
