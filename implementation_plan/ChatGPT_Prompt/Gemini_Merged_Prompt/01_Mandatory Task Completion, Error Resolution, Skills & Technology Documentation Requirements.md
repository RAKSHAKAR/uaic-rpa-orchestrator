# Mandatory Task Completion, Error Resolution, Skills & Technology Documentation Requirements

## 1. TASK COMPLETION & CONTINUATION — MANDATORY

### Current Problems / Tasks

For every task or requirement that has been assigned, you must:

1. **Complete every assigned task fully.**
2. Do not mark a task as completed merely because the implementation was partially added.
3. Verify that the requested functionality actually works end-to-end.
4. If your execution is interrupted, terminated, crashed, timed out, or stopped because of an error, **you must continue from the last successful point** and complete all remaining work.
5. Never silently skip tasks because:
   - Agent execution was terminated.
   - A command failed.
   - A dependency failed.
   - A build failed.
   - A test failed.
   - A browser/test environment crashed.
   - A terminal process stopped.
   - A previous implementation caused another error.
   - The task became large or complex.
6. Before reporting that the work is complete, review the original requirements and verify that **nothing has been missed**.
7. If any task remains incomplete, continue working on it instead of reporting completion.

### Mandatory Completion Rule

> **"Task completed" means implemented + verified + tested + all discovered issues fixed.**

Do not report "Done", "Completed", or equivalent until this condition is satisfied.

---

# 2. CONSOLE & TERMINAL ERROR RESOLUTION — MANDATORY

Before reporting that any work is complete, you must always check and resolve **all relevant errors and problems**.

### Browser / Application Console

You must:

- Open and test the application in the browser where applicable.
- Check the browser Developer Console.
- Identify all:
  - Errors
  - Exceptions
  - Failed requests
  - Unhandled promise rejections
  - React errors/warnings
  - TypeScript/runtime errors
  - Resource loading failures
  - API errors
  - Authentication errors
  - CORS errors
  - Network failures
  - Broken imports
  - Invalid routes
  - Accessibility-related errors where applicable
- Fix the root cause of every relevant issue.
- Re-test after fixing.

### Terminal / Development Environment

You must also check all relevant terminal output and resolve:

- Build errors
- Compilation errors
- TypeScript errors
- Lint errors
- Test failures
- Dependency errors
- Migration errors
- Database errors
- API/server startup errors
- Configuration errors
- Runtime exceptions
- Import/export errors
- Port/process errors
- Docker/container errors where applicable
- Any other errors introduced by the implementation

### No Error Left Behind

Do **not** respond with:

> "The task is completed."

while known relevant errors remain in the browser console, terminal, build, tests, or runtime.

If an error cannot be immediately resolved because it is caused by an external dependency or infrastructure limitation, explicitly document:

- The exact error.
- The root cause.
- What was attempted.
- Why it cannot currently be resolved.
- The impact.
- The recommended next action.

Do not hide or ignore the issue.

---

# 3. MISSED-TASK RECOVERY — MANDATORY

Whenever continuing an existing implementation, first determine:

1. What requirements were requested.
2. What has already been implemented.
3. What has been partially implemented.
4. What has not yet been implemented.
5. What implementations are broken.
6. What tests have already been completed.
7. What tests are still required.
8. What errors currently exist.

Then continue implementation from the current state.

### Important

If the previous agent execution stopped unexpectedly, **do not assume that all previous tasks were completed**.

Perform a proper gap analysis and continue with every missing or incomplete task.

The same rule applies after:

- Context limits.
- Agent restart.
- Terminal failure.
- Browser failure.
- Build failure.
- Test failure.
- Process termination.
- IDE restart.
- Dependency installation failure.
- Any other interruption.

---

# 4. SKILLS MUST BE UPDATED

These requirements must be permanently added to the appropriate project/agent **Skills** so they are automatically followed in future tasks.

The Skills must explicitly enforce:

- Complete all assigned tasks.
- Perform task-gap analysis before declaring completion.
- Resume interrupted work.
- Never silently skip incomplete work.
- Always check browser console errors.
- Always check terminal errors.
- Always run appropriate validation/testing.
- Fix discovered errors before completion.
- Verify functionality rather than relying only on code changes.
- Document unresolved external blockers when applicable.

