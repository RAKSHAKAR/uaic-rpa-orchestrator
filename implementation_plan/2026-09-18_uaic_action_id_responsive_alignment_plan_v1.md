# Implementation Plan: Action ID & Profile Target Responsive Layout Alignment

**Implementation ID:** `IMP-2026-0918-002`  
**Date:** 2026-09-18  
**Status:** Proposed  
**AI Governance:** Diagnose → Plan → Confirm → Execute  

---

## 1. Problem Diagnosis

In the **Automation & Robot Configuration** settings panel (Tab 4: Browser & Anti-Captcha Automation), under "One-Time Extension Toolbar Pinning & Persistent Profile Setup":
- The 2-column grid (`grid-cols-1 sm:grid-cols-2`) displays two cards:
  1. **Toolbar Pinning Status**
  2. **Persistent Profile Target**
- In Card 2, the `Action ID:` label and its value `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj` are rendered as inline text:
  ```tsx
  <p className="text-[10px] text-slate-500 dark:text-slate-400">
    Action ID: <code className="text-indigo-600 dark:text-indigo-400 font-mono">kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj</code>
  </p>
  ```
- Because `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj` is a 53-character uninterrupted string without whitespace or hyphens, and the column width in a 2-column grid on standard viewports is ~320px–360px:
  1. Standard browser text wrapping breaks immediately after `Action ID: `, leaving `Action ID:` isolated on the first line.
  2. The long 53-character code string drops to the second line, left-aligned at the card margin with no indentation or container styling, appearing misaligned and disjointed.
  3. The uncontained string crowds against or overflows the card's right border on narrower viewports.
  4. Card 2 lacks structural parity with Card 1 (which features a balanced header badge, status description, and bottom timestamp).

---

## 2. Proposed Changes

### Frontend: [settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)
- Refactor the 2-column setup card grid:
  - **Card 1 (Toolbar Pinning Status):** Enhance with `flex flex-col justify-between space-y-2` and a clean bottom footer divider for `Last Configured`.
  - **Card 2 (Persistent Profile Target):**
    - Add an engine badge (`settings.automation.browser_engine || "chromium"`) in the card header to visually balance Card 1's status badge.
    - Encapsulate the directory path in a subtle code pill with `break-all select-all`.
    - Create a structured key-value section for `Action ID`:
      - Header row with `Action ID:` on the left and `Preferences Key` descriptor on the right.
      - Enclose `kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj` in a dedicated styled container (`bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-100/80 dark:border-indigo-900/50 rounded-lg p-1.5`) with `break-all select-all block leading-tight text-[10px]`.
- Both cards will have matching heights, balanced borders, consistent padding (`p-3`), and responsive overflow protection.

---

## 3. Verification Plan

### Automated Tests
1. **Frontend TypeScript Check:**
   ```bash
   cd frontend
   npx tsc --noEmit
   ```
2. **Frontend Production Build:**
   ```bash
   cd frontend
   npm run build
   ```
3. **Backend Regression Test:**
   ```bash
   cd backend
   .venv\Scripts\pytest -k "test_settings" -v
   ```

### Visual & Browser Subagent Verification
1. Inspect the updated Settings page in both Light and Dark themes.
2. Verify responsive layout at desktop (1920px), tablet (1024px), and mobile (375px) breakpoints.
3. Capture visual comparison screenshot and save to `implementation_plan/Images/action_id_responsive_aligned.png`.
