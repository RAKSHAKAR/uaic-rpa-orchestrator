# Repository Architecture and Cleanup Report

> **Document Type:** Repository Architecture & Directory Reorganization Report  
> **Implementation ID:** `IMP-2026-1031-002`  
> **Status:** Final & Verified  
> **Enforced Governance:** Canonical Artifact Structure & Zero Loose Files

---

## 1. Architectural Layout & Canonical Directories

To eliminate structural drift, file scattering, and redundant artifacts, the UAIC Claim & RPA Orchestrator repository strictly enforces canonical directories for all code, scripts, tests, documentation, and media assets.

### Canonical Directory Taxonomy

| Artifact Category | Canonical Directory | Enforced Rules & Description |
|---|---|---|
| **Execution Recordings** | `docs/recordings/` | All video and WebP recordings of browser execution, test runs, and demos. No recordings permitted directly in `docs/` or subfolders. |
| **Screenshots & Frames** | `docs/frames/` | Extracted video frames, error screenshots, and intermediate capture frames. |
| **Documentation Images** | `docs/images/` | UI mockups, architecture diagrams, charts, and permanent visual assets referenced in markdown guides. |
| **Executable Scripts** | `scripts/` | All operational, maintenance, verification, and launch scripts (`.ps1`, `.bat`, `.py`). No loose utility scripts in repository root. |
| **End-to-End Testing** | `e2e/` | All E2E test suites (`e2e/backend/`, `e2e/frontend/`), execution runners (`run_all_e2e_tests.ps1`), fixtures (`e2e/fixtures/`), reports, and logs. |
| **Documentation** | `docs/` | System manuals, operational guides, implementation plans, and release reports. No documentation loose in root. |
| **Backend Service** | `backend/` | FastAPI REST application, Celery workers, automation engines, SQLAlchemy models, and unit/integration tests. |
| **Frontend UI** | `frontend/` | Next.js 14 App Router, React components, Tailwind styles, and TypeScript types. |
| **Protected Plugins** | `anticaptcha-plugin_v0.83/`, `.agents/` | Protected core assets. Strictly prohibited from relocation, purging, or modification. |

---

## 2. Inventory of Cleanup Actions Executed

All cleanup operations were performed systematically via `scripts/execute_repository_cleanup.ps1` following explicit user approval:

### 2.1 Removal of Root-Level Stale and Duplicate Files
1. **Removed 0-byte orphan SQLite database**:
   - Deleted `d:\scratch\Bot_UAIC\orchestrator.db` (0 bytes). Active database remains at `backend/orchestrator.db` as defined in `backend/.env`.
2. **Relocated Root Executable Scripts to `scripts/`**:
   - Moved `Launch_Attended_Browser.bat` -> `scripts/Launch_Attended_Browser.bat`
   - Moved `Deploy-To-GitHub.ps1` -> `scripts/Deploy-To-GitHub.ps1`
3. **Relocated Root Documentation Guides to `docs/`**:
   - Moved `CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md` -> `docs/CLIENT_DEMO_VERIFICATION_WALKTHROUGH.md`
   - Moved `DEPLOYMENT.md` -> `docs/DEPLOYMENT.md`
   - Moved `DEPLOYMENT_AND_HOSTING_GUIDE.md` -> `docs/DEPLOYMENT_AND_HOSTING_GUIDE.md`
4. **Relocated Root Test Fixture to `e2e/fixtures/`**:
   - Moved `ProdRecords8Bots.xlsx` -> `e2e/fixtures/ProdRecords8Bots.xlsx`
5. **Cleaned Stale Temporary Test Dirs in `scripts/`**:
   - Removed 5 stale pytest temporary directories (`scripts/pytest_runtime_tmp_*`) and `scripts/test_downloads/`.

### 2.2 Image and Visual Media Consolidation
1. **Relocated Loose PNG Files**:
   - Identified 156 loose `.png` visual documentation assets in `docs/` and relocated them into canonical `docs/images/`.
2. **Relocated Extracted Frames**:
   - Relocated `docs/recordings/frames` directory into canonical `docs/frames`.

### 2.3 Duplicate Recording Detection and Purging
A comprehensive SHA-256 hash comparison was executed across all recordings in `docs/` and `docs/recordings/`.

**Exact SHA-256 Duplicates Identified & Purged from `docs/` (Retained in `docs/recordings/`):**

