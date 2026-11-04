with open("frontend/src/app/settings/page.tsx", encoding="utf-8") as f:
    content = f.read()

target = "{/* Anti-Captcha Decoupled Notice Banner */}"
card_html = """{/* ========================================================================= */}
              {/* GENUINE HUMAN INTERACTION & DESKTOP OBSERVABILITY                         */}
              {/* ========================================================================= */}
              <div className="sm:col-span-2 space-y-4 p-5 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-gradient-to-r from-rose-50/40 via-amber-50/20 to-slate-50 dark:from-rose-950/20 dark:via-amber-950/10 dark:to-slate-900 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-rose-200/70 dark:border-rose-900/40">
                  <div>
                    <div className="flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-rose-500" />
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100 uppercase tracking-wider">
                        Genuine Human Interaction &amp; Desktop Observability
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-700 dark:text-rose-300 font-mono text-[10px] font-bold border border-rose-500/20">
                        Physical Browser Controls
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                      Controls authentic physical mouse pointer movements, on-screen cursor visibility, keyboard typing cadence, address bar navigation, and attended human intervention.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 dark:text-slate-400">Interaction Mode:</span>
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold text-white shadow-xs ${
                      (settings.automation.human_interaction_mode || "attended") === "attended" ? "bg-rose-600" : "bg-slate-600"
                    }`}>
                      {(settings.automation.human_interaction_mode || "attended").toUpperCase()}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {/* Human Interaction Mode */}
                  <div className="p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1.5">
                    <label className="text-xs font-semibold text-slate-800 dark:text-slate-200">Execution Mode</label>
                    <select
                      value={settings.automation.human_interaction_mode || "attended"}
                      onChange={(e) => setSettings({
                        ...settings,
                        automation: { ...settings.automation, human_interaction_mode: e.target.value as "attended" | "unattended" }
                      })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200"
                    >
                      <option value="attended">Attended (Visible GUI, Cursor Trail, Intervention)</option>
                      <option value="unattended">Unattended (Background Desktop Session)</option>
                    </select>
                    <p className="text-[10px] text-slate-500">Attended mode displays physical browser and cursor movements.</p>
                  </div>

                  {/* Mouse Movement Style */}
                  <div className="p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1.5">
                    <label className="text-xs font-semibold text-slate-800 dark:text-slate-200">Mouse Trajectory Style</label>
                    <select
                      value={settings.automation.mouse_movement_style || "bezier_natural"}
                      onChange={(e) => setSettings({
                        ...settings,
                        automation: { ...settings.automation, mouse_movement_style: e.target.value as any }
                      })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200"
                    >
                      <option value="bezier_natural">Bézier Natural (Human Curve + Micro-Jitter)</option>
                      <option value="smooth">Smooth (Cubic Interpolation)</option>
                      <option value="linear">Linear (Direct Path)</option>
                      <option value="instant">Instant (Warp)</option>
                    </select>
                    <p className="text-[10px] text-slate-500">Bézier curve emulates organic human hand movement.</p>
                  </div>

                  {/* Click Timeout */}
                  <div className="p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1.5">
                    <div className="flex justify-between items-center">
                      <label className="text-xs font-semibold text-slate-800 dark:text-slate-200">Click Timeout</label>
                      <span className="font-mono text-xs font-bold text-rose-600">{settings.automation.click_timeout_ms ?? 10000}ms</span>
                    </div>
                    <input
                      type="number"
                      min="1000"
                      max="60000"
                      step="500"
                      value={settings.automation.click_timeout_ms ?? 10000}
                      onChange={(e) => setSettings({
                        ...settings,
                        automation: { ...settings.automation, click_timeout_ms: parseInt(e.target.value) || 10000 }
                      })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200"
                    />
                    <p className="text-[10px] text-slate-500">Max wait for element clickable state before dwell.</p>
                  </div>

                  {/* Human Intervention Timeout */}
                  <div className="p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800 space-y-1.5">
                    <div className="flex justify-between items-center">
                      <label className="text-xs font-semibold text-slate-800 dark:text-slate-200">Intervention Timeout</label>
                      <span className="font-mono text-xs font-bold text-rose-600">{settings.automation.human_intervention_timeout_seconds ?? 180}s</span>
                    </div>
                    <input
                      type="number"
                      min="15"
                      max="900"
                      step="15"
                      value={settings.automation.human_intervention_timeout_seconds ?? 180}
                      onChange={(e) => setSettings({
                        ...settings,
                        automation: { ...settings.automation, human_intervention_timeout_seconds: parseInt(e.target.value) || 180 }
                      })}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-900 dark:text-slate-200"
                    />
                    <p className="text-[10px] text-slate-500">Operator intervention pause time for pending challenges.</p>
                  </div>

                  {/* Visible Cursor Trail Toggle */}
                  <div className="flex items-center justify-between p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800">
                    <div className="space-y-0.5 pr-2">
                      <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">On-Screen Cursor Trail</span>
                      <p className="text-[10px] text-slate-500">Visual pointer &amp; click ripple in recordings</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        checked={settings.automation.show_cursor_trail ?? true}
                        onChange={(e) => setSettings({
                          ...settings,
                          automation: { ...settings.automation, show_cursor_trail: e.target.checked }
                        })}
                        className="sr-only peer"
                      />
                      <div className="w-8 h-4 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-rose-600"></div>
                    </label>
                  </div>

                  {/* Enable Screen Recording Toggle */}
                  <div className="flex items-center justify-between p-3 bg-white/70 dark:bg-slate-900/70 rounded-lg border border-slate-200 dark:border-slate-800">
                    <div className="space-y-0.5 pr-2">
                      <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">Screen Recording</span>
                      <p className="text-[10px] text-slate-500">Captures genuine execution videos &amp; frames</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer shrink-0">
                      <input
                        type="checkbox"
                        checked={settings.automation.enable_screen_recording ?? true}
                        onChange={(e) => setSettings({
                          ...settings,
                          automation: { ...settings.automation, enable_screen_recording: e.target.checked }
                        })}
                        className="sr-only peer"
                      />
                      <div className="w-8 h-4 bg-slate-200 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-rose-600"></div>
                    </label>
                  </div>
                </div>
              </div>

              """

if target in content and "GENUINE HUMAN INTERACTION" not in content:
    content = content.replace(target, card_html + target, 1)
    with open("frontend/src/app/settings/page.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Settings UI successfully updated!")
else:
    print("Target not found or already patched!")

