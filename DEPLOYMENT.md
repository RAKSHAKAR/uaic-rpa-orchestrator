# Multi-Platform Deployment Architecture: UAIC RPA Orchestrator

This document outlines the multi-target deployment blueprint for running the system across Vercel, Render, VPS, and Docker containers.

---

# Phase 0: Fresh GitHub Repository Initialization & Push
Before deploying your application to Vercel, Render, or a VPS, you must initialize your local codebase as a fresh repository and push it to GitHub using the provided automation script:

1. Open PowerShell in your root project folder (`Bot_UAIC\`).
2. Run the deployment script:
   ```powershell
   .\Deploy-To-GitHub.ps1
   ```

## Target 1: Frontend on Vercel (Recommended for UI)
1. Push your repository to GitHub using `Deploy-To-GitHub.ps1`.
2. Log into [Vercel](https://vercel.com) and import your repository.
3. Set the **Root Directory** to `frontend`.
4. Configure the environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` (or `VITE_API_BASE_URL` depending on your build tool) pointing to your live backend URL (e.g., `https://api.yourdomain.com` or your Render backend URL).
5. Click **Deploy**. Vercel handles global static delivery automatically.

---

## Target 2: Backend on Render / Railway (Managed Containers)
1. Create a new **Web Service** on [Render](https://render.com) connected to your GitHub repository.
2. Set the **Root Directory** to `backend`.
3. Set the **Environment** to `Docker`.
4. Add the required environment variables (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`).
5. Deploy. Render will utilize your `backend/Dockerfile` to spin up FastAPI. Note: For Celery workers, configure a separate Render Background Worker pointing to the same repository using the celery command.

---

## Target 3: Full Stack Local/VPS Deployment (Docker Compose)
To run the entire system locally or on an Ubuntu VPS:
1. Ensure your `.env` file is configured in the root directory.
2. Run the master composition command:
   ```bash
   docker compose up -d --build