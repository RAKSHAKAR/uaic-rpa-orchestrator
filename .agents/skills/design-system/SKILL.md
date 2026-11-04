---
name: design-system
description: >-
  Maintain centralized semantic tokens, typography scales, spacing units, and reusable UI component primitives.
---

# Design System

## 1. Purpose & Overview
Establishes a unified visual design language across the application, preventing fragmented styles, inconsistent padding, and rogue colors through centralized tokens.

---

## 2. When to Use & When NOT to Use

### When to Use
- Creating or standardizing core UI primitives (Buttons, Inputs, Badges, Modals, Cards).
- Updating global application typography, spacing, or branding palettes.

### When NOT to Use
- Backend service logic.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Brand identity guidelines, color palettes, typography specs, and spacing scales.

### Prerequisites
- Tailwind CSS configuration (`tailwind.config.ts`) and CSS variable root.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Semantic Token Definition
Define semantic color tokens in CSS variables: `--primary`, `--background`, `--card`, `--border`, `--muted`.

### Step 2: Tailwind Token Extension
Map CSS variables into `tailwind.config.ts` allowing standard utility consumption (`bg-primary`, `border-border`).

### Step 3: Typography & Elevation Scales
Standardize font sizes (`text-xs` to `text-3xl`), font weights, and shadow elevations (`shadow-sm`, `shadow-md`).

### Step 4: Component Primitive Library
Author standardized UI primitives (`Button`, `Badge`, `Input`, `Card`, `Modal`) in `frontend/src/components/ui/`.

### Step 5: Living Styleguide Documentation
Document token usage and component variants in the `/branding` management console.


---

## 5. Safety Considerations & Guardrails
- Never use raw hex codes directly in page components; always consume semantic tokens.
- Ensure every token pair maintains WCAG AA contrast (4.5:1) in both Light and Dark modes.

---

## 6. Expected Deliverables & Artifacts
- Updated `tailwind.config.ts` and global CSS variable definitions.
- Standardized UI component primitives in `frontend/src/components/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] All new UI components consume centralized semantic tokens.
- [ ] The `/branding` page reflects live palette updates in real time.
- [ ] Zero rogue hex codes exist in newly developed components.

---

## 8. Error Recovery & Troubleshooting
- If Tailwind classes fail to compile, verify that custom token names in `tailwind.config.ts` match CSS variable definitions.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/design-system`. | `CUSTOM SKILL` |
| **Cursor** | Select `@design-system` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `design-system`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `design-system` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run design-system`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt design-system`. | `PROMPT FILE` |
| **Windsurf** | Activate `design-system` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/app/branding/page.tsx`
- `.agents/skills/theme-system/SKILL.md`
