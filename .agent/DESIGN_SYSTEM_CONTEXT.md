# UAIC Design System Context

> **Purpose:** Authoritative reference for the 26-token design system, theme conventions, and component standards.
> **Source of Truth:** `frontend/src/app/globals.css` (token values) and `/branding` page (runtime editing)
> **Last Updated:** 2026-11-03 (`IMP-2026-1103-002`)

---

## 1. Theme Architecture

### Two Themes Only

| Theme | Selector | Toggle |
|---|---|---|
| **Light** | `:root, [data-theme="light"]` | Default |
| **Dark** | `.dark, [data-theme="dark"]` | User toggle |

> [!IMPORTANT]
> **No `prefers-color-scheme` / system detection.** The theme system strictly supports Light and Dark only — never OS/System automatic detection. User preference is persisted in `localStorage` via `ThemeProvider.tsx`.

### Theme Switching Mechanism
- `ThemeProvider.tsx` manages theme state
- Sets `data-theme="light"` or `data-theme="dark"` on `<html>` element
- Also sets/removes `.dark` class for Tailwind dark mode
- Branding page (`/branding`) allows runtime token editing via CSS variables

---

## 2. The 26 Semantic Color Tokens

All tokens are CSS custom properties (variables). Use via `var(--token-name)` in CSS or `[--token-name]` in Tailwind.

| Token | Light Value | Dark Value | Purpose |
|---|---|---|---|
| `--color-primary` | `#4f46e5` (indigo-600) | `#6366f1` (indigo-500) | Primary actions, buttons, links |
| `--color-secondary` | `#0ea5e9` (sky-500) | `#38bdf8` (sky-400) | Secondary actions, badges |
| `--color-accent` | `#6366f1` (indigo-500) | `#818cf8` (indigo-400) | Highlights, focus rings |
| `--color-background` | `#f8fafc` | `#020617` | Page background |
| `--color-surface` | `#ffffff` | `#0f172a` | Cards, panels, dialogs |
| `--color-card` | `#ffffff` | `#1e293b` | Card backgrounds |
| `--color-header` | `#ffffff` | `#0f172a` | Navbar/header background |
| `--color-sidebar` | `#ffffff` | `#0f172a` | Sidebar background |
| `--color-text` | `#0f172a` | `#f1f5f9` | Primary text |
| `--color-text-muted` | `#64748b` | `#94a3b8` | Secondary, placeholder text |
| `--color-border` | `#e2e8f0` | `#1e293b` | Component borders |
| `--color-divider` | `#e2e8f0` | `#1e293b` | Horizontal rules, separators |
| `--color-input-background` | `#f8fafc` | `#1e293b` | Input field backgrounds |
| `--color-input-text` | `#0f172a` | `#f1f5f9` | Input field text |
| `--color-button` | `#4f46e5` | `#6366f1` | Primary button fill |
| `--color-button-text` | `#ffffff` | `#ffffff` | Primary button label |
| `--color-link` | `#4f46e5` | `#818cf8` | Hyperlink text |
| `--color-success` | `#10b981` (emerald-500) | `#34d399` (emerald-400) | Success states, completed |
| `--color-warning` | `#f59e0b` (amber-500) | `#fbbf24` (amber-400) | Warning states, pending |
| `--color-error` | `#ef4444` (red-500) | `#f87171` (red-400) | Error states, failed |
| `--color-info` | `#3b82f6` (blue-500) | `#60a5fa` (blue-400) | Info states, notifications |
| `--color-focus` | `#6366f1` | `#818cf8` | Focus ring (keyboard nav) |
| `--color-hover` | `#f1f5f9` | `#1e293b` | Hover state backgrounds |
| `--color-active` | `#e2e8f0` | `#334155` | Active/pressed states |
| `--color-selected` | `#e0e7ff` | `#312e81` | Selected row/item backgrounds |
| `--color-disabled` | `#94a3b8` | `#475569` | Disabled elements |

---

## 3. Installed Radix UI Components

All Radix UI primitives available via `@radix-ui/react-*` packages:

| Component | Package | Used For |
|---|---|---|
| AlertDialog | `@radix-ui/react-alert-dialog` | Destructive action confirmations |
| Avatar | `@radix-ui/react-avatar` | User/system avatars |
| Checkbox | `@radix-ui/react-checkbox` | Multi-select, form checkboxes |
| Dialog | `@radix-ui/react-dialog` | Modals, detail panels |
| DropdownMenu | `@radix-ui/react-dropdown-menu` | Action menus, filters |
| Label | `@radix-ui/react-label` | Accessible form labels |
| Progress | `@radix-ui/react-progress` | Loading bars |
| Select | `@radix-ui/react-select` | Dropdown selectors |
| Separator | `@radix-ui/react-separator` | Visual dividers |
| Slot | `@radix-ui/react-slot` | Polymorphic component composition |
| Switch | `@radix-ui/react-switch` | Toggle settings |
| Tabs | `@radix-ui/react-tabs` | Tab navigation |
| Toast | `@radix-ui/react-toast` | Notifications (NOT `alert()`) |
| Tooltip | `@radix-ui/react-tooltip` | Helper text on hover |

