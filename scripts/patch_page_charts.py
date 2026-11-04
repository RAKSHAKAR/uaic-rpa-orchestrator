from pathlib import Path

page = Path("frontend/src/app/page.tsx")
content = page.read_text(encoding="utf-8")

# In 5-segment progress bar, handle empty state cleanly:
old_prog = """                  {/* 5-Segment Progress Bar */}
                  <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 flex overflow-hidden p-0.5 gap-0.5">
                    {slices.map((slice) => (
                      slice.count > 0 ? (
                        <div
                          key={slice.key}
                          style={{ width: `${Math.max(2, slice.pct)}%` }}
                          className={`h-full ${slice.barColor} rounded-full transition-all duration-500`}
                          title={`${slice.label}: ${slice.pct}% (${slice.count})`}
                        />
                      ) : null
                    ))}
                  </div>"""

new_prog = """                  {/* 5-Segment Progress Bar (Resilient Non-Empty Rendering) */}
                  <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 flex overflow-hidden p-0.5 gap-0.5">
                    {slices.some((s) => s.count > 0) ? (
                      slices.map((slice) => (
                        slice.count > 0 ? (
                          <div
                            key={slice.key}
                            style={{ width: `${Math.max(2, slice.pct)}%` }}
                            className={`h-full ${slice.barColor} rounded-full transition-all duration-500`}
                            title={`${slice.label}: ${slice.pct}% (${slice.count})`}
                          />
                        ) : null
                      ))
                    ) : (
                      <div className="w-full h-full bg-slate-200/50 dark:bg-slate-700/50 rounded-full" title="No claims ingested" />
                    )}
                  </div>"""

assert old_prog in content, "old_prog not found"
content = content.replace(old_prog, new_prog, 1)

page.write_text(content, encoding="utf-8")
print("Successfully patched frontend/src/app/page.tsx")

