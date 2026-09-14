# UAIC Development Workflow & Completion Checklist

## 1. DEVELOPMENT WORKFLOW — REQUIRED ORDER

For every implementation task, follow this exact workflow to ensure stability and completeness:

```text
Understand Requirements
        ↓
Inspect Existing Implementation
        ↓
Identify Completed / Partial / Missing Work
        ↓
Create Task Gap Analysis
        ↓
Implement Missing Work
        ↓
Run Build / Type Checks
        ↓
Run Unit / Integration Tests
        ↓
Run Application
        ↓
Test in Browser Where Applicable
        ↓
Check Browser Console
        ↓
Check Network/API Errors
        ↓
Check Terminal / Server Logs
        ↓
Fix All Relevant Errors
        ↓
Create Missing Test/Re-run Tests
        ↓
Re-check Browser
        ↓
Update relevant documentation in docs folder
        ↓
Update README.md
        ↓
Update Skills if Required
        ↓
Final Requirement-by-Requirement Verification
        ↓
Only Then Report Completion
```

## 2. FINAL COMPLETION CHECKLIST

Before saying the work is complete, verify all of the following:

- [ ] Every requested task is implemented.
- [ ] No task was silently skipped.
- [ ] Interrupted/missed tasks have been recovered and completed.
- [ ] Existing functionality has not been unnecessarily broken.
- [ ] Build succeeds.
- [ ] Type checking succeeds.
- [ ] Relevant linting succeeds.
- [ ] Relevant automated tests pass.
- [ ] Application starts successfully.
- [ ] Relevant browser flows were tested.
- [ ] Browser console has no relevant errors.
- [ ] Network/API calls work correctly.
- [ ] Terminal/server logs have no relevant unresolved errors.
- [ ] Database/migrations work where applicable.
- [ ] UI/UX behavior has been verified where applicable.
- [ ] Dark/Light mode behavior has been verified where applicable.
- [ ] Responsive behavior has been verified where applicable.
- [ ] Documentation update in docs folder.
- [ ] README.md reflects the current technology stack.
- [ ] Official documentation references are present.
- [ ] Skills contain these mandatory development/completion rules.
- [ ] Final requirement-by-requirement gap analysis has been completed.

---

> **NON-NEGOTIABLE RULE**  
> Never consider a task complete just because code was written. A task is complete only when:  
> **Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked**
