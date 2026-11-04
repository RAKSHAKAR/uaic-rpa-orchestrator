---
name: mobile-testing
description: >-
  Test mobile responsive layouts, touch interactions, drawer navigation, and mobile viewports.
---

# Mobile Testing

## 1. Purpose & Overview
Verifies that web applications are intuitive, usable, and performant when operated on mobile devices (e.g. iPhone, Android smartphones) using touch controls.

---

## 2. When to Use & When NOT to Use

### When to Use
- Validating responsive UI updates on mobile viewports (375px - 430px).
- Testing mobile navigation drawers, touch modals, and scroll containers.

### When NOT to Use
- Backend server testing.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Frontend application running locally on port 3000.
- Mobile device emulation viewports.

### Prerequisites
- Playwright mobile device emulation profiles.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Mobile Viewport Emulation
Launch Playwright with mobile device profile (e.g. iPhone 14: 390x844, DPR 3.0, mobile touch enabled).

### Step 2: Navigation Drawer Interaction
Open and close mobile navigation drawer (`<Navbar />`). Verify smooth animation, focus trap, and escape key closure.

### Step 3: Table & Data Grid Touch Scroll
Verify data tables scroll smoothly horizontally without hijacking vertical page scrolling.

### Step 4: Touch Target Size Verification
Inspect buttons, icons, and table action controls. Verify hit targets meet minimum 44x44px touch guidelines.

### Step 5: Mobile Form Usability
Test form entry on mobile viewport. Confirm on-screen keyboards do not break layout or obscure submit buttons.

### Step 6: Mobile Evidence Archival
Capture mobile screenshots of all primary routes and save to `docs/`.


---

## 5. Safety Considerations & Guardrails
- Never allow horizontal body scroll on mobile screens.
- Ensure font sizes on mobile inputs are $\ge 16$px to prevent iOS auto-zoom.

---

## 6. Expected Deliverables & Artifacts
- Mobile Usability & Responsiveness Report.
- Mobile viewport screenshot artifacts in `docs/`.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Zero horizontal overflow on 375px and 390px mobile screens.
- [ ] Mobile drawer navigation operates cleanly with touch and keyboard.
- [ ] All interactive buttons satisfy 44x44px hit targets.

---

## 8. Error Recovery & Troubleshooting
- If mobile viewports trigger horizontal scroll, locate fixed-width elements and apply `max-w-full overflow-hidden`.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/mobile-testing`. | `CUSTOM SKILL` |
| **Cursor** | Select `@mobile-testing` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `mobile-testing`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `mobile-testing` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run mobile-testing`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt mobile-testing`. | `PROMPT FILE` |
| **Windsurf** | Activate `mobile-testing` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/components/Navbar.tsx`
- `frontend/src/app/page.tsx`
