# Task Queue & Celery Orchestration Engine Operator Manual

> **Authoritative Technical Guide for UAIC Distributed Task Queues, Celery Workers, Redis Broker, and Concurrency Fleet Management**  
> Covers 5 Dedicated Queues, Windows Solo vs Headless Fleet Concurrency, Auto-Queue Runner, Stuck Task Recovery, and Flower Observability.

---

## 1. Executive Summary & Architectural Overview

The UAIC Orchestrator uses **Celery 5.6+** backed by **Redis 7** as its distributed task and message broker engine. The task queue decouples HTTP API request handling from long-running browser automation, CPU-bound RapidFuzz deduplication, and external network I/O.

```
+-------------------------------------------------------------------------------+
|                            FastAPI REST API Server                            |
|                 (Uploads, Claims CRUD, Bulk Triggers, Webhooks)               |
+---------------------------------------|---------------------------------------+
                                        | (Task Enqueue via Kombu Direct)
                                        v
+-------------------------------------------------------------------------------+
|                           Redis 7 Broker & Result DB                          |
|                                                                               |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
|   | Queue: ingest |  |Queue: scrapers|  |Queue: matcher |  |Queue: notif   |  |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
+---------------------------------------|---------------------------------------+
                                        | (Distributed Worker Prefetch)
                                        v
+-------------------------------------------------------------------------------+
|                            Celery Worker Fleet                                |
|                                                                               |
|   [Attended GUI Mode]                      [Unattended Headless Fleet]        |
|   * Windows -P solo concurrency            * Dynamic concurrency (1-10 workers)|
|   * 1 visible browser instance             * Parallel headless Chrome sessions|
|   * Zero desktop subprocess conflicts      * High-throughput cloud batching   |
+---------------------------------------|---------------------------------------+
                                        |
       +-----------------+--------------+---------------+-----------------+
       |                 |                              |                 |
       v                 v                              v                 v
+--------------+  +--------------+              +---------------+  +--------------+
| ingest_tasks |  |scraper_tasks |              |  fuzzy_tasks  |  | notif_tasks  |
| (openpyxl)   |  | (Playwright) |              |  (RapidFuzz)  |  | (SMTP/Graph) |
+--------------+  +--------------+              +---------------+  +--------------+
```

---

## 2. The 5 Dedicated Task Queues

Task execution is partitioned into 5 independent queues defined in [`backend/app/core/celery_app.py`](file:///c:/Users/priyer/.gemini/antigravity-ide/scratch/Bot_UAIC/backend/app/core/celery_app.py):

| Queue Name | Routing Key | Dedicated Workload | Concurrency / Worker Rules |
| :--- | :--- | :--- | :--- |
| **`ingest`** | `ingest` | Excel & CSV parsing, column auto-mapping, 1899-12-30 date conversion | High I/O, fast execution (<3s) |
| **`scrapers`** | `scrapers` | Browser court scraping across Florida and Texas portals | Resource intensive, rate-limited per portal |
| **`matcher`** | `matcher` | 3-tier RapidFuzz cascade deduplication & Guidewire Cloud push | CPU-bound, C-accelerated string distance |
| **`notifications`**| `notifications`| Multi-provider email dispatch (SMTP, Graph, SES, MailDev) | Isolated network I/O, failure isolated |
| **`default`** | `default` | Housekeeping, system settings persistence, cache maintenance | General administrative background jobs |

### Worker Execution Parameters
- `task_acks_late=True`: Tasks are acknowledged only **after** successful completion. If a worker crashes mid-scrape, the task is re-queued automatically.
- `worker_prefetch_multiplier=1`: Workers fetch only 1 task at a time, preventing worker starvation across long-running browser scraping tasks.
- `worker_max_tasks_per_child=100`: Workers recycle child processes periodically to prevent memory leaks during long-running browser runs.

---

## 3. Concurrency Modes: Attended GUI vs. Headless Fleet

### Attended GUI Mode (Windows Desktop)
- **Celery Execution Flag**: `-P solo`
- **Rationale**: On Windows systems, launching child processes for GUI browser automation can create desktop handle collisions. The `-P solo` execution model runs tasks in the main thread of the worker, ensuring stable, visible Google Chrome automation with extension toolbar access.

### Unattended Headless Fleet Mode (Server / Docker)
- **Celery Execution Flag**: `--concurrency=N` (configurable 1 to 10 parallel claims via `max_concurrent_claims`).
- **Fleet Concurrency**: Playwright runs multi-worker browser sessions concurrently using `--headless=new` with isolated user data profiles, achieving high-throughput batch processing.
- **Fleet Testing Endpoint**: `POST /api/v1/settings/test-fleet` validates parallel concurrency across 2, 4, or 8 concurrent mock sessions.

---

## 4. Automatic Queue Runner (`queue_runner.py`)

The queue runner task operates as an autonomous background daemon:
1. **Auto-Mode Master Toggle**:
   Stored in Redis at `uaic:queue:auto_mode`. When enabled, the runner automatically polls for claims in `PENDING` status.
2. **Concurrency Window**:
   Tracks actively running claim IDs in Redis set `uaic:queue:active_item_ids`. If the active count is below `max_concurrent_claims`, it pops the next pending claims and enqueues their court scrapers.
3. **Graceful Pause**:
   When paused (`POST /api/v1/queue/pause`), currently in-flight scrapers finish processing, but no new claims are dequeued.

---

## 5. Automated Retry Runner & Stuck Task Recovery (`retry_tasks.py`)

In production, network disruptions or court portal maintenance can leave claims in an indeterminate state:
1. **Stuck Task Recovery**:
   Scans for claims marked `PROCESSING` whose last heartbeat was over **15 minutes ago**. Automatically resets them to `PENDING` and increments `retry_count`.
2. **Exponential Backoff**:
   Retries failed claims up to 3 times with progressive cooldowns (1m, 5m, 15m), preventing denial-of-service pressure on county court portals.

---

## 6. End-to-End Task Lifecycle

```
[Ingest Queue]              [Scrapers Queue]            [Matcher Queue]             [Notifications Queue]
  ingest_claim_file           run_portal_scraper          evaluate_claim_matches       send_event_notification
        |                           |                           |                           |
  Parses Excel &              Spawns Chrome &             Runs RapidFuzz              Dispatches email
  creates ClaimRecord         scrapes 8 portals           3-tier cascade              alert to adjusters
        |                           |                           |                           |
  Enqueues Scrapers --------> Enqueues Matcher ---------> Enqueues Guidewire & -----> Done!
                                                          Notification Task
```

---

## 7. Queue Observability & Monitoring

### 1. Web Queue Monitor (`/monitor`)
- Live KPI cards: Total Claims, In Queue, Active Bots, Processed, Failed.
- **8-Portal Execution Matrix**: Expandable accordion displaying live scraper status, elapsed execution time, and case count across all 8 court portals.
- 1-click controls: **Start All**, **Pause Queue**, **Retrigger Failed**, and **Auto-Mode Toggle**.

### 2. Celery Flower Dashboard
- Available at `http://localhost:5555`.
- Real-time worker health, active task pools, task execution rates, and execution time histograms.

---

## 8. CLI & API Control Commands

1. **Check Queue Health**:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/queue/status"
   ```
2. **Start Sequential Queue Processing**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/queue/start-all"
   ```
3. **Pause Queue Execution**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/queue/pause"
   ```
4. **Retrigger All Failed Claims**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/queue/retrigger"
   ```
5. **Toggle Auto-Queue Mode**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/queue/auto-mode" \
     -H "Content-Type: application/json" \
     -d '{"enabled": true}'
   ```