---

## 4. Shared Component Inventory

Located in `frontend/src/components/`:

| Component | Purpose |
|---|---|
| `Navbar.tsx` | Top navigation — must appear on all primary routes |
| `Sidebar.tsx` | Desktop left sidebar navigation |
| `ResponsiveShell.tsx` | Full-width enterprise layout wrapper |
| `MobileBottomNav.tsx` | Bottom tab bar for mobile viewports |
| `MobileDrawer.tsx` | Slide-out drawer for mobile |
| `StatCard.tsx` | Dashboard metric card |
| `StatusBadge.tsx` | Claim/portal status indicator |
| `ThemeProvider.tsx` | Light/Dark theme context + localStorage persistence |
| `BrandingContext.tsx` | Runtime branding token provider |
| `CommandPalette.tsx` | Keyboard-accessible quick-nav (Cmd/Ctrl+K) |
| `FileUploader.tsx` | Drag-and-drop Excel/CSV upload |
| `AsyncExportModal.tsx` | Export format selection + async download |
| `ExportActionToolbar.tsx` | Bulk export action bar |
| `FilterPresetManager.tsx` | Saved filter preset management |
| `MultiSelectDropdown.tsx` | Multi-value filter selector |
| `NavigationContext.tsx` | Active route context |
| `Footer.tsx` | Application footer |

---

## 5. Layout Standards

### Enterprise Full-Width Layout
```tsx
// ✅ Correct — full-width enterprise layout
<div className="w-full max-w-none flex-1 flex flex-col">
  ...
</div>

// ❌ Wrong — constrains enterprise layout
<div className="max-w-6xl mx-auto">
  ...
</div>
```

### All Primary Routes Must Include
```tsx
import { Navbar } from "@/components/Navbar";
// ...
<Navbar />
<main className="w-full flex-1">
  ...
</main>
```

---

## 6. Typography

| Scale | Class | Usage |
|---|---|---|
| Display | `text-3xl font-bold` | Page titles |
| Heading 1 | `text-2xl font-semibold` | Section headers |
| Heading 2 | `text-xl font-semibold` | Card headers |
| Heading 3 | `text-lg font-medium` | Subsection headers |
| Body | `text-sm` | Primary content |
| Small | `text-xs` | Labels, metadata, captions |
| Code | `font-mono text-sm` | Code snippets, IDs |
| Numeric | `font-mono tabular-nums` | Counts, statistics |

---

## 7. Status Badge Colors

The `StatusBadge` component maps claim/portal statuses to semantic tokens:

| Status | Color Token | Class |
|---|---|---|
| COMPLETED | `--color-success` | `bg-green-100 text-green-800` |
| IN_PROGRESS | `--color-info` | `bg-blue-100 text-blue-800` |
| PENDING | `--color-warning` | `bg-yellow-100 text-yellow-800` |
| FAILED | `--color-error` | `bg-red-100 text-red-800` |
| BLOCKED | `--color-warning` | `bg-orange-100 text-orange-800` |
| AWAITING_HUMAN | `--color-warning` | `bg-amber-100 text-amber-800` |
| MATCHED | `--color-success` | `bg-emerald-100 text-emerald-800` |
| NO_MATCH | `--color-text-muted` | `bg-gray-100 text-gray-600` |

---

## 8. Rules for New Component Development

1. **Always use semantic tokens** — never hardcode hex colors in components
2. **Test in both themes** — verify token rendering in Light and Dark before committing
3. **Use Radix primitives** — prefer existing Radix components over custom implementations
4. **Reuse `StatusBadge`** — never create duplicate status indicators
5. **Reuse `StatCard`** — for metric/KPI display
6. **No `alert()`** — use Radix `Toast` for all user notifications
7. **Keyboard accessible** — all interactive elements must be keyboard-navigable
8. **Focus rings** — use `focus:ring-2 focus:ring-[var(--color-focus)]` for all interactive elements
9. **Screen reader labels** — use `aria-label` or visible `<Label>` for all form controls
10. **Loading + empty states** — every data-fetching component must handle loading and empty states

---

## 9. Branding Page Convention

The `/branding` page is the **runtime** source of truth for token values. It:
- Reads current CSS variable values
- Provides a color picker for each of the 26 tokens
- Persists changes to the backend settings store
- Broadcasts token updates to all open tabs

**When adding new tokens:**
1. Add to `globals.css` (both `:root` and `.dark` selectors)
2. Add to the Branding page color picker grid
3. Update this file (DESIGN_SYSTEM_CONTEXT.md)
4. Update `ThemeProvider.tsx` if the token needs special handling

