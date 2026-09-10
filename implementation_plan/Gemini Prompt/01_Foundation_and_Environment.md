# 01 - FOUNDATION: PYTHON 3.14.7, ENVIRONMENT & STRICT DEVELOPMENT TASK COMPLETION RULES

## 1. PYTHON RUNTIME & ENVIRONMENT
You must update the existing implementation to officially target Python 3.14.7.
- Verify `python --version` returns 3.14.7.
- Audit and modernize all dependencies (FastAPI, Uvicorn, Pydantic, SQLAlchemy, Celery, Redis, Playwright, RapidFuzz) to versions compatible with 3.14.7.
- Do NOT blindly upgrade packages if it breaks existing functionality.
- Implement asynchronous architecture where suitable (e.g., `async def`, connection pooling) for APIs and DB queries, but **do NOT** force/make browser automation artificially asynchronous if it destabilizes the Anti-Captcha extension.

## 2. MANDATORY TASK COMPLETION RULES
- Never consider a task complete just because code was written. 
- **No Error Left Behind:** Before reporting completion, you MUST check the browser Developer Console and the Terminal for errors (unhandled promises, React errors, build failures, API errors). Fix the root causes.
- **Interruption Recovery:** If execution crashes, times out, or is interrupted, you must perform a gap analysis and resume from the last successful point. Never silently skip tasks.
- Check the browser Developer Console and Terminal for errors (CORS, unhandled promises, build errors). Fix them before reporting completion.
- **Definition of Done:** Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked.

## 3. TECHNOLOGY STACK DOCUMENTATION
- Maintain a dedicated "Technology Stack & Documentation" section in the `README.md` .
- Document the Frontend, Backend, Testing, Build, Infrastructure, and Integrations used, including links to official documentation (e.g., official React, FastAPI, Docker docs)


Supporting Docs you can ref:
    1) PYTHON 3.14.7 — RUNTIME, LIBRARY, PERFORMANCE & MODERNIZATION UPDATE.md
    2) Mandatory Task Completion, Error Resolution, Skills & Technology Documentation Requirements.md
Note: Most of them are already implemented, test before making any changes.
