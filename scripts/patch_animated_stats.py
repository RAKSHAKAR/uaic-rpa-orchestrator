import re

path = r"d:\scratch\Bot_UAIC\e2e\run_all_e2e_tests.ps1"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where the HTML template starts
start_idx = text.find('$htmlContent = @"')
end_idx = text.find('"@\n\nSet-Content -Path $htmlReportPath', start_idx)

if start_idx != -1 and end_idx != -1:
    old_html = text[start_idx:end_idx]
    
    # We want to add:
    # 1. Animated CSS styles (fadeIn, pulse, progress animation)
    # 2. Circular SVG donut chart in the header/stats section
    # 3. JavaScript count-up animation for stat values
    
    new_html = r'''$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UAIC RPA Orchestrator - E2E Test Execution Report</title>
    <style>
        :root {
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #243447;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #6366f1;
            --success: #10b981;
            --fail: #ef4444;
            --warn: #f59e0b;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 32px 24px;
            font-size: 14px;
            line-height: 1.5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            animation: slideDown 0.5s ease-out;
        }
        h1 { margin: 0 0 6px 0; font-size: 22px; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
        .meta { color: var(--text-muted); font-size: 12px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            animation: cardFadeIn 0.6s ease-out forwards;
            opacity: 0;
            transform: translateY(12px);
        }
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .stat-card:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.15);
        }
        .stat-label { 
            font-size: 11px; 
            text-transform: uppercase; 
            color: var(--text-muted); 
            font-weight: 700; 
            letter-spacing: 0.5px;
            margin-bottom: 8px; 
        }
        .stat-val { 
            font-size: 32px; 
            font-weight: 800; 
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            display: flex;
            align-items: baseline;
            gap: 4px;
        }
        .stat-val.pass { color: var(--success); }
        .stat-val.fail { color: var(--fail); }
        .stat-val.skip { color: var(--warn); }
        .stat-val.dur { color: #38bdf8; }
        
        .progress-bar-container {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            margin-top: 12px;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            border-radius: 9999px;
            width: 0%;
            transition: width 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .fill-pass { background: linear-gradient(90deg, #059669, #10b981); }
        .fill-fail { background: #ef4444; }
        .fill-skip { background: #f59e0b; }
        .fill-dur { background: linear-gradient(90deg, #0284c7, #38bdf8); }

        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            animation: cardFadeIn 0.7s ease-out 0.4s forwards;
            opacity: 0;
            transform: translateY(12px);
        }
        th, td {
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            background: #0b1120;
            font-size: 11px;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        tbody tr:hover { background: var(--surface-hover); }
        tbody tr:last-child td { border-bottom: none; }
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-success { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
        .badge-failure { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
        .badge-pass { background: #064e3b; color: #6ee7b7; padding: 4px 10px; border-radius: 6px; font-size: 11px; }
        .badge-fail { background: #7f1d1d; color: #fca5a5; padding: 4px 10px; border-radius: 6px; font-size: 11px; }
        .num-pass { color: var(--success); font-weight: 700; }
        .num-fail { color: var(--fail); font-weight: 700; }
        .num-skip { color: var(--warn); font-weight: 700; }
        
        .footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 36px;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-16px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes cardFadeIn {
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>UAIC RPA Orchestrator - E2E Execution Report</h1>
                <div class="meta">
                    Execution ID: <strong>IMP-2026-1031-002</strong> &bull;
                    Environment: <strong>$Environment</strong> &bull;
                    Mode: <strong>$effectiveMode</strong> &bull;
                    Timestamp: <strong>$($endTime.ToString('yyyy-MM-dd HH:mm:ss'))</strong>
                </div>
            </div>
            <div>
                <span class="badge $statusBadgeClass" style="font-size: 13px; padding: 8px 18px;">$statusBadgeText</span>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Passed Tests</div>
                <div class="stat-val pass" id="valPassed" data-target="$totalPassed">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-pass" id="barPassed" data-width="100%"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed Tests</div>
                <div class="stat-val fail" id="valFailed" data-target="$totalFailed">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-fail" id="barFailed" data-width="$(if ($totalFailed -gt 0) { '100%' } else { '0%' })"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Skipped Tests</div>
                <div class="stat-val skip" id="valSkipped" data-target="$totalSkipped">0</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-skip" id="barSkipped" data-width="$(if ($totalSkipped -gt 0) { '100%' } else { '0%' })"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Duration</div>
                <div class="stat-val dur" id="valDuration" data-target="$totalDuration" data-suffix="s">0s</div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill fill-dur" id="barDuration" data-width="100%"></div>
                </div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Test Suite</th>
                    <th>Target Scope</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                </tr>
            </thead>
            <tbody>
                $tableRows
            </tbody>
        </table>

        <div class="footer">
            UAIC RPA Orchestrator &bull; Production Court Discovery & Cloud Push &bull; Playwright + Celery + FastAPI + RapidFuzz
        </div>
    </div>

    <script>
        // Smooth animated statistic counters and loading bars
        window.addEventListener('DOMContentLoaded', () => {
            const counters = [
                { id: 'valPassed', bar: 'barPassed', target: $totalPassed, suffix: '' },
                { id: 'valFailed', bar: 'barFailed', target: $totalFailed, suffix: '' },
                { id: 'valSkipped', bar: 'barSkipped', target: $totalSkipped, suffix: '' },
                { id: 'valDuration', bar: 'barDuration', target: $totalDuration, suffix: 's', decimals: 2 }
            ];

            const duration = 1200;
            const startTime = performance.now();

            function animate(currentTime) {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOut = 1 - Math.pow(1 - progress, 3);

                counters.forEach(c => {
                    const el = document.getElementById(c.id);
                    if (!el) return;
                    const val = (c.target * easeOut);
                    el.textContent = (c.decimals ? val.toFixed(c.decimals) : Math.round(val)) + c.suffix;
                });

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    counters.forEach(c => {
                        const el = document.getElementById(c.id);
                        if (el) el.textContent = (c.decimals ? c.target.toFixed(c.decimals) : c.target) + c.suffix;
                    });
                }
            }

            requestAnimationFrame(animate);

            // Animate progress bars
            setTimeout(() => {
                document.querySelectorAll('.progress-bar-fill').forEach(bar => {
                    const targetWidth = bar.getAttribute('data-width');
                    if (targetWidth) bar.style.width = targetWidth;
                });
            }, 150);
        });
    </script>
</body>
</html>'''

    text = text[:start_idx] + new_html + text[end_idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("e2e/run_all_e2e_tests.ps1 updated with animated statistics engine successfully")
else:
    print("Could not find start/end markers in run_all_e2e_tests.ps1")

