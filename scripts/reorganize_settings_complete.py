import os
import shutil

src_file = os.path.join("frontend", "src", "app", "settings", "page.tsx")
bak_file = src_file + ".bak"

if not os.path.exists(bak_file):
    shutil.copyfile(src_file, bak_file)

with open(bak_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update tabs navigation array
old_tabs = """  const tabs = [
    { id: "guidewire", label: "APIs", icon: Zap },
    { id: "portals", label: "County Court Portals", icon: Globe },
    { id: "automation", label: "Browser & CAPTCHA", icon: ShieldCheck },
    { id: "proxy", label: "Proxy Settings", icon: Network },
    { id: "extension", label: "AntiCaptcha Extension", icon: Plug },
    { id: "email", label: "Email & Notifications", icon: Mail },
    { id: "storage", label: "Storage & Error Screenshots", icon: HardDrive },
    { id: "matcher", label: "RapidFuzz & Filters", icon: Sparkles },
    { id: "queue", label: "Task Queue & Alerts", icon: Layers },
  ];"""

new_tabs = """  const tabs = [
    { id: "guidewire", label: "APIs & Matching Engine", icon: Zap },
    { id: "portals", label: "County Court Portals", icon: Globe },
    { id: "automation", label: "Browser Automation & Fleet", icon: ShieldCheck },
    { id: "extension", label: "CAPTCHA Solver & Extension", icon: Plug },
    { id: "proxy", label: "Proxy Network", icon: Network },
    { id: "email", label: "Email & Notifications", icon: Mail },
    { id: "storage", label: "Storage & Retention", icon: HardDrive },
    { id: "queue", label: "Task Queue & Telemetry", icon: Layers },
  ];"""

assert old_tabs in content, "old_tabs not found in backup file!"
content = content.replace(old_tabs, new_tabs)
print("[OK] Replaced tabs navigation array")

# 2. Extract RapidFuzz card from matcher tab
matcher_start_str = '{activeTab === "matcher" && ('
queue_start_str = '{activeTab === "queue" && ('

idx_m = content.find(matcher_start_str)
idx_q = content.find(queue_start_str)
assert idx_m != -1 and idx_q != -1, "matcher or queue block not found!"

matcher_block = content[idx_m:idx_q]
card_start_str = '<div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">'
c_start = matcher_block.find(card_start_str)
c_end = matcher_block.rfind('</div>') + len('</div>')
rapidfuzz_card = matcher_block[c_start:c_end]
print(f"[OK] Extracted RapidFuzz card ({len(rapidfuzz_card)} chars)")

# Delete matcher tab from content
content = content[:idx_m] + content[idx_q:]
print("[OK] Removed matcher tab block")

# Insert RapidFuzz card into guidewire tab before Fuzzy Match API Tester Card
fuzzy_tester_comment = '{/* Fuzzy Match API Tester Card */}'
assert fuzzy_tester_comment in content, "fuzzy_tester_comment not found!"
content = content.replace(fuzzy_tester_comment, rapidfuzz_card + "\n\n            " + fuzzy_tester_comment)
print("[OK] Inserted RapidFuzz card into APIs tab")

# 3. Reconstruct 'automation' tab cleanly without duplicate AntiCaptcha cards
# Let's locate the automation block
auto_start_str = '{activeTab === "automation" && ('
proxy_start_str = '{activeTab === "proxy" && ('

idx_auto = content.find(auto_start_str)
idx_proxy = content.find(proxy_start_str)
assert idx_auto != -1 and idx_proxy != -1, "automation or proxy block not found!"

auto_block = content[idx_auto:idx_proxy]

# Let's see what we need inside clean automation block:
clean_auto_block = """{activeTab === "automation" && (
          <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 md:p-8 space-y-6 shadow-xs w-full transition-colors">
            <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
              <ShieldCheck className="w-5 h-5 text-indigo-500" />
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                  Browser Automation &amp; RPA Execution Fleet
                </h3>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Configure parallel worker concurrency fleet, navigation timeouts, browser engine, and live launch testing.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
              {/* Concurrent RPA Claim Executions (1 to 10 Parallel Claims) */}
              <div className="sm:col-span-2 space-y-3 p-4 rounded-xl border border-indigo-200 dark:border-indigo-800/60 bg-gradient-to-r from-indigo-50/60 via-purple-50/40 to-slate-50 dark:from-indigo-950/30 dark:via-purple-950/20 dark:to-slate-900">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-md bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 font-bold text-xs">
                        Parallel RPA Concurrency
                      </span>
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                        Concurrent Scraper Worker Fleet (1 – 10 Parallel Claims)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1">
                      Controls how many court portal scrapers and claims execute concurrently in parallel. 1 = Sequential FIFO execution, 10 = Maximum high-throughput parallel fleet.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 dark:text-slate-400">Current Fleet:</span>
                    <span className="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-bold bg-indigo-600 text-white shadow-xs">
                      {settings.automation.max_concurrent_claims || 3}x Parallel Workers
                    </span>
                  </div>
                </div>

                <div className="space-y-2 pt-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 dark:text-slate-400 font-mono text-[10px]">1 Worker (Sequential)</span>
                    <span className="font-mono text-xs font-extrabold text-indigo-600 dark:text-indigo-400 bg-white dark:bg-slate-900 px-2.5 py-0.5 rounded-md border border-indigo-200 dark:border-indigo-800 shadow-2xs">
                      {settings.automation.max_concurrent_claims || 3} Parallel Workers
                    </span>
                    <span className="text-slate-500 dark:text-slate-400 font-mono text-[10px]">10 Workers (Max Concurrency)</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    value={settings.automation.max_concurrent_claims || 3}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          max_concurrent_claims: parseInt(e.target.value, 10) || 1,
                        },
                      })
                    }
                    className="w-full accent-indigo-600 cursor-pointer h-2 bg-slate-200 dark:bg-slate-700 rounded-lg"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 font-mono px-0.5">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
                      <button
                        key={n}
                        type="button"
                        onClick={() =>
                          setSettings({
                            ...settings,
                            automation: {
                              ...settings.automation,
                              max_concurrent_claims: n,
                            },
                          })
                        }
                        className={`hover:text-indigo-600 cursor-pointer transition-colors ${
                          (settings.automation.max_concurrent_claims || 3) === n
                            ? "font-bold text-indigo-600 dark:text-indigo-400"
                            : ""
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Preset quick buttons */}
                <div className="flex items-center gap-2 pt-1 border-t border-indigo-100 dark:border-indigo-900/60 flex-wrap text-xs">
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold">Quick Presets:</span>
                  {[
                    { label: "Sequential (1)", val: 1 },
                    { label: "Conservative (2)", val: 2 },
                    { label: "Recommended (3)", val: 3 },
                    { label: "Balanced (5)", val: 5 },
                    { label: "High Throughput (8)", val: 8 },
                    { label: "Max Speed (10)", val: 10 },
                  ].map((p) => (
                    <button
                      key={p.val}
                      type="button"
                      onClick={() =>
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            max_concurrent_claims: p.val,
                          },
                        })
                      }
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold cursor-pointer transition-all ${
                        (settings.automation.max_concurrent_claims || 3) === p.val
                          ? "bg-indigo-600 text-white shadow-2xs"
                          : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-indigo-400"
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Page Timeout */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Portal Navigation Timeout (Seconds)
                  </label>
                  <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                    {settings.automation.page_timeout_seconds}s
                  </span>
                </div>
                <input
                  type="number"
                  min="5"
                  max="120"
                  value={settings.automation.page_timeout_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        page_timeout_seconds: parseInt(e.target.value) || 30,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                  Maximum network idle wait time before scraper fails over or attempts recovery.
                </p>
              </div>

              {/* Page Reload Backoff Delay */}
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <label className="font-semibold text-slate-700 dark:text-slate-300">
                    Page Reload Backoff Delay (Seconds)
                  </label>
                  <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                    {settings.automation.reload_backoff_seconds}s
                  </span>
                </div>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={settings.automation.reload_backoff_seconds}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        reload_backoff_seconds: parseInt(e.target.value) || 2,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                />
                <p className="text-[10px] text-slate-500 dark:text-slate-400">
                  Delay before retrying or re-navigating after CAPTCHA timeout or network reset.
                </p>
              </div>

              {/* Browser Automation Engine Selector */}
              <div className="sm:col-span-2 space-y-3 pt-2 border-t border-slate-200 dark:border-slate-800/80">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-800 dark:text-slate-200 text-xs block">
                    Browser Automation Engine
                  </label>
                  <span className="text-[10px] text-indigo-600 dark:text-indigo-400 font-semibold bg-indigo-50 dark:bg-indigo-950/50 px-2 py-0.5 rounded border border-indigo-200 dark:border-indigo-800">
                    Extension Compatibility Core
                  </span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {/* Option 1: Chromium */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      (settings.automation.browser_engine || "chromium") === "chromium"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="chromium"
                      checked={(settings.automation.browser_engine || "chromium") === "chromium"}
                      onChange={() => {
                        const engine = "chromium";
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: engine,
                            user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
                        <Laptop className="w-3.5 h-3.5 text-indigo-500" />
                        Chromium (Bundled)
                      </span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                        Default
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight">
                      Playwright bundled Chromium. Highest reliability, seamless unpacked extension loading, zero policy interference.
                    </p>
                  </label>

                  {/* Option 2: Google Chrome */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings.automation.browser_engine === "chrome"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="chrome"
                      checked={settings.automation.browser_engine === "chrome"}
                      onChange={() => {
                        const engine = "chrome";
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: engine,
                            user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">Google Chrome</span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                        Installed
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight">
                      System installed Google Chrome. Note: Enterprise-managed Chrome will automatically fall back to Chromium if extensions are blocked.
                    </p>
                  </label>

                  {/* Option 3: Microsoft Edge */}
                  <label
                    className={`relative flex flex-col p-3.5 rounded-xl border cursor-pointer transition-all ${
                      settings.automation.browser_engine === "msedge"
                        ? "bg-indigo-50/70 dark:bg-indigo-950/40 border-indigo-500 ring-1 ring-indigo-500"
                        : "bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="browser_engine"
                      value="msedge"
                      checked={settings.automation.browser_engine === "msedge"}
                      onChange={() => {
                        const engine = "msedge";
                        setSettings({
                          ...settings,
                          automation: {
                            ...settings.automation,
                            browser_engine: engine,
                            user_agent: ENGINE_USER_AGENTS[engine] || settings.automation.user_agent,
                          },
                        });
                      }}
                      className="sr-only"
                    />
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">Microsoft Edge</span>
                      <span className="text-[9px] font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                        Supported
                      </span>
                    </div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-tight">
                      System Microsoft Edge via Chromium channel. Full extension support with active service worker lifecycle.
                    </p>
                  </label>
                </div>
              </div>

              {/* Google Chrome Executable Binary Path */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Google Chrome Executable Location
                  </label>
                  <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold bg-emerald-50 dark:bg-emerald-950/50 px-2 py-0.5 rounded border border-emerald-200 dark:border-emerald-800">
                    Windows Default Auto-Detected
                  </span>
                </div>
                <input
                  type="text"
                  placeholder="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                  value={settings.automation.chrome_binary_path || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        chrome_binary_path: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Standard Windows path: <code className="text-slate-700 dark:text-slate-300 font-mono">C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe</code>. Used when Google Chrome engine is selected.
                </p>
              </div>

              {/* Chrome User Profile Directory (Optional) */}
              <div className="space-y-1.5">
                <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                  Chrome User Profile Directory (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. C:\\Users\\user\\AppData\\Local\\Google\\Chrome\\User Data"
                  value={settings.automation.chrome_user_data_dir || ""}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        chrome_user_data_dir: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500 font-mono"
                />
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Path to persistent user profile for cookie persistence or single sign-on.
                </p>
              </div>

              {/* User Agent */}
              <div className="sm:col-span-2 space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-slate-700 dark:text-slate-300 text-xs block">
                    Browser User-Agent String
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      const engine = settings.automation.browser_engine || "chromium";
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          user_agent: ENGINE_USER_AGENTS[engine] || ENGINE_USER_AGENTS.chromium,
                        },
                      });
                    }}
                    className="text-[10px] text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 font-medium cursor-pointer"
                  >
                    Reset to Default for Selected Engine
                  </button>
                </div>
                <input
                  type="text"
                  value={settings.automation.user_agent}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      automation: {
                        ...settings.automation,
                        user_agent: e.target.value,
                      },
                    })
                  }
                  className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 font-mono focus:outline-hidden focus:border-indigo-500"
                />
              </div>

              {/* Browser Execution Mode Interactive Card & Live Tester */}
              <div className="sm:col-span-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                      <Monitor className="w-4 h-4 text-indigo-500" />
                      Browser Execution Mode &amp; Runtime Environment
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">
                      Select how Google Chrome executes county court portal scrapers and automated CAPTCHA workflows.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                        !settings.automation.headless_mode
                          ? "bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20"
                          : "bg-sky-500/10 text-sky-600 dark:text-sky-400 border-sky-500/20"
                      }`}
                    >
                      Active: {!settings.automation.headless_mode ? "Attended (Visible GUI)" : "Headless (Background)"}
                    </span>
                  </div>
                </div>

                {/* Dual Mode Selector Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {/* Option 1: Attended Mode */}
                  <div
                    onClick={() =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          headless_mode: false,
                        },
                      })
                    }
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                      !settings.automation.headless_mode
                        ? "border-purple-600 bg-purple-50/50 dark:bg-purple-950/30 ring-2 ring-purple-600/20"
                        : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 mb-2">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                            !settings.automation.headless_mode
                              ? "bg-purple-600 text-white"
                              : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                          }`}
                        >
                          <Eye className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-slate-200 flex items-center gap-1.5">
                            Attended (Visible GUI)
                            {!settings.automation.headless_mode && (
                              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-purple-600 text-white">
                                Selected
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-purple-600 dark:text-purple-400 font-medium">
                            Real Desktop Window • Operator Visible
                          </span>
                        </div>
                      </div>
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          !settings.automation.headless_mode
                            ? "border-purple-600 bg-purple-600 text-white"
                            : "border-slate-300 dark:border-slate-700"
                        }`}
                      >
                        {!settings.automation.headless_mode && (
                          <div className="w-1.5 h-1.5 rounded-full bg-white" />
                        )}
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed mt-1">
                      Spawns real Chrome windows on your Windows desktop. You see tabs open, fields fill, and the AntiCaptcha extension solve challenges in real time.
                    </p>
                  </div>

                  {/* Option 2: Headless Mode */}
                  <div
                    onClick={() =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          headless_mode: true,
                        },
                      })
                    }
                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                      settings.automation.headless_mode
                        ? "border-sky-600 bg-sky-50/50 dark:bg-sky-950/30 ring-2 ring-sky-600/20"
                        : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2 mb-2">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                            settings.automation.headless_mode
                              ? "bg-sky-600 text-white"
                              : "bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400"
                          }`}
                        >
                          <EyeOff className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-slate-200 flex items-center gap-1.5">
                            Headless (Background)
                            {settings.automation.headless_mode && (
                              <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 rounded bg-sky-600 text-white">
                                Selected
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-sky-600 dark:text-sky-400 font-medium">
                            Silent Execution • Server Production Mode
                          </span>
                        </div>
                      </div>
                      <div
                        className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                          settings.automation.headless_mode
                            ? "border-sky-600 bg-sky-600 text-white"
                            : "border-slate-300 dark:border-slate-700"
                        }`}
                      >
                        {settings.automation.headless_mode && (
                          <div className="w-1.5 h-1.5 rounded-full bg-white" />
                        )}
                      </div>
                    </div>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed mt-1">
                      Runs Chrome silently without displaying a browser window. Consumes less RAM/CPU, optimal for Docker containers and server deployments.
                    </p>
                  </div>
                </div>

                {/* Live Browser Test Actions */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-200 dark:border-slate-800/80">
                  <div className="text-[11px] text-slate-500 dark:text-slate-400">
                    Test launch Chrome right now to verify display, AntiCaptcha extension, and browser profile:
                  </div>
                  <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap">
                    <button
                      type="button"
                      disabled={isTestingBrowser}
                      onClick={() => handleTestBrowser(false)}
                      className="px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50"
                    >
                      {isTestingBrowser ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Eye className="w-3.5 h-3.5" />}
                      Test Attended (Visible GUI)
                    </button>
                    <button
                      type="button"
                      disabled={isTestingBrowser}
                      onClick={() => handleTestBrowser(true)}
                      className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50"
                    >
                      {isTestingBrowser ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <EyeOff className="w-3.5 h-3.5" />}
                      Test Headless
                    </button>
                  </div>
                </div>

                {/* Browser Test Results Banner */}
                {browserTestResult && (
                  <div
                    className={`rounded-xl p-3.5 text-xs border space-y-2 transition-all ${
                      browserTestResult.success
                        ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                        : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2.5 min-w-0 pb-2 border-b border-black/5 dark:border-white/5">
                      <div className="flex items-center gap-2 font-bold min-w-0">
                        {browserTestResult.success ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
                        )}
                        <span className="truncate">
                          {browserTestResult.success
                            ? "Chrome Launch Test Passed Successfully"
                            : "Chrome Launch Test Failed"}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="font-mono text-[10px] opacity-70 bg-black/5 dark:bg-white/5 px-2 py-0.5 rounded">
                          {browserTestResult.duration_ms.toFixed(0)} ms
                        </span>
                        <button
                          type="button"
                          onClick={() => setBrowserTestResult(null)}
                          className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer p-0.5"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <p className="text-[11px] leading-relaxed">{browserTestResult.message}</p>

                    {browserTestResult.extension_path && (
                      <div className="text-[10px] font-mono opacity-80 bg-black/5 dark:bg-white/5 p-2 rounded-lg break-all">
                        Extension Path: {browserTestResult.extension_path}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}"""

# Replace old automation block with clean automation block
content = content[:idx_auto] + clean_auto_block + "\n\n        " + content[idx_proxy:]
print("[OK] Reconstructed clean 'automation' tab block")

# 4. Enhance 'extension' tab: Add CAPTCHA Loop Parameters & Pinning Card
ext_start_str = '{activeTab === "extension" && ('
email_start_str = '{activeTab === "email" && ('

idx_ext = content.find(ext_start_str)
idx_email = content.find(email_start_str)
assert idx_ext != -1 and idx_email != -1, "extension or email block not found!"

ext_block = content[idx_ext:idx_email]

# Let's inspect where to insert the CAPTCHA loop parameters and toolbar pinning card in extension tab
# The extension tab starts with Header Banner, then Plugin Configuration.
# We will insert Card 1 (CAPTCHA Auto-Click & Refresh Loop Parameters) directly after Header Banner!
header_banner_end = '</div>\n            </div>'
idx_hb = ext_block.find(header_banner_end)
assert idx_hb != -1, "header banner end not found in extension block!"

captcha_loop_card = """

            {/* CAPTCHA Auto-Click & Refresh Loop Parameters */}
            <div className="bg-white dark:bg-slate-900/40 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 space-y-5 shadow-xs">
              <div className="flex items-center gap-2 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <ShieldCheck className="w-5 h-5 text-amber-500" />
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-200">
                    CAPTCHA Challenge Detection &amp; Auto-Retry Parameters
                  </h4>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Control challenge detection timeouts, page refresh retries, and token wait durations across all court scrapers.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
                {/* Max CAPTCHA Attempts */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <label className="font-semibold text-slate-700 dark:text-slate-300">
                      Max Retry &amp; Refresh Attempts
                    </label>
                    <span className="font-mono text-xs font-bold text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800/60 px-2 py-0.5 rounded-md">
                      {settings.automation.max_captcha_attempts} Attempts
                    </span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="20"
                    step="1"
                    value={settings.automation.max_captcha_attempts}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          max_captcha_attempts: parseInt(e.target.value) || 1,
                        },
                      })
                    }
                    className="w-full accent-amber-500 cursor-pointer"
                  />
                  <p className="text-[10px] text-slate-500 dark:text-slate-400">
                    Attempts to click CAPTCHA checkbox, wait for token resolution, reload page on error, before gracefully skipping the portal.
                  </p>
                </div>

                {/* CAPTCHA Wait Duration */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <label className="font-semibold text-slate-700 dark:text-slate-300">
                      CAPTCHA Resolution Wait (Seconds)
                    </label>
                    <span className="font-mono text-xs font-bold text-slate-900 dark:text-slate-200">
                      {settings.automation.captcha_wait_seconds}s
                    </span>
                  </div>
                  <input
                    type="number"
                    min="3"
                    max="180"
                    value={settings.automation.captcha_wait_seconds}
                    onChange={(e) =>
                      setSettings({
                        ...settings,
                        automation: {
                          ...settings.automation,
                          captcha_wait_seconds: parseInt(e.target.value) || 5,
                        },
                      })
                    }
                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-900 dark:text-slate-200 focus:outline-hidden focus:border-indigo-500"
                  />
                  <p className="text-[10px] text-slate-500 dark:text-slate-400">
                    Maximum time to wait for the AntiCaptcha extension to solve reCAPTCHA or Turnstile before refreshing.
                  </p>
                </div>
              </div>
            </div>"""

pinning_card = """

            {/* One-Time Extension Toolbar Pinning & Persistent Profile Card */}
            <div className="bg-gradient-to-r from-slate-50 to-indigo-50/40 dark:from-slate-950/60 dark:to-indigo-950/20 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200 dark:border-slate-800/80">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2 text-xs font-bold text-slate-900 dark:text-slate-200">
                    <Pin className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                    One-Time Extension Toolbar Pinning &amp; Persistent Profile Setup
                  </div>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Configures Anti-Captcha once into persistent profile (<code>data/browser_profile/</code>) and pins it to the modern Chromium toolbar (<code>toolbar.pinned_actions</code>). Subsequent scraper runs reuse this profile without repeated overhead.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleSetupExtension}
                  disabled={isSettingUpExtension}
                  className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer disabled:opacity-50 shrink-0"
                >
                  {isSettingUpExtension ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Pin className="w-3.5 h-3.5" />
                  )}
                  Configure &amp; Pin Extension
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Toolbar Pinning Status</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                      settings.automation.extension_setup_verified
                        ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800"
                        : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200 dark:border-amber-800"
                    }`}>
                      {settings.automation.extension_setup_verified ? "Pinned & Verified" : "Pending Setup"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 dark:text-slate-300">
                    {settings.automation.extension_setup_verified
                      ? "Anti-Captcha is pinned to the Chromium browser toolbar and ready for instant automated CAPTCHA solving."
                      : "Click 'Configure & Pin Extension' to initialize toolbar action pinning in Preferences."}
                  </p>
                  {settings.automation.extension_setup_timestamp && (
                    <p className="text-[10px] text-slate-400 font-mono">
                      Last Configured: {settings.automation.extension_setup_timestamp}
                    </p>
                  )}
                </div>

                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 space-y-1.5">
                  <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">Persistent Profile Target</span>
                  <p className="text-[11px] font-mono text-slate-700 dark:text-slate-300">
                    backend/data/browser_profile/
                  </p>
                  <p className="text-[10px] text-slate-500 dark:text-slate-400">
                    Action ID: <code className="text-indigo-600 dark:text-indigo-400 font-mono">kActionExtensionId:gcpdbjbmekkdlkpldjgffhmapgpdlcpj</code>
                  </p>
                </div>
              </div>

              {extensionSetupResult && (
                <div className={`rounded-xl p-3 text-xs border space-y-1 ${
                  extensionSetupResult.verified
                    ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
                    : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
                }`}>
                  <div className="flex items-center gap-2 font-bold">
                    {extensionSetupResult.verified ? (
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    ) : (
                      <AlertCircle className="w-3.5 h-3.5" />
                    )}
                    {extensionSetupResult.message}
                  </div>
                  <div className="text-[10px] opacity-70 font-mono">
                    Target: {extensionSetupResult.persistent_profile_path} • Pinned: {String(extensionSetupResult.pinned_to_toolbar)}
                  </div>
                </div>
              )}
            </div>"""

# Insert captcha loop card after header banner in extension block
ext_block_new = ext_block[:idx_hb + len(header_banner_end)] + captcha_loop_card + ext_block[idx_hb + len(header_banner_end):]

# Insert pinning card before the last closing </div> of extension tab
last_div_idx = ext_block_new.rfind('</div>')
ext_block_new = ext_block_new[:last_div_idx] + pinning_card + "\n          " + ext_block_new[last_div_idx:]

content = content[:idx_ext] + ext_block_new + content[idx_email:]
print("[OK] Enhanced 'extension' tab with CAPTCHA Loop Parameters & Pinning Card")

# 5. Swap extension and proxy blocks so extension is Tab 4 and proxy is Tab 5
# Current order in content is: automation -> proxy -> extension -> email
# Let's locate proxy and extension blocks:
idx_proxy_start = content.find('{activeTab === "proxy" && (')
idx_ext_start = content.find('{activeTab === "extension" && (')
idx_email_start = content.find('{activeTab === "email" && (')

proxy_block = content[idx_proxy_start:idx_ext_start]
ext_block_current = content[idx_ext_start:idx_email_start]

# Swap: put ext_block_current first, then proxy_block
swapped = ext_block_current + proxy_block
content = content[:idx_proxy_start] + swapped + content[idx_email_start:]
print("[OK] Swapped extension and proxy tabs in component rendering")

with open(src_file, "w", encoding="utf-8") as f:
    f.write(content)

print("[ALL DONE] Saved updated page.tsx successfully!")
