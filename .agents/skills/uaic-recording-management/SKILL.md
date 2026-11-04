---
name: uaic-recording-management
description: >-
  Organize, deduplicate, and convert Playwright browser recordings (.webp) and visual screenshots (.png) into docs/.
---

# Uaic Recording Management

## 1. Purpose & Overview
Manages visual evidence assets (video recordings, screenshots, walk-through captures), ensuring all browser subagent recordings are converted, organized, and permanently stored in `docs/` rather than transient IDE directories.

---

## 2. When to Use & When NOT to Use

### When to Use
- Following attended browser execution or client demonstration recordings.
- Organizing and deduplicating visual artifacts in `docs/recordings/` and `docs/images/`.

### When NOT to Use
- Code refactoring.

---

## 3. Required Inputs & Prerequisites

### Required Inputs
- Recorded video frames (.png) or Playwright webm videos in temporary directories.

### Prerequisites
- Image conversion tools (Pillow, ffmpeg).

---

## 4. Step-by-Step Execution Procedure

### Step 1: Recording Asset Discovery
Identify new video frames or recordings in transient directories or `backend/screenshots/`.

### Step 2: Compression & WebP Encoding
Encode recorded frames into high-efficiency WebP animations using `scripts/patch_recording_engine.py`.

### Step 3: Destination Archival in docs/
Move finalized recordings to `docs/` or `docs/recordings/`. Ensure descriptive filenames (e.g. `broward_attended_execution.webp`).

### Step 4: Transient Frame Cleanup
Purge individual raw frame PNGs (`frame_*.png`, `master_frame_*.png`) from root and `docs/` after successful video compilation.

### Step 5: Walkthrough Linkage
Update `docs/WALKTHROUGH.md` with markdown image links pointing to the archived recordings.


---

## 5. Safety Considerations & Guardrails
- CRITICAL: Never leave visual verification recordings exclusively in the transient IDE brain directory.
- Save all recordings permanently in `docs/`.

---

## 6. Expected Deliverables & Artifacts
- Compressed demonstration recordings in `docs/`.
- Updated `docs/WALKTHROUGH.md` referencing visual assets.

---

## 7. Acceptance Criteria & Definition of Done
- [ ] Recordings are stored permanently in `docs/`.
- [ ] Raw frame clutter is purged from repository.
- [ ] `docs/WALKTHROUGH.md` links render valid images.

---

## 8. Error Recovery & Troubleshooting
- If WebP encoding fails, retain raw frames in `docs/recordings/` and log compression error.

---

## 9. Tool Invocation & Reference Mapping

| AI Tool | Invocation Mechanism | Classification |
|---|---|---|
| **Google Antigravity** | Invoke via chat: `/uaic-recording-management`. | `CUSTOM SKILL` |
| **Cursor** | Select `@uaic-recording-management` in Cursor chat. | `CUSTOM RULE / SKILL` |
| **Claude Code** | Prompt Claude Code with `uaic-recording-management`. | `PROJECT INSTRUCTION` |
| **OpenAI Codex** | Reference `uaic-recording-management` in Codex context. | `CUSTOM SKILL` |
| **Gemini CLI** | Invoke via `gemini run uaic-recording-management`. | `CUSTOM SKILL` |
| **GitHub Copilot** | Invoke via Copilot Chat `/prompt uaic-recording-management`. | `PROMPT FILE` |
| **Windsurf** | Activate `uaic-recording-management` in Windsurf. | `WORKFLOW RULE` |


### Authoritative References
- `docs/WALKTHROUGH.md`
- `scripts/patch_recording_engine.py`
