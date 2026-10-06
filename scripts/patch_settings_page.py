import re
from pathlib import Path

settings_file = Path(r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\frontend\src\app\settings\page.tsx")
content = settings_file.read_text(encoding="utf-8")

# 1. Patch handleSave
save_target = """      if (updated.branding) {
        updateBranding(updated.branding);
      }
      setFeedback({"""

save_replacement = """      if (updated.branding) {
        updateBranding(updated.branding);
      }
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("uaic:settings-updated", { detail: updated }));
        if (updated.automation) {
          try {
            localStorage.setItem("uaic_automation_settings", JSON.stringify(updated.automation));
          } catch {}
        }
      }
      setFeedback({"""

# 2. Patch handleReset
reset_target = """      if (def.branding) {
        updateBranding(def.branding);
      }
      setFeedback({"""

reset_replacement = """      if (def.branding) {
        updateBranding(def.branding);
      }
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("uaic:settings-updated", { detail: def }));
        if (def.automation) {
          try {
            localStorage.setItem("uaic_automation_settings", JSON.stringify(def.automation));
          } catch {}
        }
      }
      setFeedback({"""

# Normalize CRLF for matching
content_norm = content.replace("\r\n", "\n")

if save_target in content_norm and reset_target in content_norm:
    content_norm = content_norm.replace(save_target, save_replacement, 1)
    content_norm = content_norm.replace(reset_target, reset_replacement, 1)
    # Write back keeping CRLF or LF as appropriate
    settings_file.write_text(content_norm, encoding="utf-8")
    print("SUCCESS: Successfully patched handleSave and handleReset in page.tsx")
else:
    print("WARNING: Targets not found in page.tsx")
