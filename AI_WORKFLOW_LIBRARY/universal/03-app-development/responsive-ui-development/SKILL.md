---
name: responsive-ui-development
description: >-
  Build and validate fluid, usable layouts across mobile (375px), tablet (768px), and widescreen desktop (1920px) viewports.
---

# Responsive Ui Development

## 1. Purpose & Overview
Ensures all web interfaces adapt seamlessly across diverse screen resolutions without horizontal overflow, overlapping controls, unreadable text, or truncated data tables.

---

## 2. When to Use & When NOT to Use

### When to Use
- Authoring or revising UI pages, stat cards, data grids, or navigation headers.
- Fixing mobile layout glitches or table scrolling defects.

### When NOT to Use
- Backend API or headless worker tasks.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Target page components, responsive breakpoint specifications, and viewports.

### Prerequisites
- Tailwind CSS responsive modifiers (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Mobile-First Layout Scaffolding
Design base utility classes for mobile screens (375px-640px) with single-column flow and responsive typography.

### Step 2: Grid & Flex Adaptability
Implement adaptive grids (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`) for stat cards and metric panels.

### Step 3: Table & Data Grid Responsiveness
Wrap wide tabular data in horizontal scroll containers (`overflow-x-auto`) with fixed column headers.

### Step 4: Navigation Drawer & Header Adaptability
Provide responsive hamburger drawers for mobile viewports and persistent navigation bars on desktop.

### Step 5: Multi-Viewport Verification
Validate rendering across 375px, 768px, 1280px, and 1920px viewports using Playwright or browser DevTools.


---

## 5. Safety Considerations & Guardrails
- Never allow horizontal scroll on the primary `body` or `html` element.
- Do NOT use fixed pixel widths on container elements (use `w-full` or percentages).

---

## 6. Expected Deliverables & Artifacts
- Responsive Next.js components and layouts.
- Multi-viewport visual screenshot evidence.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero horizontal overflow on mobile viewports (375px).
- [ ] Stat cards and grids reflow gracefully across tablet and desktop sizes.
- [ ] Touch targets on mobile meet minimum 44x44px accessibility guidelines.

---

## 8. Error Recovery & Troubleshooting
- If elements cause horizontal overflow, inspect DevTools DOM with `* { outline: 1px solid red; }` to locate rogue fixed-width elements.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/responsive-ui-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@responsive-ui-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `responsive-ui-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `responsive-ui-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run responsive-ui-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt responsive-ui-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `responsive-ui-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/page.tsx`
- `frontend/src/components/Navbar.tsx`
