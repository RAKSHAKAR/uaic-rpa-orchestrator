# Historical Implementation: Execution Modes & Environment Parity

> **Subsystem:** Attended / Unattended Modes & Local / Docker Parity  
> **Historical Scope:** October 2026 Engineering Sprints  
> **Status:** Fully Remediated, Benchmarked & Verified  

---

## 1. Dual Execution Modes

The platform supports two distinct operational modes:
1. **Attended Mode (Visible GUI)**:
   - Launches a visible Google Chrome window on the host desktop.
   - Paces interactions with human-like randomized delays (100–300ms typing jitter, realistic mouse movement).
   - Allows operator to visually intervene if a portal presents terms-of-service disclaimers or two-factor challenges.
2. **Unattended Mode (Headless)**:
   - Runs headless Chrome without opening a desktop window.
   - Optimized for high-throughput batch claim processing.

---

## 2. Key Remediations & Technical Milestones

### 2.1 Resolution of `setup_local.ps1` TypeError
- **Defect Diagnosed**: `setup_local.ps1` line 526 passed `updated_by='setup_local.ps1'` to `save_system_settings_async()`, triggering a silent `TypeError` in Pydantic schema validation.
- **Remediation**: Removed the invalid argument; settings save cleanly to the SQLite database.

### 2.2 Bidirectional Mode Synchronization
- **Backend Schema Validator**: Added `@model_validator(mode="after")` in `backend/app/schemas/settings.py` keeping `headless_mode` and `human_interaction_mode` bidirectionally synchronized.
- **Frontend Settings Sync**: Updated `frontend/src/app/settings/page.tsx` so toggling either the radio card or the toggle switch updates both fields simultaneously in the API payload.

### 2.3 Docker Container Parity via Xvfb + noVNC
- **Defect Diagnosed**: Docker containers could not run visible attended mode because headless was forced in container environments.
- **Remediation**:
  - Installed `xvfb`, `x11vnc`, `novnc`, `websockify`, and `fluxbox` in `backend/Dockerfile`.
  - Exposed ports `6080` (noVNC web client) and `5900` (VNC server) in `docker-compose.yml`.
  - Operators can access `http://localhost:6080/vnc.html` to visually observe Chrome running inside the container.

