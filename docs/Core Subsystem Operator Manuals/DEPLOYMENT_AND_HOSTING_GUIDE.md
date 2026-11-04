# UAIC Claim & RPA Orchestrator — Enterprise Deployment & Hosting Guide

> **Authoritative Operational Runbook for Production VPS, Cloud Infrastructure & Multi-Browser Orchestration**  
> **Document Version:** 2.0.0  
> **Supported Environments:** Ubuntu 22.04/24.04 LTS, Debian 12, Windows Server 2022, Docker & Docker Compose  
> **Target Runtime:** Next.js 14 + Python 3.14 + FastAPI + Celery + Redis + PostgreSQL + Playwright

---

## Table of Contents

1. [Architecture Overview & Workflow](#1-architecture-overview--workflow)
2. [Switching from Development to Production Environment](#2-switching-from-development-to-production-environment)
3. [Complete Multi-Browser Installation Guide (Linux & Windows)](#3-complete-multi-browser-installation-guide-linux--windows)
4. [Attended (Visible GUI) vs. Unattended (Headless) Mode on VPS/Cloud](#4-attended-visible-gui-vs-unattended-headless-mode-on-vpscloud)
5. [Anti-Captcha Extension v0.83 Setup & Security Policies](#5-anti-captcha-extension-v083-setup--security-policies)
6. [Step-by-Step Production VPS Deployment (Docker Compose)](#6-step-by-step-production-vps-deployment-docker-compose)
7. [Step-by-Step Production VPS Deployment (Native Systemd)](#7-step-by-step-production-vps-deployment-native-systemd)
8. [Reverse Proxy (Nginx) & SSL/TLS Configuration](#8-reverse-proxy-nginx--ssltls-configuration)
9. [Operational Runbook, Health Monitoring & Auto-Recovery](#9-operational-runbook-health-monitoring--auto-recovery)

---

## 1. Architecture Overview & Workflow

The UAIC Orchestrator replaces legacy Microsoft Power Automate Desktop bots with a high-throughput, multi-threaded court case discovery engine.

```
                              ┌─────────────────────────────────────────┐
                              │           Operator / Adjuster           │
                              │    Web Browser (Chrome, Edge, Safari)   │
                              └────────────────────┬────────────────────┘
                                                   │ HTTPS (Port 443)
                                                   ▼
                              ┌─────────────────────────────────────────┐
                              │            Nginx Reverse Proxy          │
                              │    SSL Termination, Static Caching      │
                              └────────┬───────────────────────┬────────┘
                                       │                       │
               /api/v1, /docs          │                       │ /* (App Router)
                                       ▼                       ▼
            ┌────────────────────────────────────┐ ┌────────────────────────────────────┐
            │         FastAPI API Server         │ │        Next.js 14 Frontend         │
            │      uvicorn app.main:app          │ │      Node.js Standalone Server     │
            │          (Port 8000)               │ │             (Port 3000)            │
            └──────────────────┬─────────────────┘ └────────────────────────────────────┘
                               │
               Async Tasks     │ Enqueue
                               ▼
            ┌────────────────────────────────────┐
            │          Redis 7 Message           │
            │          Broker & Cache            │
            │          (Port 6379)               │
            └──────────────────┬─────────────────┘
                               │
            ┌──────────────────┴─────────────────┐
            │                                    │
            ▼                                    ▼
┌───────────────────────────────┐ ┌─────────────────────────────────────────────┐
│    Celery Scraper Workers     │ │           Celery Matching Workers           │
│   Playwright Browser Fleet    │ │      RapidFuzz Party Name Deduplication     │
│   (Chromium / Chrome / Edge)  │ │      & Guidewire Insurance Cloud Dispatch   │
│     Display :99 (Xvfb/VNC)    │ └──────────────────────┬──────────────────────┘
└───────────────┬───────────────┘                        │
                │                                        │
                ▼                                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                          PostgreSQL 15 Database (Port 5432)                   │
│      Claims, Scraped Court Cases, Fuzzy Matches, Audit Logs, Settings         │
└───────────────────────────────────────────────────────────────────────────────┘
```

### When an Excel File is Uploaded from a Deployed URL:
1. **Upload & Ingestion:** The operator uploads an `.xlsx` or `.csv` batch file via `/upload`. FastAPI streams the file to `uploads/` and queues `ingest_claims_file_task`.
2. **Auto-Queue Runner:** Once claims are ingested into `RECORD_PENDING`, the Celery queue runner automatically pulls claims sequentially up to configured concurrency limits.
3. **Court Discovery:** Scraper workers launch the selected browser (Chromium, Google Chrome, or Microsoft Edge), navigate in parallel across Florida (`Broward`, `Hillsborough`, `Miami-Dade`) or Texas (`Dallas`, `Travis`, `Harris County JP`, `Harris County Clerk`, `Harris District Clerk`) court portals, solve Turnstile/reCAPTCHA challenges, and extract matching case records.
4. **Fuzzy Deduplication:** Scraped court cases pass to `evaluate_fuzzy_matches_task`. RapidFuzz executes the 3-party cascade (`Claimant` → `Insured` → `Driver` against `CaseStyle`) with configurable thresholds (default: 60%).
5. **Guidewire Cloud Integration:** Positively verified matches are serialized into the Guidewire case update schema and dispatched to Guidewire ClaimCenter, generating real-time Activity IDs.

---

## 2. Switching from Development to Production Environment

In development mode, the system enables verbose debug logging, auto-reloading, unmasked debug tracebacks, and displays the **`Environment: development`** badge in the header and footer.

To switch to **`Environment: production`**, perform the following changes:

### Step 2.1: Update Backend Environment Variables (`backend/.env` or Docker env)

```ini
# ==============================================================================
# UAIC Orchestrator — Production Environment Configuration
# ==============================================================================

# Application Environment (Toggles badges, swagger docs, and strict error handling)
APP_NAME="UAIC Claim & RPA Orchestrator"
APP_ENV="production"
DEBUG=False

# Cryptographic Secret Key (Generate with: openssl rand -hex 32)
SECRET_KEY="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

# Database Connection (Production PostgreSQL with asyncpg driver)
DATABASE_URL="postgresql+asyncpg://uaic_user:SecureProdPassword123!@db:5432/uaic_db"

# Redis Broker & Cache (Include password if Redis AUTH is enabled)
REDIS_URL="redis://:RedisProdSecretPass789!@redis:6379/0"
CELERY_BROKER_URL="redis://:RedisProdSecretPass789!@redis:6379/0"
CELERY_RESULT_BACKEND="redis://:RedisProdSecretPass789!@redis:6379/1"

# CORS Security (STRICT: Restrict strictly to your production domain)
BACKEND_CORS_ORIGINS=["https://orchestrator.yourcompany.com"]

# Guidewire Production API Integration
GUIDEWIRE_API_URL="https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate"
GUIDEWIRE_API_KEY="your-production-guidewire-api-key"

# Anti-Captcha API Key (Can also be managed dynamically via Settings page)
ANTICAPTCHA_API_KEY="your-20-character-anticaptcha-key"

# Virtual Display for Headless/VPS Containers
DISPLAY=:99
```

### Step 2.2: Update Frontend Environment Variables (`frontend/.env.production`)

Create or update `frontend/.env.production`:

```ini
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://orchestrator.yourcompany.com/api/v1
NEXT_PUBLIC_API_BASE_URL=https://orchestrator.yourcompany.com/api/v1
```

### Step 2.3: Build Frontend for Production

When building for production, Next.js generates static optimizations and tree-shakes developer packages:

```bash
cd frontend
npm ci
npm run build
```

### Step 2.4: Verification of Production Mode

1. Navigate to `https://orchestrator.yourcompany.com`.
2. Inspect the global navbar and footer:
   - Environment Badge: Shows **`Environment: production`** (or **`Production`** with a green status indicator).
   - FastAPI `/docs` (Swagger) and `/redoc` are disabled when `DEBUG=False` to prevent schema exposure.
   - API error responses return sanitized enterprise error messages without internal stack traces.

---

## 3. Complete Multi-Browser Installation Guide (Linux & Windows)

The UAIC Orchestrator supports three browser engines, selectable via **Settings → Browser Automation**:
1. **Playwright Chromium (Bundled)** — Lightweight, highly stable, fast startup.
2. **Google Chrome (Official Stable)** — Maximum compatibility with anti-bot algorithms (Cloudflare Turnstile, DataDome).
3. **Microsoft Edge (Official Stable)** — Enterprise parity with Windows desktop automation.

Below are the exact commands to install all three browsers on Linux (Ubuntu/Debian) and Windows.

---

### Option A: Linux (Ubuntu 22.04 / 24.04 LTS & Debian 12)

#### 1. Playwright Bundled Chromium
Playwright provides pre-compiled binaries along with all required X11, font, and codec libraries:

```bash
# Update package index
sudo apt-get update

# Install Playwright browser and system OS dependencies
playwright install --with-deps chromium

# Verify installed binary location
ls -ld /root/.cache/ms-playwright/chromium-* || ls -ld ~/.cache/ms-playwright/chromium-*
```

#### 2. Official Google Chrome Stable
Install the official Google Chrome `.deb` package signed with Google's release key:

```bash
# Install curl and prerequisites
sudo apt-get install -y wget curl gnupg

# Download the latest stable Google Chrome package
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install package and resolve dependencies
sudo apt-get update
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

# Clean up installer
rm -f google-chrome-stable_current_amd64.deb

# Verify installation and path
google-chrome --version
which google-chrome
# Output: /usr/bin/google-chrome
```

#### 3. Official Microsoft Edge Stable
Add Microsoft's official Linux package repository and install Edge:

```bash
# Import Microsoft GPG signing key
curl -fSsL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/microsoft-edge.gpg > /dev/null

# Add Microsoft Edge repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-edge.gpg] https://packages.microsoft.com/repos/edge stable main" | sudo tee /etc/apt/sources.list.d/microsoft-edge.list

# Update package index and install Microsoft Edge
sudo apt-get update
sudo apt-get install -y microsoft-edge-stable

# Verify installation and path
microsoft-edge --version
which microsoft-edge
# Output: /usr/bin/microsoft-edge
```

---

### Option B: Windows Server 2022 / Windows 10/11

#### 1. Playwright Bundled Chromium
In your Python virtual environment on Windows:

```powershell
# Activate your venv
.\.venv\Scripts\Activate.ps1

# Install Playwright Chromium
playwright install chromium

# Binary path will be in:
# %LOCALAPPDATA%\ms-playwright\chromium-<revision>\chrome-win\chrome.exe
```

#### 2. Official Google Chrome Stable
Install via Windows Package Manager (`winget`) or official offline standalone MSI:

```powershell
# Install via Winget
winget install --id Google.Chrome --exact --accept-source-agreements --accept-package-agreements

# Default install locations detected by Orchestrator:
# C:\Program Files\Google\Chrome\Application\chrome.exe
# C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
```

#### 3. Official Microsoft Edge Stable
Microsoft Edge is pre-installed on Windows 10, 11, and Windows Server 2022. To update or reinstall:

```powershell
# Install or update via Winget
winget install --id Microsoft.Edge --exact --accept-source-agreements --accept-package-agreements

# Default install locations detected by Orchestrator:
# C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
# C:\Program Files\Microsoft\Edge\Application\msedge.exe
```

---

### Browser Detection Matrix

The Orchestrator's `BrowserManager` (`backend/app/automation/browser_manager.py`) automatically probes these paths in priority order:

| Browser Selection | Operating System | Auto-Detected Binary Paths |
| :--- | :--- | :--- |
| **Playwright Chromium** | Linux | `/ms-playwright/chromium-*/chrome-linux/chrome`, `~/.cache/ms-playwright/...` |
| **Playwright Chromium** | Windows | `%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win\chrome.exe` |
| **Google Chrome** | Linux | `/usr/bin/google-chrome`, `/usr/bin/google-chrome-stable` |
| **Google Chrome** | Windows | `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| **Microsoft Edge** | Linux | `/usr/bin/microsoft-edge`, `/usr/bin/microsoft-edge-stable` |
| **Microsoft Edge** | Windows | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` |

---

## 4. Attended (Visible GUI) vs. Unattended (Headless) Mode on VPS/Cloud

A common deployment question is: **"When hosted on a cloud VPS (which has no physical monitor attached), can we run Attended (Visible GUI) mode, and how does the browser execute?"**

### The Technical Challenge:
1. **Manifest V3 Extensions (Anti-Captcha):** The Chrome Manifest V3 specification requires an active graphical window or display server. In pure headless mode (`headless=True`), Chrome does not initialize extension background service workers, which prevents CAPTCHA auto-solving.
2. **Cloud VPS Constraints:** Cloud VPS instances (AWS EC2, DigitalOcean, Linode, Hetzner, Azure) are headless Linux servers without a monitor or graphics card.

### The Architectural Solution:
The UAIC Orchestrator uses **Xvfb (X Virtual Framebuffer)**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Cloud VPS / Docker Container                    │
│                                                                        │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │                 Xvfb Virtual Display (:99)                   │    │
│   │                 (Virtual 1920x1080x24 Monitor)               │    │
│   │                                                              │    │
│   │   ┌──────────────────────────────────────────────────────┐   │    │
│   │   │  Playwright Chrome / Edge / Chromium (Attended GUI)  │   │    │
│   │   │  Loads Anti-Captcha Extension v0.83                   │   │    │
│   │   │  Navigates Portals, Solves CAPTCHAs, Extracts Tables │   │    │
│   │   └──────────────────────────────────────────────────────┘   │    │
│   └──────────────────────────────┬───────────────────────────────┘    │
│                                  │                                     │
│   ┌──────────────────────────────▼───────────────────────────────┐    │
│   │                  x11vnc Server (Port 5900)                   │    │
│   │                 Scrapes display buffer :99                   │    │
│   └──────────────────────────────┬───────────────────────────────┘    │
│                                  │                                     │
│   ┌──────────────────────────────▼───────────────────────────────┐    │
│   │               noVNC / Websockify (Port 6080)                 │    │
│   │            Renders Live Desktop into Web Browser             │    │
│   └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS / WSS
                                   ▼
          ┌──────────────────────────────────────────────────┐
          │     Operator's Laptop Web Browser (Anywhere)     │
          │   https://orchestrator.yourcompany.com/vnc.html   │
          │         Watch Real Chrome Window Live!           │
          └──────────────────────────────────────────────────┘
```

### Modes Breakdown:

| Operating Mode | Settings Value | How It Executes on VPS | How Operator Views It |
| :--- | :--- | :--- | :--- |
| **Unattended Mode** | `headless: true` (or virtual headless) | Runs in background Xvfb buffer or headless pipeline. | Claims process automatically in background. Results, tables, and screenshots are viewed on Dashboard. |
| **Attended Mode (VPS)** | `headless: false` | Runs inside Xvfb virtual display `:99`. Extensions load 100% normally. | Operator views live interactive Chrome window by opening `noVNC` web URL in their browser! |
| **Attended Mode (Windows Local)** | `headless: false` | Real Chrome/Edge window pops up directly on your Windows desktop. | Operator sees the browser window open and type right on their screen. |

---

## 5. Anti-Captcha Extension v0.83 Setup & Security Policies

The Anti-Captcha extension is packaged in `anticaptcha-plugin_v0.83/` and automates Turnstile and reCAPTCHA solving.

### How the Orchestrator Loads the Extension
In `backend/app/automation/browser_manager.py`, Chrome/Edge is launched with:
```python
launch_args = [
    f"--disable-extensions-except={ext_path}",
    f"--load-extension={ext_path}",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]
```

### Step 5.1: Configure Anti-Captcha API Key
1. **Via UI (Recommended):** Go to `https://orchestrator.yourcompany.com/settings` → Click **CAPTCHA Extension** tab → Enter your 32-character key → Click **Save Settings** & **Setup Extension**.
2. **Via Config File:** Edit `anticaptcha-plugin_v0.83/js/config_ac_api_key.js`:
   ```javascript
   var antiCapthaPredefinedApiKey = 'YOUR_32_CHAR_API_KEY_HERE';
   ```

### Step 5.2: Resolving Enterprise Organization Policies
If running on a corporate Windows laptop or locked-down enterprise VPS, Chrome or Edge might show:
`"This extension is blocked by your organization"`.

#### Resolution on Windows:
Open PowerShell as Administrator:
```powershell
# Remove extension install blacklists
Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Chrome\ExtensionInstallBlocklist" -Name "*" -ErrorAction SilentlyContinue
Remove-ItemProperty -Path "HKCU:\Software\Policies\Google\Chrome\ExtensionInstallBlocklist" -Name "*" -ErrorAction SilentlyContinue

# Allow unpacked extension loading
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Chrome" -Name "DeveloperToolsAvailability" -Value 1 -Type DWord
```

#### Resolution on Linux:
Remove restrictive managed policy files:
```bash
sudo rm -rf /etc/opt/chrome/policies/managed/*
sudo rm -rf /etc/opt/edge/policies/managed/*
```

---

## 6. Step-by-Step Production VPS Deployment (Docker Compose)

This is the recommended, zero-friction method to deploy the complete stack on any cloud VPS (Ubuntu 22.04 LTS).

### Step 6.1: VPS Hardware Requirements
- **CPU:** 4 vCPUs minimum (8 vCPUs recommended for multi-tab browser concurrency).
- **RAM:** 8 GB RAM minimum (16 GB recommended when running 3+ parallel browser sessions).
- **Disk:** 50 GB SSD.

### Step 6.2: Install Docker & Docker Compose on Ubuntu VPS

```bash
# Update packages
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker CE and Compose plugin
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker
```

### Step 6.3: Clone Codebase and Configure Environment

```bash
# Clone repository
git clone https://github.com/your-org/Bot_UAIC.git /opt/uaic-orchestrator
cd /opt/uaic-orchestrator

# Create production root environment file
cat << 'EOF' > .env
APP_NAME="UAIC Claim & RPA Orchestrator"
APP_ENV=production
DEBUG=false
SECRET_KEY=9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b
DB_USER=uaic_admin
DB_PASSWORD=SuperSecretDbPassword2026!
DB_NAME=uaic_production
REDIS_PASSWORD=SuperSecretRedisPassword2026!
ANTICAPTCHA_API_KEY=your_actual_anticaptcha_key_here
GUIDEWIRE_API_URL=https://uaic-gwcp-prod-igoauthproxy.api.delta4-andromeda.guidewire.net/api/powerapps/caseupdate
GUIDEWIRE_API_KEY=your_guidewire_key_here
NEXT_PUBLIC_API_URL=https://orchestrator.yourcompany.com/api/v1
NEXT_PUBLIC_API_BASE_URL=https://orchestrator.yourcompany.com/api/v1
EOF
```

### Step 6.4: Production `docker-compose.yml` Configuration

Ensure your root `docker-compose.yml` includes the production Xvfb display, worker scaling, and noVNC viewing service:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: uaic_postgres
    environment:
      POSTGRES_USER: ${DB_USER:-uaic_admin}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-SuperSecretDbPassword2026!}
      POSTGRES_DB: ${DB_NAME:-uaic_production}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-uaic_admin} -d ${DB_NAME:-uaic_production}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: uaic_redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}
    volumes:
      - redis_data:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: uaic_fastapi
    command: bash -c "Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp & export DISPLAY=:99 && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
    volumes:
      - ./backend/screenshots:/app/screenshots
      - ./backend/logs:/app/logs
      - ./backend/uploads:/app/uploads
      - ./anticaptcha-plugin_v0.83:/app/anticaptcha-plugin_v0.83
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER:-uaic_admin}:${DB_PASSWORD:-SuperSecretDbPassword2026!}@db:5432/${DB_NAME:-uaic_production}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/1
      - APP_ENV=production
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - DISPLAY=:99
    ports:
      - "127.0.0.1:8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: uaic_celery_worker
    command: bash -c "Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp & export DISPLAY=:99 && celery -A app.core.celery_app worker --loglevel=info --concurrency=4 -Q default,scrapers,matcher,notifications -n worker1@%h"
    volumes:
      - ./backend/screenshots:/app/screenshots
      - ./backend/logs:/app/logs
      - ./backend/uploads:/app/uploads
      - ./anticaptcha-plugin_v0.83:/app/anticaptcha-plugin_v0.83
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER:-uaic_admin}:${DB_PASSWORD:-SuperSecretDbPassword2026!}@db:5432/${DB_NAME:-uaic_production}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/0
      - CELERY_RESULT_BACKEND=redis://:${REDIS_PASSWORD:-SuperSecretRedisPassword2026!}@redis:6379/1
      - APP_ENV=production
      - DEBUG=false
      - SECRET_KEY=${SECRET_KEY}
      - DISPLAY=:99
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: always

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: uaic_frontend
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
    ports:
      - "127.0.0.1:3000:3000"
    restart: always

volumes:
  postgres_data:
  redis_data:
```

### Step 6.5: Build & Launch

```bash
cd /opt/uaic-orchestrator

# Build all containers and launch in background
docker compose up -d --build

# Inspect running containers
docker compose ps

# Check Celery Worker Logs
docker compose logs -f celery_worker
```

---

## 7. Step-by-Step Production VPS Deployment (Native Systemd)

If deploying directly onto bare-metal Linux without Docker:

### Step 7.1: Systemd Service for FastAPI API (`/etc/systemd/system/uaic-api.service`)

```ini
[Unit]
Description=UAIC Orchestrator FastAPI Server
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/uaic-orchestrator/backend
Environment="PATH=/opt/uaic-orchestrator/backend/.venv/bin"
EnvironmentFile=/opt/uaic-orchestrator/backend/.env
ExecStart=/opt/uaic-orchestrator/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 7.2: Systemd Service for Celery Worker (`/etc/systemd/system/uaic-worker.service`)

```ini
[Unit]
Description=UAIC Orchestrator Celery Worker & Browser Fleet
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/uaic-orchestrator/backend
Environment="PATH=/opt/uaic-orchestrator/backend/.venv/bin"
EnvironmentFile=/opt/uaic-orchestrator/backend/.env
# Starts Xvfb on display :99 before launching Celery
ExecStartPre=-/usr/bin/killall Xvfb
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
ExecStart=/opt/uaic-orchestrator/backend/.venv/bin/celery -A app.core.celery_app worker --loglevel=info --concurrency=4 -Q default,scrapers,matcher,notifications
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Step 7.3: Systemd Service for Next.js Frontend (`/etc/systemd/system/uaic-frontend.service`)

```ini
[Unit]
Description=UAIC Orchestrator Next.js Frontend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/uaic-orchestrator/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/node .next/standalone/server.js
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Step 7.4: Enable & Start All Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable uaic-api uaic-worker uaic-frontend
sudo systemctl start uaic-api uaic-worker uaic-frontend
sudo systemctl status uaic-api uaic-worker uaic-frontend
```

---

## 8. Reverse Proxy (Nginx) & SSL/TLS Configuration

Install Nginx and configure SSL using Let's Encrypt Certbot:

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

Create `/etc/nginx/sites-available/uaic-orchestrator.conf`:

```nginx
# Upstream clusters
upstream fastapi_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream nextjs_frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name orchestrator.yourcompany.com;
    return 301 https://$host$request_uri;
}

# HTTPS Production Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name orchestrator.yourcompany.com;

    # SSL Certificate files (Certbot managed)
    ssl_certificate /etc/letsencrypt/live/orchestrator.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/orchestrator.yourcompany.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    client_max_body_size 100M;

    # Backend API & WebSocket routing
    location /api/ {
        proxy_pass http://fastapi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }

    # Frontend Next.js routing
    location / {
        proxy_pass http://nextjs_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and request SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/uaic-orchestrator.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Generate SSL certificate automatically
sudo certbot --nginx -d orchestrator.yourcompany.com --non-interactive --agree-tos -m devops@yourcompany.com
```

---

## 9. Operational Runbook, Health Monitoring & Auto-Recovery

### Health Check Probes
The orchestrator provides built-in enterprise health monitoring endpoints for load balancers (AWS ALB, Cloudflare, Kubernetes):

- **Liveness Probe:** `GET /api/v1/health`
  ```json
  { "status": "ok", "app": "UAIC Claim & RPA Orchestrator", "environment": "production" }
  ```
- **Deep Component Probe:** `GET /api/v1/health/detailed`
  Checks connectivity across PostgreSQL, Redis, Celery, AntiCaptcha API balance, and reachability across all 8 Florida and Texas court portals.

### Auto-Queue & Stuck Claim Recovery
If a worker is restarted or a court portal times out mid-search, the queue runner automatically handles recovery:
- Claims in `SCRAPING_IN_PROGRESS` with no heartbeat for > 10 minutes are automatically transitioned to `RECORD_PENDING` and rescheduled.
- Concurrency locks are managed in Redis with auto-expiring TTLs (30 minutes max) to prevent queue deadlocks.

### Log Inspection Commands

```bash
# Live Celery scraper execution logs
docker compose logs -f --tail=100 celery_worker

# Live FastAPI request & audit logs
docker compose logs -f --tail=100 backend

# Filter for court portal results
docker compose logs celery_worker | grep -E "scraped|cases found|Turnstile|RapidFuzz"
```

---

*Enterprise Deployment Guide verified and finalized for production compliance.*
