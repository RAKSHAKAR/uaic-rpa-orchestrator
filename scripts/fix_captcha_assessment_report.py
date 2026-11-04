target = """```mermaid
flowchart TD
    Exc[Caught Exception / Signal] --> Classify[classify_exception]
    Match -->|SecurityBlockException| WAFCode[WAF-001 Rate Limit / WAF-002 PerimeterX]
    Match -->|CaptchaResolutionError| CapCode[CAP-004 Max Attempts Reached]
    Match -->|Session Timeout Popup| SesCode[SES-001 Session Timeout]
    Match -->|TimeoutError| NetCode[NET-001 Network Timeout]
    Match -->|Other| GenCode[ERR-001 General Error]
    
    WAFCode --> Event[ErrorEvent: Code, Category, Severity, RecoveryAction]
    CapCode --> Event
    SesCode --> Event
    NetCode --> Event
    GenCode --> Event
    
    Event --> Action{Recovery Action}
    Action -->|APPLY_PORTAL_COOLDOWN| CD[set_portal_cooldown + Schedule Celery Retry]
    Action -->|MARK_AWAITING_HUMAN| Human[Set AWAITING_HUMAN + Screenshot + Audit]
    Action -->|STOP_AND_RECOVER_SESSION| Sess[Click Continue + Re-fill Form]
    Action -->|BOUNDED_RETRY_WITH_BACKOFF| Retry[Celery Task Retry with Backoff]
```"""

replacement = """```mermaid
flowchart TD
    Exc["Caught Exception / Signal"] --> Classify["classify_exception()"]
    Classify --> Match{"Exception Type"}
    
    Match -->|"SecurityBlockException"| WAFCode["WAF-001 Rate Limit / WAF-002 PerimeterX"]
    Match -->|"CaptchaResolutionError"| CapCode["CAP-004 Max Attempts Reached"]
    Match -->|"Session Timeout Popup"| SesCode["SES-001 Session Timeout"]
    Match -->|"TimeoutError"| NetCode["NET-001 Network Timeout"]
    Match -->|"Other"| GenCode["ERR-001 General Error"]
    
    WAFCode --> Event["ErrorEvent: Code, Category, Severity, RecoveryAction"]
    CapCode --> Event
    SesCode --> Event
    NetCode --> Event
    GenCode --> Event
    
    Event --> Action{"Recovery Action"}
    Action -->|"APPLY_PORTAL_COOLDOWN"| CD["set_portal_cooldown + Schedule Celery Retry"]
    Action -->|"MARK_AWAITING_HUMAN"| Human["Set AWAITING_HUMAN + Screenshot + Audit"]
    Action -->|"STOP_AND_RECOVER_SESSION"| Sess["Click Continue + Re-fill Form"]
    Action -->|"BOUNDED_RETRY_WITH_BACKOFF"| Retry["Celery Task Retry with Backoff"]
```"""

path = "docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

norm_text = text.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

if norm_target in norm_text:
    new_text = norm_text.replace(norm_target, norm_replacement)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(new_text)
    print("SUCCESS: patched docs/Reports/CAPTCHA_ASSESSMENT_REPORT.md")
else:
    print("ERROR: target not found")
