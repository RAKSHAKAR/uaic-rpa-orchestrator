---
name: frontend-development
description: >-
  Implement accessible, maintainable Next.js 14 App Router pages, components, layouts, and state management.
---

# Frontend Development

## 1. Purpose & Overview
Provides expert engineering guidance for authoring high-performance React 18 components, custom hooks, and full-width layouts using TypeScript and Tailwind CSS.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring new Next.js routes, dashboard views, or interactive UI components.
- Refactoring complex React component state and optimizing render performance.

### When NOT to Use
- Backend API development or database schema design.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Component specification, UI design tokens, and typed API response schemas.

### Prerequisites
- Next.js 14 App Router project setup (`frontend/`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Route & Page Scaffolding
Create App Router route (`app/<route>/page.tsx`). Mark client-interactive components with `'use client'`.

### Step 2: Layout & Landmark Architecture
Enforce enterprise full-width layout (`w-full max-w-none flex-1`) with semantic `<header>`, `<main>`, `<section>` landmarks.

### Step 3: State & Hook Architecture
Implement local state (`useState`, `useReducer`), debounce hooks for inputs, and context consumers.

### Step 4: Dual-Theme Styling
Apply Tailwind utility classes with dual-mode semantics (`bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100`).

### Step 5: Accessibility & Form Validation
Implement accessible focus rings, ARIA labels, and live region announcements.

### Step 6: Type Checking & Lint Verification
Run `npx tsc --noEmit` and `npm run lint`.


---

## 5. Safety Considerations & Guardrails
- NEVER use browser `alert()` for user notifications; use toast banners or modal dialogs.
- Avoid massive single-file components; modularize into `components/` subdirectories.

---

## 6. Expected Deliverables & Artifacts
- Modular React components and Next.js page routes.
- Zero TypeScript and ESLint error baseline.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] `npx tsc --noEmit` compiles cleanly with 0 errors.
- [ ] Component renders identically across Light and Dark themes without visual defects.
- [ ] Interactive elements are 100% keyboard navigable with visible focus indicators.

---

## 8. Error Recovery & Troubleshooting
- If React useEffect dependency warnings occur, wrap callbacks in `useCallback` or decouple state updates.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/frontend-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@frontend-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `frontend-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `frontend-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run frontend-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt frontend-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `frontend-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/page.tsx`
- `.agents/skills/theme-system/SKILL.md`
