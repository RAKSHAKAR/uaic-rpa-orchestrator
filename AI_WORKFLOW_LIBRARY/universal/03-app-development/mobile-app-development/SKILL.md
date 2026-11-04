---
name: mobile-app-development
description: >-
  Guidelines and scaffolding for building native or hybrid mobile client applications and consuming backend APIs.
---

# Mobile App Development

## 1. Purpose & Overview
Provides architectural guidelines for developing cross-platform mobile applications (React Native, Flutter, PWA) that consume backend REST APIs securely with offline caching.

---

## 2. When to Use & When NOT to Use

### When to Use
- Designing or implementing mobile client applications companion to the web platform.
- Configuring Progressive Web App (PWA) manifests and service workers.

### When NOT to Use
- Standard desktop browser web applications.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Mobile screen designs, touch interaction specifications, and mobile API endpoints.

### Prerequisites
- REST API documentation and authentication schemas.

---

## 4. Step-by-Step Execution Procedure

### Step 1: Mobile Architecture & Framework Selection
Select target framework (PWA, React Native, or native Kotlin/Swift) based on offline requirements and hardware access.

### Step 2: PWA Manifest & Icon Scaffolding
Create `manifest.json` with app icons, theme colors, display modes, and service worker registration.

### Step 3: Touch Interaction & Gesture Design
Implement touch-optimized controls with minimum 44x44px hit targets and swipe gesture navigation.

### Step 4: Offline Storage & Synchronization
Implement local caching (IndexedDB, SQLite) with background queue synchronization when network restores.

### Step 5: Push Notification Integration
Configure push notification services for claim completion and system alerts.

### Step 6: Mobile Emulation Verification
Test application in mobile device emulators across iOS and Android viewports.


---

## 5. Safety Considerations & Guardrails
- Never store unencrypted tokens or credentials in insecure mobile device storage.
- Handle intermittent network connectivity gracefully with offline retry queues.

---

## 6. Expected Deliverables & Artifacts
- PWA manifest and mobile-responsive shell or mobile client project.
- Offline caching and sync handlers.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Application installs as PWA or runs on mobile device emulator without errors.
- [ ] Touch interactions and gestures function smoothly without lag.
- [ ] Offline state displays clear notification and queues actions for sync.

---

## 8. Error Recovery & Troubleshooting
- If sync collisions occur upon reconnecting, apply server-wins or timestamp-based reconciliation.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/mobile-app-development`. | `CUSTOM SKILL` |
| **Cursor** | Select `@mobile-app-development` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `mobile-app-development`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `mobile-app-development` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run mobile-app-development`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt mobile-app-development`. | `PROMPT FILE` |
| **Windsurf** | Activate `mobile-app-development` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `frontend/public/`
- `AGENTS.md` - Section 6
