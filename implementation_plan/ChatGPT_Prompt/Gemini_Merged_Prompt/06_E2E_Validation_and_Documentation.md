# 06 - END-TO-END VALIDATION & DOCUMENTATION RECONCILIATION

## 1. ATTENDED VS UNATTENDED PARITY (E2E TESTING)
- Execute a complete mock claim workflow in **Attended Mode** (visible System Chrome GUI). Verify the Anti-Captcha extension loads and resolves challenges visibly.
- Execute the exact same workflow in **Unattended Mode** (Headless). 
- **Rule:** Everything that successfully works in Attended Mode MUST work in Unattended Mode. Automation cannot rely on manual clicks, active desktop sessions, or pre-opened browsers.
- Verify all 8 scrapers extract data, paginate correctly, generate accurate fuzzy matches, and submit correctly formatted payloads to Guidewire.

## 2. DOCUMENTATION RECONCILIATION
Perform a full forensic reconciliation of all project documentation.
- DO NOT blindly delete old documentation. Compare Original Prompts -> Historical Docs -> Actual Code.
- Consolidate all implementation data into three authoritative files with naming conversion and store in implementation_plan folder as defined in system.
  1. `master-implementation-plan.md`
  2. `master-gap-analysis.md`
  3. `master-walkthrough.md`
- Ensure `README.md` acts as the living technical booklet covering the full stack, routing, APIs, and workflows.
- Verify `.gitignore` is comprehensive (excluding `.env`, `.venv`, `node_modules`, `__pycache__`, etc.).


Suporting Docs you can ref:
1) Attended & Unattended End-to-End Validation — V4 Parity and Improvement.md  
2) Antigravity — Full Documentation Reconciliation, .gitignore & Current-State Consolidation Prompt.md 

Note: Most of them are already implemented, test before making any changes.

