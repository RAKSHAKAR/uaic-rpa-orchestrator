---
name: form-development
description: >-
  Build accessible forms with client and server-side validation, accessible error announcements, and debounced submission.
---

# Form Development

## 1. Purpose & Overview
Ensures user input forms handle data entry, validation feedback, submission states, and backend error mapping reliably and accessibly.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring forms for claim creation, settings configuration, or filter criteria.
- Implementing complex multi-step wizards or upload dialogs.

### When NOT to Use
- Read-only data display grids.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Form field schemas, validation rules (regex, ranges, required fields), and submission endpoint.

### Prerequisites
- Typed API client and backend Pydantic validation schemas.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Form State & Schema Definition
Define form state interface with TypeScript. Establish validation rules mirroring backend Pydantic schemas.

### Step 2: Accessible Field Rendering
Render form controls with associated `<label htmlFor='...'>`, `<input id='...'>`, and `<span role='alert'>` error messages.

### Step 3: Client-Side Validation & Feedback
Validate fields on blur and submit. Display inline error messages with clear, actionable guidance.

### Step 4: Submission State & Debounce
Disable submit button during active submission (`isSubmitting`). Prevent duplicate clicks with debounced handlers.

### Step 5: Backend Error Mapping
Parse FastAPI 422 validation detail arrays and map field-specific errors back to corresponding form inputs.

### Step 6: Success Notification & Form Reset
Show success toast notification upon completion and optionally reset form state.


---

## 5. Safety Considerations & Guardrails
- Never submit passwords or sensitive tokens via unencrypted query parameters.
- Always validate inputs on the server regardless of client-side validation.

---

## 6. Expected Deliverables & Artifacts
- Accessible React form component with complete validation logic.
- Error handling and submission verification pass.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All required fields enforce validation before submission.
- [ ] Server-side 422 validation errors are rendered inline beside offending inputs.
- [ ] Submitting state prevents concurrent duplicate submissions.

---

## 8. Error Recovery & Troubleshooting
- If form state desynchronizes, reset to last known-good state or initial defaults.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/form-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@form-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `form-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `form-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run form-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt form-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `form-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/settings/page.tsx`
- `backend/app/schemas/settings.py`
