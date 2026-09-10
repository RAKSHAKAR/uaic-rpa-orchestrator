# Global Light Mode / Dark Mode Theme System Implementation, Branding Integration & Skill Enforcement

**Implementation ID:** `IMP-2026-0905-004`  
**Document Type:** Implementation Plan  
**Version:** `v1.1` (Updated with Dedicated Theme Tab on Branding Page)  
**Date:** 2026-09-05  
**Status:** `PROPOSED (Awaiting User Approval)`  
**Author:** Antigravity AI Engineering Governance Agent  

---

## 1. Executive Summary & Objective

The objective of this implementation is to establish a **single, centralized, enterprise-grade theme system** that guarantees every part of the UAIC Claim & RPA Orchestrator works consistently, accessibly, and flawlessly in exactly two theme modes:
1. **Light Mode**
2. **Dark Mode**

### Strict Operational Constraints:
- **NO `System` / `Auto` / OS theme detection**: Automatic switching based on OS appearance (`prefers-color-scheme`), browser settings, or system clocks is strictly prohibited. The application theme is explicitly controlled by its own Light/Dark selector (`☀ Light` / `🌙 Dark`).
- **Existing Branding Page is the Single Source of Truth**: The `/branding` administrative console is the authoritative origin for all visual identity and theme color configurations.
- **Dedicated Theme Tab on Branding Page**: Per user specification, the `/branding` page will feature a clean tabbed interface:
  - **Tab 1: Brand & Identity** — App Title, Subtitle, Logo Asset URL, File Upload, Monogram Letter, and Favicon Presets.
  - **Tab 2: Theme & Colors** — Independent Light Mode & Dark Mode palettes, 26 semantic color token editors with live pickers/hex inputs, curated theme presets, and live dual-mode preview.
- **Zero Hardcoded Color Breakage**: Eliminate any instances of white-on-white text, black-on-black text, invisible input borders, or unthemed widgets across all 9 primary application routes, modals, drawers, tables, forms, filters, badges, and charts.
- **Permanent Skill Enforcement**: Create `.agents/skills/theme-system/SKILL.md` to permanently govern all future development sessions with strict dual-theme verification gates.

---

## 2. Architecture & Data Flow

