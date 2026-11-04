---
name: internationalization
description: >-
  Implement multi-locale message catalogs, date/currency formatting, language switching, and RTL layout compatibility.
---

# Internationalization

## 1. Purpose & Overview
Prepares the application for global multi-language deployment by abstracting UI text into localized message catalogs and formatting dates/numbers according to user locale.

---

## 2. When to Use & When NOT to Use

### When to Use
- Adding multilingual support (e.g. Spanish, French) to the platform.
- Standardizing date and number formatting across international jurisdictions.

### When NOT to Use
- Strictly internal single-language backends where English is the permanent standard.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- UI message strings, supported locale codes (`en-US`, `es-ES`), and translation dictionaries.

### Prerequisites
- Internationalization framework (e.g. `next-intl`, `react-i18next`).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Hardcoded String Extraction
Extract hardcoded English text strings from JSX into centralized JSON dictionary catalogs (`messages/en.json`).

### Step 2: Translation Catalog Structure
Organize messages by feature namespace (`common`, `dashboard`, `settings`, `errors`).

### Step 3: Locale Provider & Hook Integration
Wrap application in `I18nProvider`. Replace static text with translation hooks (`t('dashboard.title')`).

### Step 4: Date, Time & Number Formatting
Replace hardcoded date strings with `Intl.DateTimeFormat` and currency with `Intl.NumberFormat`.

### Step 5: Language Selector Component
Implement accessible language dropdown selector in the navigation bar persisting user choice.

### Step 6: RTL & Layout Adaptability
Ensure CSS layouts support bi-directional flow (`dir='rtl'`) if targeting Arabic or Hebrew locales.


---

## 5. Safety Considerations & Guardrails
- Never translate technical system identifiers, API enum keys, or database column names.
- Preserve exact date conversion rules (e.g., DOL base date 1899-12-30) regardless of display locale.

---

## 6. Expected Deliverables & Artifacts
- Localized message catalogs (`en.json`, `es.json`).
- Internationalized Next.js components with locale switching.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Switching languages dynamically re-renders all UI text without page reload errors.
- [ ] Dates and numbers format according to the active locale standard.
- [ ] Zero missing translation key warnings in console.

---

## 8. Error Recovery & Troubleshooting
- If a key is missing from a secondary language catalog, fall back cleanly to the primary English string.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/internationalization`. | `CUSTOM SKILL` |
| **Cursor** | Select `@internationalization` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `internationalization`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `internationalization` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run internationalization`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt internationalization`. | `PROMPT FILE` |
| **Windsurf** | Activate `internationalization` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/src/types/index.ts`
- `AGENTS.md` - Section 3 (DOL Date Conversion)
