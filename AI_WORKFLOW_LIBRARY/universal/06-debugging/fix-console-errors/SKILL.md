---
name: fix-console-errors
description: >-
  Inspect and resolve browser Developer Console errors, unhandled promise rejections, React warnings, and CORS failures.
---

# Fix Console Errors

## 1. Purpose & Overview
Eliminates browser Developer Console errors and warnings, ensuring seamless client-side execution, zero unhandled promise rejections, and pristine user experience.

---

## 2. When to Use & When NOT to Use

### When to Use
- Browser DevTools shows red console errors or unhandled promise rejections.
- React emits hydration mismatch warnings or duplicate key warnings.
- API calls fail with CORS (Cross-Origin Resource Sharing) errors.

### When NOT to Use
- Headless backend CLI tasks.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Browser console logs, network request details, and affected component JSX.

### Prerequisites
- Running frontend and backend stack.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Console Log Extraction
Extract exact console error strings, stack traces, and network failure status codes from browser DevTools.

### Step 2: React Warning Diagnosis
Diagnose React warnings: unique `key` prop missing in lists, hydration differences between server/client, or controlled/uncontrolled input switching.

### Step 3: CORS & Network Resolution
If API calls fail with CORS errors, verify FastAPI `CORSMiddleware` configuration (`allow_origins`, `allow_credentials`) in `backend/app/main.py`.

### Step 4: Promise Rejection Handling
Wrap all asynchronous Axios/Fetch promises in `try/catch` blocks or `.catch()` handlers with user-facing toast alerts.

### Step 5: Clean Console Verification
Navigate through the application with browser DevTools open. Confirm 0 console errors and 0 warnings are emitted.


---

## 5. Safety Considerations & Guardrails
- Never set `allow_origins=['*']` with `allow_credentials=True` in production CORS configurations.
- Do not suppress console errors using monkey-patched `console.error = () => {}`.

---

## 6. Expected Deliverables & Artifacts
- Cleaned frontend components and CORS configuration.
- DevTools console screenshot demonstrating 0 errors.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Browser console remains completely clean (0 errors, 0 warnings) across all primary user workflows.
- [ ] All asynchronous network requests handle failure gracefully.
- [ ] React hydration completes without SSR mismatch warnings.

---

## 8. Error Recovery & Troubleshooting
- If hydration warnings persist on date formatting, use client-only rendering wrappers or `suppressHydrationWarning`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/fix-console-errors`. | `CUSTOM SKILL` |
| **Cursor** | Select `@fix-console-errors` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `fix-console-errors`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `fix-console-errors` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run fix-console-errors`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt fix-console-errors`. | `PROMPT FILE` |
| **Windsurf** | Activate `fix-console-errors` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `AGENTS.md` - Section 8 (No Error Left Behind)
- `backend/app/main.py` - CORS Configuration
