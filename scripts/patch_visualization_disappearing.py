import re
from pathlib import Path

claims_page = Path("frontend/src/app/claims/[id]/page.tsx")
content = claims_page.read_text(encoding="utf-8")

# 1. Update fetchClaim signature and loading logic
old_fetch = """  const fetchClaim = useCallback(async () => {
    setIsLoading(true);
    setNotFound(false);"""

new_fetch = """  const fetchClaim = useCallback(async (isSilent = false) => {
    if (!isSilent) {
      setIsLoading(true);
    }
    setNotFound(false);"""

assert old_fetch in content, "old_fetch not found"
content = content.replace(old_fetch, new_fetch, 1)

# 2. Update polling interval to call fetchClaim(true)
old_poll = """    const timer = setInterval(() => {
      fetchClaim();
      fetchScreenshots();
      fetchClaimAuditLogs();
    }, 3000);"""

new_poll = """    const timer = setInterval(() => {
      fetchClaim(true);
      fetchScreenshots();
      fetchClaimAuditLogs();
    }, 3000);"""

assert old_poll in content, "old_poll not found"
content = content.replace(old_poll, new_poll, 1)

# 3. Update loading gate to only block on initial load when claim is absent
old_gate = """  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col w-full">
        <Navbar />
        <div className="p-12 text-center text-slate-500 dark:text-slate-400 text-xs flex flex-col items-center justify-center gap-3 my-auto">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" />
          <span>Loading claim 360 & RPA telemetry...</span>
        </div>
      </div>
    );
  }"""

new_gate = """  if (isLoading && !claim) {
    return (
      <div className="flex-1 flex flex-col w-full">
        <Navbar />
        <div className="p-12 text-center text-slate-500 dark:text-slate-400 text-xs flex flex-col items-center justify-center gap-3 my-auto">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" />
          <span>Loading claim 360 & RPA telemetry...</span>
        </div>
      </div>
    );
  }"""

assert old_gate in content, "old_gate not found"
content = content.replace(old_gate, new_gate, 1)

# 4. Make Waterfall Latency Distribution Bar permanently visible with standby state
old_waterfall_start = "          {/* Horizontal Waterfall Latency Distribution Bar */}\n          {waterfallData.length > 0 && ("
old_waterfall_end = "          {/* Mock/Seed Mode Notice — shown when browser automation stages are absent */}"

start_idx = content.find(old_waterfall_start)
end_idx = content.find(old_waterfall_end)
assert start_idx != -1 and end_idx != -1, "Waterfall block markers not found"

new_waterfall = """          {/* Horizontal Waterfall Latency Distribution Bar (Permanent Resilient Visualization) */}
          <div className="space-y-2 bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-800 dark:text-slate-300 flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-amber-500 dark:text-amber-400" />
                Stage Latency Waterfall Distribution
              </span>
              <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                {waterfallData.length > 0 ? (
                  <>
                    Longest Phase:{" "}
                    <strong className="text-amber-600 dark:text-amber-400">
                      {waterfallData.reduce((max, cur) => (cur.duration > max.duration ? cur : max), waterfallData[0])?.name} (
                      {waterfallData.reduce((max, cur) => (cur.duration > max.duration ? cur : max), waterfallData[0])?.duration}s)
                    </strong>
                  </>
                ) : (
                  <span className="text-slate-400">Standby / Awaiting stage execution</span>
                )}
              </span>
            </div>

            {/* Multi-segment Progress Bar */}
            <div className="h-3 w-full bg-slate-200 dark:bg-slate-900 rounded-full overflow-hidden flex gap-0.5 p-0.5 border border-slate-300 dark:border-slate-800">
              {waterfallData.length > 0 ? (
                waterfallData.map((item) => (
                  <div
                    key={item.key}
                    style={{ width: `${Math.max(item.percentage, 2)}%` }}
                    className={`${item.color} h-full rounded-xs transition-all hover:brightness-125 cursor-pointer relative group`}
                    title={`${item.name}: ${item.duration}s (${item.percentage.toFixed(1)}%)`}
                  />
                ))
              ) : (
                <div className="w-full h-full bg-slate-100 dark:bg-slate-800/60 rounded flex items-center justify-center text-[9px] font-mono text-slate-400">
                  Standby — Telemetry stages will populate during automation run
                </div>
              )}
            </div>

            {/* Waterfall Legend */}
            <div className="flex items-center gap-3 flex-wrap pt-1 text-[11px] font-mono">
              {waterfallData.length > 0 ? (
                waterfallData.map((item) => (
                  <div
                    key={item.key}
                    onClick={() => item.stage && setInspectedStage({ key: item.key, data: item.stage })}
                    className="flex items-center gap-1.5 cursor-pointer hover:underline text-slate-700 dark:text-slate-300"
                  >
                    <span className={`w-2 h-2 rounded-full ${item.color}`} />
                    <span>{item.label}:</span>
                    <strong className="text-slate-900 dark:text-slate-100">{formatDurationHms(item.duration)}</strong>
                    <span className="text-slate-500">({item.percentage.toFixed(0)}%)</span>
                  </div>
                ))
              ) : (
                <span className="text-slate-400 text-[10px]">
                  9 operational stages tracked: Launch, Navigation, Data Entry, CAPTCHA, Submit, Retrieval, DB Save, RapidFuzz, Guidewire
                </span>
              )}
            </div>
          </div>
"""

content = content[:start_idx] + new_waterfall + content[end_idx:]

claims_page.write_text(content, encoding="utf-8")
print("Successfully patched frontend/src/app/claims/[id]/page.tsx")

