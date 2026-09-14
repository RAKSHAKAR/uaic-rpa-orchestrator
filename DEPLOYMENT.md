# Multi-Platform Deployment Architecture & Universal CI/CD Standards

This document establishes the cloud-agnostic, microservices deployment blueprint for running the **UAIC Claim & RPA Orchestrator** across Vercel, Render, AWS, Azure, Google Cloud, Docker Compose, Kubernetes, and bare-metal VPS environments.

---

## 1. Zero-Coupling Microservices Architecture

The system is strictly decoupled into independent tiers communicating exclusively via RESTful HTTP/JSON contracts:
* **Frontend Tier (`frontend/`)**: Next.js 14 App Router, dynamic serverless/edge-ready or containerized, using `NEXT_PUBLIC_API_BASE_URL` to route requests to any host.
* **Backend API Tier (`backend/`)**: FastAPI + Python 3.14.7, exposes dynamic port via `$PORT` (`0.0.0.0:${PORT:-8000}`).
* **Task Worker Tier (`backend/`)**: Celery workers consuming tasks from Redis over 4 isolated queues (`ingest`, `scrapers`, `matcher`, `notifications`).
* **Persistence & Cache Tier**: PostgreSQL (or SQLite local) and Redis 7.
* **Email Gateway Tier**: MailDev (local/testing) or standard SMTP (production).

> [!IMPORTANT]
> **Zero Coupling Rule:** Neither the frontend nor backend assume shared disk volumes, file systems, or co-located hosts in production.

---

## 2. Universal CI/CD Pipeline Compatibility

The repository includes standard CI automation that operates agnostically across all major CI/CD providers:

### GitHub Actions (`.github/workflows/ci.yml`)
Automated matrix on push/pull request:
* **Backend Job**: Python 3.14 environment, `pip install -r requirements.txt`, `ruff check app tests`, `pytest -ra -q`.
* **Frontend Job**: Node.js 18, `npm ci`, `npx tsc --noEmit`, `npm run build`.

### GitLab CI/CD (`.gitlab-ci.yml` mapping)
```yaml
stages:
  - test
  - build

backend-test:
  stage: test
  image: python:3.14-slim
  script:
    - cd backend && pip install -r requirements.txt
    - ruff check app tests
    - pytest -ra -q

frontend-test:
  stage: test
  image: node:18-alpine
  script:
    - cd frontend && npm ci
    - npx tsc --noEmit
    - npm run build
```

### Bitbucket Pipelines / Jenkins / CircleCI
Standard steps:
1. `cd backend && pip install -r requirements.txt && ruff check app tests && pytest -ra -q`
2. `cd frontend && npm ci && npx tsc --noEmit && npm run build`

---

## 3. Frontend Hosting Targets

### Vercel (Edge / Serverless)
1. Import GitHub repository in [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Set Environment Variables:
   - `NEXT_PUBLIC_API_BASE_URL`: Live backend URL (e.g. `https://api.yourdomain.com/api/v1`).
   - `NEXT_PUBLIC_API_URL`: Live backend URL (backward compatibility).
4. Deploy. Vercel automatically builds and deploys edge-optimized static and dynamic routes.

### Netlify / Cloudflare Pages
1. Build command: `npm run build`.
2. Publish directory: `.next`.
3. Configure `NEXT_PUBLIC_API_BASE_URL` in platform build environment.

### Containerized Frontend (`frontend/Dockerfile`)
```bash
cd frontend
docker build -t uaic-frontend:latest .
docker run -d -p 3000:3000 -e NEXT_PUBLIC_API_BASE_URL=http://backend-host:8000/api/v1 uaic-frontend:latest
```

---

## 4. Backend Hosting Targets

### Render / Railway / PaaS
1. Create a **Web Service** pointing to the `backend/` root directory.
2. Build via `backend/Dockerfile` or native Python runtime.
3. Configure environment variables:
   - `DATABASE_URL`: Managed PostgreSQL connection string (`postgresql+asyncpg://...`).
   - `REDIS_URL`: Managed Redis connection string (`redis://...`).
   - `SECRET_KEY`: Production cryptographic secret.
   - `PORT`: Automatically assigned by Render/Railway (the app binds to `0.0.0.0:${PORT:-8000}`).
4. Create a companion **Background Worker** for Celery:
   - Command: `celery -A app.core.celery_app worker --concurrency=10 --loglevel=info`

### Traditional Linux VPS (Ubuntu / Debian)
1. Install Python 3.14 and Node.js 18.
2. Run backend via Systemd or Supervisord:
   ```ini
   [Unit]
   Description=UAIC FastAPI Service
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/Bot_UAIC/backend
   ExecStart=/var/www/Bot_UAIC/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

---

## 5. Cloud Providers & Container Orchestration

### Unified Docker Compose (`docker-compose.yml`)
Orchestrates the entire microservice fleet with a single command:
```bash
docker compose up -d --build
```
Services spun up:
* `db`: PostgreSQL 15 on port `5432`
* `redis`: Redis 7 on port `6379`
* `maildev`: MailDev SMTP on port `1025`, Web UI on port `1080`
* `backend`: FastAPI API server on port `8000`
* `celery_worker`: Celery distributed scraping & matching worker
* `celery_beat`: Celery scheduled periodic tasks
* `frontend`: Next.js 14 web application on port `3000`

### Kubernetes (K8s) Architecture
For enterprise clusters (AWS EKS, Google Cloud GKE, Azure AKS):
* **Deployments**:
  * `uaic-api`: Scaled deployment running `backend/Dockerfile` with horizontal pod autoscaler (HPA).
  * `uaic-worker`: Scaled deployment running `celery worker`.
  * `uaic-frontend`: Scaled deployment running `frontend/Dockerfile`.
* **Services**:
  * `uaic-api-svc`: ClusterIP exposing port 8000 to Ingress.
  * `uaic-frontend-svc`: ClusterIP exposing port 3000 to Ingress.
* **Ingress**:
  * Routes `/api/*` to `uaic-api-svc:8000`.
  * Routes `/*` to `uaic-frontend-svc:3000`.

---

## 6. Environment Variable Matrix

| Variable | Target Layer | Required | Default / Example | Purpose |
|---|---|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Frontend | Yes | `http://localhost:8000/api/v1` | Base URL for all browser API queries |
| `NEXT_PUBLIC_API_URL` | Frontend | Optional | `http://localhost:8000/api/v1` | Fallback alias for API client |
| `PORT` | Backend | Optional | `8000` | Dynamic port routing on cloud PaaS |
| `HOST` | Backend | Optional | `0.0.0.0` | Network host interface binding |
| `DATABASE_URL` | Backend | Yes | `postgresql+asyncpg://user:pass@host:5432/db` | Async SQLAlchemy database URL |
| `REDIS_URL` | Backend | Yes | `redis://host:6379/0` | Celery broker and runtime cache |
| `SECRET_KEY` | Backend | Yes | Random 64-char string | Session & token encryption |
| `GUIDEWIRE_API_URL` | Backend | Optional | `https://gw.company.com/api/caseupdate` | Guidewire ClaimCenter endpoint |
| `GUIDEWIRE_API_KEY` | Backend | Optional | Masked secret | Guidewire authentication token |