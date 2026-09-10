# 01 - FOUNDATION: PYTHON 3.14.7 & STRICT DEVELOPMENT RULES

## 1. PYTHON RUNTIME & DEPENDENCIES
- Update the existing implementation to target **Python 3.14.7** exclusively. Verify using `python --version`.
- Audit and modernize all dependencies (FastAPI, Uvicorn, Pydantic, SQLAlchemy, Celery, Redis, Playwright, RapidFuzz) to 3.14.7 compatible versions.
- Implement asynchronous architecture (e.g., `async def`, connection pooling) for APIs and DB queries, but **DO NOT** force browser automation to be asynchronous if it destabilizes the Anti-Captcha extension.

## 2. MANDATORY TASK COMPLETION RULES
- **No Error Left Behind:** Before reporting completion, you MUST check the browser Developer Console and the Terminal for errors (unhandled promises, React errors, build failures, API errors). Fix the root causes.
- **Interruption Recovery:** If execution crashes, times out, or is interrupted, you must perform a gap analysis and resume from the last successful point. Never silently skip tasks.
- **Definition of Done:** Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked.

## 3. TECHNOLOGY STACK DOCUMENTATION
- Maintain a dedicated "Technology Stack & Documentation" section in the `README.md`.
- Document the Frontend, Backend, Testing, Build, Infrastructure, and Integrations used, including links to official documentation (e.g., official React, FastAPI, Docker docs).


Suporting Docs you can ref:
1) PYTHON 3.14.7 — RUNTIME, LIBRARY, PERFORMANCE & MODERNIZATION UPDATE.md  
2) Mandatory Task Completion, Error Resolution, Skills & Technology Documentation Requirements.md

Note: Most of them are already implemented, test before making any changes.


