from pathlib import Path

settings_file = Path(r"c:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\frontend\src\app\settings\page.tsx")
content = settings_file.read_text(encoding="utf-8").replace("\r\n", "\n")

helper_def = """  const previewAutomation = (partial: any) => {
    if (typeof window !== "undefined") {
      const merged = { ...(settings?.automation || {}), ...partial };
      window.dispatchEvent(new CustomEvent("uaic:settings-preview", { detail: { automation: merged } }));
      try {
        localStorage.setItem("uaic_automation_settings", JSON.stringify(merged));
      } catch {}
    }
  };
"""

# Insert helper before handleSave
if "const previewAutomation =" not in content:
    content = content.replace("  const handleSave = async (e?: React.FormEvent) => {", helper_def + "\n  const handleSave = async (e?: React.FormEvent) => {", 1)

# Hook into browser_engine onChange for chromium
old_cr = """                          const engine = "chromium";
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""
new_cr = """                          const engine = "chromium";
                          previewAutomation({ browser_engine: engine });
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""

# Hook into browser_engine onChange for chrome
old_ch = """                          const engine = "chrome";
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""
new_ch = """                          const engine = "chrome";
                          previewAutomation({ browser_engine: engine });
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""

# Hook into browser_engine onChange for msedge
old_ed = """                          const engine = "msedge";
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""
new_ed = """                          const engine = "msedge";
                          previewAutomation({ browser_engine: engine });
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              browser_engine: engine,
                              user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                            },
                          });"""

# Hook into headless_mode onClick (Attended)
old_att = """                      onClick={() =>
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            headless_mode: false,
                          },
                        })
                      }"""
new_att = """                      onClick={() => {
                        previewAutomation({ headless_mode: false });
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            headless_mode: false,
                          },
                        });
                      }}"""

# Hook into headless_mode onClick (Headless)
old_hd = """                      onClick={() =>
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            headless_mode: true,
                          },
                        })
                      }"""
new_hd = """                      onClick={() => {
                        previewAutomation({ headless_mode: true });
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            headless_mode: true,
                          },
                        });
                      }}"""

content = content.replace(old_cr, new_cr, 1)
content = content.replace(old_ch, new_ch, 1)
content = content.replace(old_ed, new_ed, 1)
content = content.replace(old_att, new_att, 1)
content = content.replace(old_hd, new_hd, 1)

settings_file.write_text(content, encoding="utf-8")
print("SUCCESS: Successfully hooked previewAutomation into page.tsx")