```text
┌─────────────────────────────────────────────────────────────────┐
│                    Branding Page (/branding)                    │
│   ┌───────────────────────────┬─────────────────────────────┐   │
│   │  Tab 1: Brand & Identity  │   Tab 2: Theme & Colors     │   │
│   │  - Title & Subtitle       │   - [☀️ Light] | [🌙 Dark]   │   │
│   │  - Logo URL & Upload      │   - 26 Semantic Tokens      │   │
│   │  - Favicon Presets        │   - Curated Theme Presets   │   │
│   │  - Fallback Monogram      │   - Reset Theme Defaults    │   │
│   └───────────────────────────┴─────────────────────────────┘   │
│         - Live Solution-Wide Brand & Theme Preview Card         │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Save / Update Settings
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                Backend Settings Service & API                   │
│   - GET /api/v1/settings/branding & POST /api/v1/settings/branding
│   - Pydantic BaseModel ThemePalette & BrandingSettings          │
│   - Redis / DB persistence & Reset-to-Defaults Endpoint         │
└────────────────────────────────┬────────────────────────────────┘
                                 │ Hydration / Fetch Settings
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              BrandingContext & Dynamic Token Engine             │
│   - Injects runtime CSS variables into <style id="uaic-tokens">│
│   - Exposes branding state, updateBranding(), refreshBranding() │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               ThemeProvider & Semantic CSS Tokens               │
│   - Controls active theme ("light" | "dark" only)               │
│   - Toggles .light / .dark & [data-theme="light"|"dark"] on <html>
│   - Persists user selection in localStorage ("uaic_theme")      │
│   - ZERO OS/System theme detection logic                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application-Wide Consumption                  │
│   - CSS Variables: --color-primary, --color-background, etc.   │
│   - Tailwind CSS: darkMode: "class" with light / dark tokens   │
│   - All 9 Routes: Dashboard, Claim Detail, Upload, Monitor,    │
│     Health, Audit Trail, Exceptions, Settings, Branding        │
│   - All Components: Navbar, Sidebar, Drawers, Modals, Tables   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. User Review Required

> [!IMPORTANT]
> **Dedicated "Theme & Colors" Tab on `/branding`**: The Branding page will be organized with a tabbed layout:
> 1. `Brand & Identity` (Title, Subtitle, Logo upload, presets, monogram)
> 2. `Theme & Colors` (Dedicated tab containing Light Mode and Dark Mode configuration sub-views, preset selectors, and the 26 semantic color tokens).

> [!IMPORTANT]
> **Strict Two-Mode Theme Policy**: Per user specification, the application supports **only** `Light` and `Dark` modes. No `System`, `Auto`, or `prefers-color-scheme` logic will be included. The toggle strictly switches between `Light` and `Dark`.

> [!TIP]
> **Dynamic Live Preview & Instant Token Injection**: Color adjustments on the Theme tab will immediately update the active DOM via a dynamic `<style>` injection tag, providing instant real-time feedback before permanent saving.

---

## 4. Proposed Changes

### Component 1: Backend Schemas, Settings & Persistence
- **[MODIFY] [backend/app/schemas/settings.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/schemas/settings.py)**:
  - Define `ThemePalette(BaseModel)` with 26 semantic color fields:
    `primary`, `secondary`, `accent`, `background`, `surface`, `card`, `header`, `sidebar`, `text`, `text_muted`, `border`, `divider`, `input_background`, `input_text`, `button`, `button_text`, `link`, `success`, `warning`, `error`, `info`, `focus`, `hover`, `active`, `selected`, `disabled`.
  - Add `light_palette: ThemePalette` and `dark_palette: ThemePalette` to `BrandingSettings` with full default values.
- **[MODIFY] [backend/tests/test_settings_alignment.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/tests/test_settings_alignment.py)**:
  - Add test `test_branding_theme_palettes_persistence` validating serialization, persistence in Redis/DB, and reset-to-defaults functionality.

---

### Component 2: Frontend Types & Centralized Design Tokens
- **[MODIFY] [frontend/src/types/index.ts](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/types/index.ts)**:
  - Export `ThemePalette` interface with all 26 tokens.
  - Update `BrandingSettings` interface to include optional `light_palette` and `dark_palette`.
- **[MODIFY] [frontend/src/app/globals.css](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/globals.css)**:
  - Define complete base CSS variables for `:root, [data-theme="light"]` and `.dark, [data-theme="dark"]`.
  - Add utility helper classes using these variables where applicable.
- **[MODIFY] [frontend/src/components/ThemeProvider.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/ThemeProvider.tsx)**:
  - Maintain strictly `type Theme = "dark" | "light"`.
  - Ensure both class (`light` or `dark`) and attribute `data-theme` (`light` or `dark`) are synchronized on `document.documentElement`.
  - Persist strictly in `localStorage.getItem("uaic_theme")` defaulting to `"dark"`.
  - Zero OS/System detection listeners.
- **[MODIFY] [frontend/src/components/BrandingContext.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/BrandingContext.tsx)**:
  - Include default Light Mode and Dark Mode palettes.
  - Implement dynamic token injection engine: whenever `branding.light_palette` or `branding.dark_palette` are updated, update `<style id="uaic-dynamic-theme-tokens">` in `document.head`.

---

### Component 3: Administrative Branding UI with Dedicated Theme Tab (`/branding`)
- **[MODIFY] [frontend/src/app/branding/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/branding/page.tsx)**:
  - **Tab Navigation Bar**:
    - Tab 1: `Brand & Identity` (App title, subtitle, logo URL, custom logo upload dropzone, icon presets, monogram badge letter).
    - Tab 2: `Theme & Colors` (Dedicated tab for full theme management).
  - **Inside Theme & Colors Tab**:
    - Mode Switcher: Sub-tabs / pill toggles between `☀️ Light Mode Palette` and `🌙 Dark Mode Palette`.
    - Curated Theme Presets (e.g. *Classic Enterprise Slate*, *Modern Indigo*, *Midnight Slate*, *High Contrast*, *Deep Onyx*, *Emerald Pro*).
    - Semantic Color Token Grid: 26 categorized token controls with swatch preview, native HTML5 color input picker, and hex code text input:
      - **Brand & Core**: Primary, Secondary, Accent.
      - **Surfaces & Layout**: Background, Surface, Card, Header, Sidebar.
      - **Typography**: Text, Muted Text.
      - **Borders & Separators**: Border, Divider.
      - **Form Inputs**: Input Background, Input Text.
      - **Buttons & Actions**: Button Background, Button Text, Link.
      - **Status Alerts**: Success, Warning, Error, Info.
      - **Interactive States**: Focus Ring, Hover State, Active State, Selected Item, Disabled State.
    - Quick actions: "Reset Light Palette", "Reset Dark Palette", "Reset All Theme Defaults".
  - **Live Solution-Wide Brand & Theme Preview**:
    - Side-by-side or toggled preview showing how both Light and Dark themes look on cards, tables, headers, and badges.

---

### Component 4: Navigation & Global Shell Theme Controls
- **[MODIFY] [frontend/src/components/Navbar.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/Navbar.tsx)**:
  - Ensure theme toggle button (`☀ Light` / `🌙 Dark`) has prominent accessible labels and smooth icon transitions.
- **[MODIFY] [frontend/src/components/MobileDrawer.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/components/MobileDrawer.tsx)**:
  - Add dedicated Light / Dark theme switcher in the slide-over drawer so mobile operators have direct access to theme toggling without needing the topbar.
- **[MODIFY] [frontend/src/app/settings/page.tsx](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/frontend/src/app/settings/page.tsx)**:
  - Audit and fix hardcoded dark elements (e.g., Guidewire API tester terminal card at line 781) to ensure clean dual-mode rendering (`bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100`).

---

### Component 5: Governance Skill & Architectural Rules
- **[NEW] [.agents/skills/theme-system/SKILL.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/.agents/skills/theme-system/SKILL.md)**:
  - Document the permanent rule: GBS AI supports exactly two application themes: Light and Dark. System/OS automatic theme detection is not supported and must never be introduced.
  - Mandate verification lifecycle for all future UI work: Semantic Tokens -> Light Mode Check -> Dark Mode Check -> Responsive Check -> Accessibility -> Automated Test.
- **[MODIFY] [AGENTS.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/AGENTS.md) & [README.md](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/README.md)**:
  - Reference `theme-system` skill and document theme token architecture.

---

### Component 6: Automated Testing & Verification
- **[NEW] [scripts/test_theme_e2e.py](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/scripts/test_theme_e2e.py)**:
  - Playwright browser test script that:
    1. Loads the application on `http://localhost:3000`.
    2. Toggles to Light Mode; verifies `<html>` class is `light`, attribute `data-theme` is `light`.
    3. Navigates across all 9 primary routes in Light Mode.
    4. Toggles to Dark Mode; verifies `<html>` class is `dark`, attribute `data-theme` is `dark`.
    5. Navigates across all 9 primary routes in Dark Mode.
    6. Tests the new `Theme & Colors` tab on `/branding`, switches between Light/Dark palettes, modifies colors, and verifies dynamic CSS injection.
    7. Tests persistence across page refresh and navigation.
    8. Takes full-page screenshots of major views in both Light and Dark mode for visual regression proof.

