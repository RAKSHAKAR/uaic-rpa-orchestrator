# Multi-Provider Storage & Async Exports Operator Manual

> **Authoritative Technical Guide for UAIC Storage Systems, Error Screen Captures, and Asynchronous Dossier Exports**  
> Covers Local/S3/Azure/GCS Storage Abstraction, Scraper Lightbox Captures, Background Celery Streaming Exports, and Brand Assets.

---

## 1. Executive Summary & Architectural Overview

The UAIC Orchestrator incorporates an enterprise storage subsystem providing abstracted file persistence across local and cloud environments. It handles three critical operational asset types:
1. **Scraper Error Screenshots**: High-resolution browser captures recorded upon portal timeouts, CAPTCHA blocks, or DOM changes.
2. **Asynchronous Streaming Exports**: Background-generated claim dossiers (XLSX, CSV, JSON, PDF) for enterprise compliance and reporting.
3. **Brand Identity Assets**: Custom corporate logos and favicons served statically to the web application.

```
+-------------------------------------------------------------------------------+
|                             Storage Abstraction Layer                         |
|                                                                               |
|   +-------------------+     +--------------------+     +------------------+   |
|   | Error Screenshots |     | Asynchronous       |     | Brand Logos &    |   |
|   | (BaseCourtScraper)|     | Streaming Exports  |     | Identity Assets  |   |
|   +-------------------+     +--------------------+     +------------------+   |
|             \                         |                         /             |
|              \                        |                        /              |
|               v                       v                       v               |
|   +-----------------------------------------------------------------------+   |
|   |                  StorageService / StorageSettings                     |   |
|   |             (Hierarchical Directory & Provider Routing)               |   |
|   +-----------------------------------------------------------------------+   |
+---------------------------------------|---------------------------------------+
                                        |
       +-----------------+--------------+---------------+-----------------+
       |                 |                              |                 |
       v                 v                              v                 v
+--------------+  +--------------+              +---------------+  +--------------+
|  Local Disk  |  |    AWS S3    |              |  Azure Blob   |  | Google Cloud |
|  (Fallback)  |  |   (boto3)    |              |    Storage    |  | Storage (GCS)|
+--------------+  +--------------+              +---------------+  +--------------+
```

---

## 2. Multi-Provider Storage Abstraction

The `StorageService` in [`backend/app/services/storage_service.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/services/storage_service.py) decouples application workflows from specific storage infrastructure:

| Provider Key | Technology | Required Credentials | Fallback Behavior |
| :--- | :--- | :--- | :--- |
| **`local`** | Server Filesystem | None (`backend/screenshots/`, `backend/exports/`) | **Primary baseline** (Always active) |
| **`s3`** | Amazon Simple Storage Service | AWS Access Key, Secret Key, Region, Bucket Name | Fails over to Local Disk on error |
| **`azure`** | Azure Blob Storage | Azure Connection String, Container Name | Fails over to Local Disk on error |
| **`gcs`** | Google Cloud Storage | GCS Service Account JSON, Bucket Name | Fails over to Local Disk on error |

### Zero-Dependency Fallback
If cloud credentials expire, network egress fails, or cloud buckets are misconfigured, `StorageService` **automatically writes the asset to the local server disk** and logs a warning. Workflows and scraper tasks **never abort** due to storage provider unavailability.

---

## 3. Scraper Error Screenshots & Operator Lightbox

### Automatic Failure Captures
When any court scraper encounters a critical DOM exception, page load timeout, or unsolved CAPTCHA challenge:
1. `BaseCourtScraper.capture_error_screenshot()` snaps the active viewport.
2. The image is saved hierarchically:
   ```
   backend/screenshots/{claim_id}/{portal_key}/{timestamp}_{claim_id}_{portal}.png
   ```
3. An `ErrorScreenshot` ORM record is committed to the database, capturing:
   - `claim_id` & `portal_key`
   - `attempt_number` (1 through 5)
   - `url` & `page_title`
   - `error_type` & `error_details` (truncated stack trace)

### Operator Lightbox Viewer
Operators inspecting claim dossiers at `/claims/[id]` can click on any failed portal card to open the **High-Resolution Lightbox**:
- Visual zoom and pan across captured court error states.
- Inspection of actual portal error messages, Cloudflare challenge screens, or invalid dockets.
- Binary stream endpoint: `GET /api/v1/claims/{id}/screenshots/{id}/image`.

---

## 4. Asynchronous Streaming Exports

Exporting massive claim datasets (>10,000 records) can exceed web server HTTP gateway timeouts. The orchestrator handles this via asynchronous background Celery tasks (`app.tasks.export_tasks`):

```
+---------------+      POST /export-async      +------------------+
| Operator Web  | ---------------------------> | FastAPI Endpoint |
| Client        |                              +------------------+
+---------------+                                       | (Enqueues Task)
       ^                                                v
       |                                       +------------------+
       | GET /export-async/{id}/status         |  Celery Worker   |
       +-------------------------------------- | (export_tasks.py)|
       | (Progress Polling: 25%, 50%, 100%)    +------------------+
       |                                                |
       | GET /export-async/download/{file}              v
       +====================================== +------------------+
                                               | Disk: ./exports/ |
                                               +------------------+
```

### Supported Export Formats
1. **Excel Workbook (`.xlsx`)**: Formatted multi-column spreadsheet generated via `openpyxl` with auto-column widths, styled headers, and serial date normalization.
2. **Standard CSV (`.csv`)**: High-throughput tabular export compatible with any downstream data warehouse or Excel.
3. **Structured JSON (`.json`)**: Full-fidelity data dump containing claim metadata, court dockets, and RapidFuzz scoring telemetry.
4. **Claim Dossier PDF**: Single-claim summary document containing party information, portal statuses, docket details, and Guidewire dispatch receipts.

---

## 5. Brand Asset Management

The orchestrator supports dynamic corporate whitelabeling:
- **Logo Storage**: Custom logos uploaded via `POST /api/v1/settings/upload-logo` are validated (PNG/JPEG/SVG, max 5MB) and saved to `backend/static/`.
- **Favicon Storage**: Favicon images are persisted to `backend/static/favicon.ico`.
- **Public HTTP Delivery**: Served directly by FastAPI static mounts at `GET /api/v1/settings/logo/{filename}` with aggressive client-side HTTP caching.

---

## 6. Operator Testing & Diagnostics

1. **Test Cloud Storage Connectivity**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/settings/test-storage" \
     -H "Content-Type: application/json" \
     -d '{
       "storage_provider": "s3",
       "s3_bucket_name": "uaic-claim-dossiers",
       "s3_region": "us-east-1"
     }'
   ```
   *Uploads a 1KB synthetic test block, verifies read accessibility, and reports handshake latency.*

2. **Trigger Asynchronous Bulk Export**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/claims/export-async" \
     -H "Content-Type: application/json" \
     -d '{
       "format": "xlsx",
       "filters": {"state": "FL", "status": "MATCH_FOUND"}
     }'
   ```
   *Returns `task_id` for background polling.*
