---
name: theme-system
description: |
  Global Light Mode & Dark Mode Theme Governance Skill.
  Enforces exactly two application themes (Light and Dark only).
  Strictly prohibits System/OS automatic theme detection (no prefers-color-scheme).
  Enforces Branding Page as the single authoritative source of truth for all theme tokens.
  Mandates strict multi-theme verification for every new UI component, route, and layout.
---

# Global Theme System & Dual-Mode Governance Skill

> **CRITICAL ARCHITECTURAL MANDATE:**  
> **GBS AI supports exactly two application themes: Light and Dark.**  
> **System/OS automatic theme detection is not supported and must never be introduced.**  
> **Every new page, route, component, modal, form, table, control, dynamic component, and feature MUST support both Light and Dark modes through the centralized Branding Theme Token system.**

---

## 1. Absolute Theme Rules

1. **Exactly Two Theme Modes**:
   - `Light` (`[data-theme="light"]`, `.light`)
   - `Dark` (`[data-theme="dark"]`, `.dark`)
2. **NO System / OS / Auto Mode**:
   - ❌ Do NOT implement OS theme detection (`window.matchMedia('(prefers-color-scheme: ...)')`).
   - ❌ Do NOT add "System", "Auto", or "Follow OS" toggles or menu options.
   - ❌ The application theme is explicitly controlled by the operator's Light/Dark selector (`☀ Light` / `🌙 Dark`).
3. **Branding Page is Single Source of Truth**:
   - The `/branding` page (`app/branding/page.tsx`) controls both Light Mode and Dark Mode color tokens.
   - All theme colors are persisted in backend database settings (`BrandingSettings.light_palette` and `BrandingSettings.dark_palette`).
   - Dynamic token injection (`BrandingContext.tsx`) updates active CSS variables in `:root` and `.dark` dynamically in real time without requiring page reloads.
4. **Zero Hardcoded Colors**:
   - ❌ No `#ffffff`, `#000000`, `bg-slate-900`, `text-white`, `text-black` without appropriate theme token or dual `dark:` variant.
   - ✅ Always pair background and text tokens: `bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 border-slate-200 dark:border-slate-800`.
   - Never allow white text on white background or black text on black background under either mode.

---

## 2. Mandatory Verification Lifecycle for Any Future UI Change

Every future UI change, new page, component, or dialog MUST follow this mandatory lifecycle:

```text
NEW UI COMPONENT / ROUTE
          ↓
USE SEMANTIC THEME TOKENS
          ↓
LIGHT MODE VERIFICATION (No white-on-white, clear borders, readable text)
          ↓
DARK MODE VERIFICATION (No black-on-black, readable inputs, muted text contrast)
          ↓
RESPONSIVE VIEWPORT VERIFICATION (Desktop, Tablet, Mobile)
          ↓
ACCESSIBILITY & CONTRAST VERIFICATION (WCAG AA 4.5:1 text contrast)
          ↓
AUTOMATED TESTS (tsc, lint, build, pytest)
          ↓
BROWSER / E2E VERIFICATION (Playwright dual-mode test)
          ↓
FEATURE COMPLETE
```

A feature is **NEVER** complete if it has only been verified in one mode.

---

## 3. Semantic Design Token Reference (26 Tokens)

All theme palettes must supply complete definitions for the following 26 semantic design tokens:

| Token Category | Token Key | CSS Variable | Description |
|---|---|---|---|
| **Core Brand** | `primary` | `--color-primary` | Main brand action / CTA color |
| | `secondary` | `--color-secondary` | Secondary brand accent tint |
| | `accent` | `--color-accent` | Tertiary highlight color |
| **Surfaces** | `background` | `--color-background` | Main page canvas background |
| | `surface` | `--color-surface` | Section / panel background |
| | `card` | `--color-card` | Card & widget background |
| | `header` | `--color-header` | Navbar & topbar background |
| | `sidebar` | `--color-sidebar` | Sidebar navigation background |
| **Typography** | `text` | `--color-text` | Primary reading text |
| | `text_muted` | `--color-text-muted` | Secondary / caption text |
| **Borders** | `border` | `--color-border` | Container & input borders |
| | `divider` | `--color-divider` | Horizontal / vertical separation rules |
| **Form Inputs** | `input_background` | `--color-input-background` | Input, select, and textarea background |
| | `input_text` | `--color-input-text` | Character text color in form controls |
| **Buttons** | `button` | `--color-button` | Primary button fill |
| | `button_text` | `--color-button-text` | Primary button label text |
| | `link` | `--color-link` | Clickable anchor text |
| **Status Alerts**| `success` | `--color-success` | Matched cases, completed tasks |
| | `warning` | `--color-warning` | Exceptions, pending reviews |
| | `error` | `--color-error` | Scraper failures, system errors |
| | `info` | `--color-info` | Informational badges & notices |
| **Interactive** | `focus` | `--color-focus` | Keyboard focus outline ring |
| | `hover` | `--color-hover` | Cursor hover background tint |
| | `active` | `--color-active` | Pressed button / active click |
| | `selected` | `--color-selected` | Highlighted row or selected pill |
| | `disabled` | `--color-disabled` | Inactive control background/text |

---

## 4. Architectural Implementation Map

- **Theme State & Toggle**: `frontend/src/components/ThemeProvider.tsx`
  - Stores selection in `localStorage.getItem("uaic_theme")`.
  - Sets `.light` / `.dark` class and `[data-theme="light"|"dark"]` attribute on `document.documentElement`.
- **Dynamic Token Injection**: `frontend/src/components/BrandingContext.tsx`
  - Injects CSS rules into `<style id="uaic-dynamic-theme-tokens">` in `document.head`.
- **Administrative Configuration**: `frontend/src/app/branding/page.tsx`
  - Tab 1: `Brand & Identity` (Title, Subtitle, Logo Asset, Favicon Presets)
  - Tab 2: `Theme & Colors` (Light & Dark independent palettes, curated presets, 26 semantic color token editors)
- **CSS Token Roots**: `frontend/src/app/globals.css`
  - Base `:root, [data-theme="light"]` and `.dark, [data-theme="dark"]` custom properties.
- **Backend Schema & Persistence**: `backend/app/schemas/settings.py`
  - `ThemePalette` model and `BrandingSettings.light_palette` / `dark_palette`.

---

## 5. Automated Verification Commands

```powershell
# 1. Backend settings & palette persistence test
cd backend
.venv\Scripts\pytest tests/test_settings_alignment.py -k "branding" -v

# 2. Frontend TypeScript verification
cd frontend
npx tsc --noEmit

# 3. Frontend lint
npm run lint

# 4. Frontend production build
npm run build

# 5. Playwright E2E browser verification
python scripts/test_theme_e2e.py
```
