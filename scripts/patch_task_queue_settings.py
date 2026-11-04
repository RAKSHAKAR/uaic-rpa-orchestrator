with open("backend/app/schemas/settings.py", encoding="utf-8") as f:
    content = f.read()

target = """    failed_claims_retry_interval_minutes: int = Field(
        default=0,
        ge=0,
        le=1440,
        description="Interval in minutes between automatic retriggers of failed claims via Celery Beat (0 = fallback to task_retry_delay_seconds)",
    )"""

addition = """
    failed_claims_retry_interval_value: int | None = Field(
        default=60,
        description="Interval value for automated retriggering of failed claims",
    )
    failed_claims_retry_interval_unit: str | None = Field(
        default="minutes",
        description="Unit for automated retriggering (minutes, hours, seconds)",
    )
    failed_claims_retry_interval_seconds: int | None = Field(
        default=3600,
        description="Interval in seconds for automated retriggering of failed claims",
    )"""

if "failed_claims_retry_interval_value" not in content:
    if target in content:
        content = content.replace(target, target + addition, 1)
    else:
        target_cr = target.replace("\n", "\r\n")
        if target_cr in content:
            content = content.replace(target_cr, target_cr + addition.replace("\n", "\r\n"), 1)

with open("backend/app/schemas/settings.py", "w", encoding="utf-8") as f:
    f.write(content)

print("TaskQueueSettings patched successfully.")

