
with open("backend/app/schemas/settings.py", encoding="utf-8") as f:
    content = f.read()

# 1. Add fields before stealth_clicks
new_fields = """    human_interaction_mode: str = Field(
        default="attended",
        description="Human interaction mode: attended (visible desktop, cursor indicator, manual intervention) or unattended (background session)",
    )
    mouse_movement_style: str = Field(
        default="bezier_natural",
        description="Mouse movement trajectory: bezier_natural (human Bézier curve + jitter), smooth, linear, or instant",
    )
    click_timeout_ms: int = Field(
        default=10000,
        ge=1000,
        le=60000,
        description="Maximum wait time for clickable element readiness in milliseconds",
    )
    screenshot_frequency_seconds: float = Field(
        default=1.0,
        ge=0.2,
        le=10.0,
        description="Interval between automated diagnostic screenshot captures in seconds",
    )
    enable_screen_recording: bool = Field(
        default=True,
        description="Enable automated screen/video recording during browser execution",
    )
    human_intervention_timeout_seconds: int = Field(
        default=180,
        ge=15,
        le=900,
        description="Timeout in seconds for operator manual intervention when CAPTCHAs require human verification",
    )
    show_cursor_trail: bool = Field(
        default=True,
        description="Render visible animated cursor indicator and click ripples on attended browser screen",
    )
"""

if "human_interaction_mode" not in content:
    target = "    stealth_clicks: bool = Field("
    content = content.replace(target, new_fields + target, 1)

# 2. Add validators after valid_typing_speed_mode
new_validators = """
    @field_validator("human_interaction_mode")
    @classmethod
    def valid_human_interaction_mode(cls, value: str) -> str:
        if value not in {"attended", "unattended"}:
            raise ValueError("human_interaction_mode must be attended or unattended")
        return value

    @field_validator("mouse_movement_style")
    @classmethod
    def valid_mouse_movement_style(cls, value: str) -> str:
        if value not in {"bezier_natural", "smooth", "linear", "instant"}:
            raise ValueError("mouse_movement_style must be bezier_natural, smooth, linear, or instant")
        return value
"""

if "valid_human_interaction_mode" not in content:
    target_v = """    @field_validator("typing_speed_mode")
    @classmethod
    def valid_typing_speed_mode(cls, value: str) -> str:
        if value not in {"turbo", "fast", "balanced", "cautious"}:
            raise ValueError("typing_speed_mode must be turbo, fast, balanced, or cautious")
        return value"""
    # handle both CRLF and LF
    target_v_cr = target_v.replace("\n", "\r\n")
    if target_v in content:
        content = content.replace(target_v, target_v + new_validators, 1)
    elif target_v_cr in content:
        content = content.replace(target_v_cr, target_v_cr + new_validators.replace("\n", "\r\n"), 1)
    else:
        print("Could not match target_v exactly!")

with open("backend/app/schemas/settings.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully patched backend/app/schemas/settings.py")