---

## 5. Verification Plan

### Automated Verification:
1. **Backend Tests**:
   ```powershell
   cd backend
   .venv\Scripts\pytest tests/test_settings_alignment.py -k "branding" -v
   .venv\Scripts\pytest --tb=short -q
   ```
2. **Backend Lint**:
   ```powershell
   cd backend
   .venv\Scripts\ruff check app tests
   ```
3. **Frontend TypeScript & Build**:
   ```powershell
   cd frontend
   npx tsc --noEmit
   npm run lint
   npm run build
   ```
4. **Playwright E2E Verification**:
   ```powershell
   python scripts/test_theme_e2e.py
   ```
5. **PowerShell Syntax Check**:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\check_ps1_syntax.ps1"
   ```

---

## 6. Definition of Done Checklist
- [x] Detailed implementation plan documented and updated with dedicated Theme tab.
- [ ] User approval obtained prior to source code edits.
- [ ] Branding page has dedicated tabs: `Brand & Identity` and `Theme & Colors`.
- [ ] Exactly two themes supported: `Light` and `Dark` (no System/OS mode).
- [ ] Branding page is the authoritative source of truth for both Light and Dark palettes.
- [ ] All 26 semantic color tokens configurable per theme mode.
- [ ] Dynamic token engine updates active CSS variables in real time.
- [ ] All 9 routes verified in both Light and Dark modes.
- [ ] All shared components verified in both Light and Dark modes.
- [ ] Zero unreadable contrast or broken layouts.
- [ ] Permanent governance skill `.agents/skills/theme-system/SKILL.md` created.
- [ ] 100% test suite passing.