These rules must become part of the standard development workflow and must not be treated as a one-time instruction.

---

# 5. TECHNOLOGY STACK DOCUMENTATION — MANDATORY

For **every technology, framework, library, platform, service, tool, runtime, database, ORM, testing framework, build tool, authentication technology, deployment technology, or major dependency** used to create this solution, maintain documentation in the project's `README.md`.

The documentation must help a new developer understand:

1. **What technology is being used.**
2. **Why it is being used.**
3. **What role it plays in this solution.**
4. **How it integrates with the rest of the application.**
5. **What major functionality/features of that technology are being used.**
6. **Where it is used in the codebase**, when practical.
7. **The official documentation URL** where developers can learn more.

---

# 6. README.md — TECHNOLOGY REFERENCE SECTION

The project's `README.md` must contain a dedicated section such as:

## Technology Stack & Documentation

Maintain a concise table similar to:

| Technology | Purpose in This Solution | How We Use It | Official Documentation |
|---|---|---|---|
| Technology A | Short explanation | How it is used here | Official documentation URL |
| Technology B | Short explanation | How it is used here | Official documentation URL |
| Technology C | Short explanation | How it is used here | Official documentation URL |

The documentation should cover, where applicable:

### Frontend

- Framework
- UI library
- CSS framework
- Component library
- State management
- Routing
- Form handling
- Validation
- HTTP/API client
- Icons
- Charts
- Rich text/editor libraries

### Backend

- Runtime
- Programming language
- Backend framework
- API framework
- ORM
- Database
- Authentication
- Authorization/RBAC
- Validation
- Background jobs
- Queue system
- Caching
- Logging
- Monitoring

### Testing

- Unit testing framework
- Integration testing
- API testing
- End-to-end testing
- Browser automation
- Test utilities
- Mocking tools

### Build & Development

- Package manager
- Build tool
- Bundler
- Compiler
- Linter
- Formatter
- Git tooling
- Development scripts

### Infrastructure & Deployment

- Docker
- Cloud platform
- Hosting platform
- CI/CD
- Reverse proxy
- Database hosting
- Storage
- CDN
- Environment/configuration management

### Integrations

Document major external technologies/services such as:

- Google APIs
- Google Business Profile APIs
- Meta APIs
- Microsoft APIs
- Social media APIs
- Email providers
- SMS providers
- WhatsApp providers
- Payment providers
- AI providers
- SEO services
- Analytics services

Only document technologies that are actually used by the solution. Do not add technologies merely because they are possible options.

---

# 7. OFFICIAL DOCUMENTATION LINKS

Whenever documenting a technology, use its **official documentation** whenever an official documentation website exists.

For example:

- React → official React documentation
- TypeScript → official TypeScript documentation
- Node.js → official Node.js documentation
- PostgreSQL → official PostgreSQL documentation
- Prisma → official Prisma documentation
- Playwright → official Playwright documentation
- Docker → official Docker documentation

Do not rely on random blogs as the primary documentation reference.

If an official documentation URL changes, update the README accordingly.

---

# 8. KEEP README.md UP TO DATE

The technology documentation must be maintained continuously.

Whenever you:

- Add a new technology.
- Remove a technology.
- Replace a technology.
- Upgrade to a materially different version.
- Introduce a new major framework/library.
- Add a new external integration.
- Change the architecture.

You must review and update the relevant `README.md` documentation.

Do not allow the README technology section to become outdated.

---

# 9. DEVELOPMENT WORKFLOW — REQUIRED ORDER

For every implementation task, follow this general workflow:

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
Update relavant all kind of documentaiton in docs folder
        ↓
Update README.md
        ↓
Update Skills if Required
        ↓
Final Requirement-by-Requirement Verification
        ↓
Only Then Report Completion
```

---

# 10. FINAL COMPLETION CHECKLIST

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

# 11. NON-NEGOTIABLE RULE

**Never consider a task complete just because code was written.**

A task is complete only when:

> **Implemented → Tested → Verified → Errors Fixed → Documentation Updated → Requirements Rechecked**

This rule must be followed for all future development work in this solution.