| File Name | SHA-256 Hash | File Size | Action |
|---|---|---|---|
| `broward_3parties_attended_execution.webp` | `CB5D4EB084CA4AA2D3DB488CB5423740DED99A9FC61E639DD576ED0BD099C376` | 1,455,612 B | Purged from `docs/`, retained in `docs/recordings/` |
| `all_8bots_attended_consolidated.webp` | `050731D79E3120C1C4C70162B1FD21B7EAE1E1A361E34DA31DBA1DFF1338DF35` | 850,382 B | Purged from `docs/`, retained in `docs/recordings/` |
| `broward_attended_execution.webp` | `7F6196DF181A7D1875AFB4109FF77C0680A68A02A0B7FF1282136E7B61C80927` | 264,664 B | Purged from `docs/`, retained in `docs/recordings/` |
| `dallas_attended_execution.webp` | `A7A8118080C0B0A7B090C8B0D3F551846A31BD7D9F88A1A2847E4513E08FE592` | 203,254 B | Purged from `docs/`, retained in `docs/recordings/` |
| `demo_attended_execution.webp` | `050731D79E3120C1C4C70162B1FD21B7EAE1E1A361E34DA31DBA1DFF1338DF35` | 850,382 B | Purged from `docs/`, retained in `docs/recordings/` |
| `harris_clerk_attended_execution.webp` | `B415C5A8662B0F409C88C00840A0F37DF8EC6C5E3589B679B6E965259C3946C3` | 407,736 B | Purged from `docs/`, retained in `docs/recordings/` |
| `harris_district_clerk_attended_execution.webp`| `F8D14BDAC6D9A95C17CFEC07B98E9BC465F5590FA52A4A87C39535B37EB188BE` | 322,866 B | Purged from `docs/`, retained in `docs/recordings/` |
| `harris_jp_attended_execution.webp` | `83901B9302636DA0B527027CEF28EE39CD27DE0A22D857E4E77041BCF9A5D698` | 179,850 B | Purged from `docs/`, retained in `docs/recordings/` |
| `hillsborough_attended_execution.webp` | `29FD737890BCFD43657C60ECDA2B32B25869B1BCFEA9CCAEF5218731F2A7FA12` | 493,798 B | Purged from `docs/`, retained in `docs/recordings/` |
| `miami_dade_attended_execution.webp` | `AA31EC0285AC98C2C0284458A3CE1A05AE3D3933DFD86D82F1FEAE42C446F04C` | 303,226 B | Purged from `docs/`, retained in `docs/recordings/` |
| `travis_attended_execution.webp` | `CD387D3865DC816C7B7D4E708E5F706596C61A83257FFBA8792015BA00FF2934` | 177,960 B | Purged from `docs/`, retained in `docs/recordings/` |

In addition, 33 loose `.webp` files in `docs/` were consolidated into `docs/recordings/`.

### 2.4 Automated Markdown Link Synchronization
To prevent broken image and video links in documentation following the relocation of assets:
- Executed `scripts/update_markdown_media_links.py`.
- Replaced all references from `docs/image.png` to `docs/images/image.png` and `docs/video.webp` to `docs/recordings/video.webp`.
- Verified all documentation renders cleanly without 404 image errors.

---

## 3. Phase 2 Cleanup — Historical Plans Archival & Recording Deduplication

**Executed:** 2026-10-31 (IMP-2026-1031-002, Phase 2)

### 3.1 Historical Implementation Plans Archived

- **126 dated plan files** (`YYYY-MM-DD_uaic_*.md`) moved from `docs/` root to `docs/history/`.
- `docs/` root now contains exactly **29 clean, active documentation files** plus 4 canonical subdirectories: `recordings/`, `frames/`, `images/`, `history/`.
- `docs/INDEX.md` updated to reference `docs/history/` for the IMP-2026-1031-002 verified record.

### 3.2 Recording Canonical Cleanup

- **44 stale, redundant, or old recording files** deleted from `docs/recordings/` (old dated recordings, verify screenshots erroneously stored as recordings, superseded copies).
- **9 canonical recordings** remain — one per portal (8 individual) + one combined:

| File | Portal | KB |
|---|---|---|
| `01_broward_attended_execution.webp` | Broward County (FL) | 1421 |
| `02_hillsborough_hover_attended_execution.webp` | Hillsborough (FL) | 482 |
| `03_miami_dade_ocs_attended_execution.webp` | Miami-Dade (FL) | 296 |
| `04_travis_odyssey_attended_execution.webp` | Travis County (TX) | 174 |
| `05_dallas_courts_attended_execution.webp` | Dallas County (TX) | 199 |
| `06_harris_jp_attended_execution.webp` | Harris JP (TX) | 176 |
| `07_harris_cclerk_attended_execution.webp` | Harris County Clerk (TX) | 398 |
| `08_harris_district_attended_execution.webp` | Harris District (TX) | 315 |
| `09_all_8bots_combined_attended_orchestration.webp` | All 8 combined | 831 |

> [!IMPORTANT]
> These 9 recordings represent the current canonical set from prior attended execution sessions. Genuine live re-execution recordings with AntiCaptcha, fuzzy match, and Guidewire coverage require real Chrome Playwright sessions with active portal connectivity and a valid AntiCaptcha API key.

---

## 4. Preservation & Integrity Proof

To guarantee that no functional components or business rules were affected:
1. **Zero Functionality Lost**: All 8 county court scrapers, API endpoints, Celery workers, and Guidewire integration models remain completely intact.
2. **Zero Credentials or Settings Removed**: `backend/.env`, database secrets, and system configuration tables are untouched.
3. **Zero Power Automate Flow Data Lost**: `PowerAutomateSolutions/` and `v4_subflows/` remain intact as behavioral reference.
4. **Test Regression Suite Passes 100%**: Post-cleanup test suite passed 100% of tests.
5. **Frontend Lint**: 0 ESLint warnings or errors.
6. **Python Lint**: `ruff check app tests` — All checks passed.
7. **TypeScript**: `tsc --noEmit` — 0 errors.
8. **PS1 Syntax**: All 15 PowerShell scripts pass AST parser with 0 errors.

