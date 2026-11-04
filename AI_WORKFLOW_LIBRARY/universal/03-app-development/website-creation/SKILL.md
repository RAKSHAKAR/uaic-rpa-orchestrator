---
name: website-creation
description: >-
  Build or extend complete web applications adhering to approved architecture, design system, theme tokens, and accessibility standards.
---

# Website Creation

## 1. Purpose & Overview
Guides the end-to-end development of modern web applications, coordinating routing, layout hierarchies, component trees, state management, and API integration into a cohesive, performant platform.

---

## 2. When to Use & When NOT to Use

### When to Use
- Scaffolding a new web application or major multi-page web module.
- Building high-impact user-facing portals with modern frameworks (Next.js 14, React 18).

### When NOT to Use
- Building backend-only background daemons with zero UI surfaces.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- UI/UX wireframes or mockups, page hierarchy specifications, design system tokens, and API schemas.

### Prerequisites
- Configured Next.js or React runtime with TypeScript and Tailwind CSS.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Layout & Route Hierarchy Scaffolding
Establish Next.js App Router structure (`app/layout.tsx`, `app/page.tsx`, nested routes). Implement unified `<Navbar />` and footer landmarks.

### Step 2: Design Token & Theme Integration
Bind semantic theme tokens (`bg-white dark:bg-slate-900`, CSS variables) ensuring zero hardcoded contrast-breaking colors.

### Step 3: Page View & State Implementation
Build responsive page views (`w-full max-w-none flex-1`) with robust loading, empty, and error states.

### Step 4: API Client Binding & Data Fetching
Connect UI views to backend REST endpoints via typed Axios/Fetch clients with error boundaries.

### Step 5: Full-Stack Verification & Accessibility Pass
Run `tsc --noEmit`, test keyboard navigation, verify contrast, and capture dual-mode screenshots.


---

## 5. Safety Considerations & Guardrails
- Never implement auto/OS theme detection; enforce explicit Light and Dark mode selectors.
- Do NOT artificially constrain enterprise layouts with fixed max-widths (like `max-w-4xl`).

---

## 6. Expected Deliverables & Artifacts
- Complete responsive web application routes and components.
- Dual-theme visual verification evidence in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All pages render without errors in both Light Mode and Dark Mode.
- [ ] TypeScript type check passes with 0 errors (`npx tsc --noEmit`).
- [ ] Responsive layout adapts cleanly to desktop, tablet, and mobile viewports.

---

## 8. Error Recovery & Troubleshooting
- If SSR hydration mismatches occur, verify client-only providers have `'use client'` directives.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/website-creation`. | `CUSTOM SKILL` |
| **Cursor** | Select `@website-creation` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `website-creation`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `website-creation` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run website-creation`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt website-creation`. | `PROMPT FILE` |
| **Windsurf** | Activate `website-creation` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/layout.tsx`
- `.agents/skills/theme-system/SKILL.md`
