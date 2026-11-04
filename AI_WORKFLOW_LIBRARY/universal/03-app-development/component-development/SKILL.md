---
name: component-development
description: >-
  Create encapsulated, accessible, and testable React components with strict TypeScript contracts and clear prop interfaces.
---

# Component Development

## 1. Purpose & Overview
Guides the authoring of reusable frontend components that adhere to Single Responsibility, strict typing, memoization, and accessible keyboard interactions.

---

## 2. When to Use & When NOT to Use

### When to Use
- Building new UI widgets, data cards, modals, or filter controls.
- Extracting repetitive JSX markup into shared reusable components.

### When NOT to Use
- Writing one-off script commands or backend functions.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Component functional requirements, prop definitions, and event callback signatures.

### Prerequisites
- TypeScript and React 18 component architecture.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Prop Interface Definition
Define strict TypeScript `interface <ComponentName>Props` with explicit types, optional flags, and JSDoc descriptions.

### Step 2: Component Implementation
Implement functional component using named export. Destructure props with clean defaults.

### Step 3: State & Effect Management
Manage internal state with `useState` or custom hooks. Avoid unnecessary `useEffect` triggers.

### Step 4: Accessibility & ARIA
Apply semantic HTML elements (`<button>`, `<dialog>`), ARIA labels (`aria-label`, `aria-expanded`), and keyboard event handlers (`onKeyDown`).

### Step 5: Dual-Theme Styling
Style with Tailwind utility classes adhering to the dual-theme token system.

### Step 6: Component Verification
Verify component rendering and interactions with TypeScript type-checking.


---

## 5. Safety Considerations & Guardrails
- Avoid prop drilling deeper than 2 levels; use Context or state management for deep state.
- Never use `any` in component prop interfaces.

---

## 6. Expected Deliverables & Artifacts
- TypeScript React component file in `frontend/src/components/`.
- Exported component contract and unit test if applicable.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Component compiles cleanly with zero TypeScript errors.
- [ ] Keyboard interactions (Enter, Space, Escape, Tab) function properly.
- [ ] Renders cleanly in both Light Mode and Dark Mode.

---

## 8. Error Recovery & Troubleshooting
- If re-renders cause performance drops, wrap component in `React.memo` or extract memoized subcomponents.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/component-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@component-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `component-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `component-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run component-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt component-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `component-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/components/Navbar.tsx`
- `frontend/src/types/index.ts`
