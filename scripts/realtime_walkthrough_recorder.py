"""Real-time parallel action recorder for live manual walkthrough.

Connects to the active Chrome session via CDP (port 9222) and automatically
monitors, intercepts, and records all user interactions across all tabs:
- Clicks (button, link, div, checkbox, tile)
- Form inputs (typing, selecting, date picking)
- Page navigations & frame updates
- CAPTCHA encounters and resolutions
- Results tables, column headers, row extraction
- Pagination controls & page transitions
- Automatic screenshots saved to implementation_plan/Images/
- Structured log saved to implementation_plan/manual_walkthrough_recorded_steps.md
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from playwright.async_api import async_playwright, BrowserContext, Frame, Page

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("walkthrough_recorder")

repo_root = Path(__file__).resolve().parent.parent
images_dir = repo_root / "implementation_plan" / "Images"
images_dir.mkdir(parents=True, exist_ok=True)
md_log_file = repo_root / "implementation_plan" / "manual_walkthrough_recorded_steps.md"
jsonl_log_file = repo_root / "implementation_plan" / "manual_walkthrough_recorded_steps.jsonl"

step_counter = 0
hooked_pages = set()

# Initialize MD file header
if not md_log_file.exists() or md_log_file.stat().st_size == 0:
    md_log_file.write_text(
        "# Manual Portal Walkthrough — Live Recorded Action Sequence\n\n"
        f"> **Recording Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "> **Mode:** Attended GUI Manual Demonstration\n"
        "> **Objective:** Capture exact human navigation, selectors, tables, pagination, and columns across county portals.\n\n"
        "---\n\n"
        "| Step | Timestamp | Tab / Portal | Action | Element / Selector | Value / Details | Screenshot |\n"
        "|:---:|:---:|:---|:---:|:---|:---|:---:|\n",
        encoding="utf-8"
    )

INJECTED_RECORDER_JS = """
(() => {
    if (window.__uaic_recorder_attached) return;
    window.__uaic_recorder_attached = true;

    function getCssSelector(el) {
        if (!el || el.nodeType !== 1) return '';
        if (el.id) return '#' + el.id;
        if (el.name) return el.tagName.toLowerCase() + '[name="' + el.name + '"]';
        
        let path = [];
        let cur = el;
        while (cur && cur.nodeType === 1) {
            let tag = cur.tagName.toLowerCase();
            if (cur.id) {
                path.unshift('#' + cur.id);
                break;
            }
            let sib = cur;
            let nth = 1;
            while (sib = sib.previousElementSibling) {
                if (sib.tagName.toLowerCase() === tag) nth++;
            }
            path.unshift(tag + ':nth-of-type(' + nth + ')');
            cur = cur.parentNode;
            if (path.length > 5) break;
        }
        return path.join(' > ');
    }

    function getXPath(el) {
        if (!el || el.nodeType !== 1) return '';
        if (el.id) return '//*[@id="' + el.id + '"]';
        let parts = [];
        for (; el && el.nodeType === 1; el = el.parentNode) {
            let idx = 1;
            for (let sib = el.previousSibling; sib; sib = sib.previousSibling) {
                if (sib.nodeType === 1 && sib.tagName === el.tagName) idx++;
            }
            parts.unshift(el.tagName.toLowerCase() + '[' + idx + ']');
            if (parts.length > 5) break;
        }
        return '/' + parts.join('/');
    }

    // Capture Clicks
    document.addEventListener('click', (e) => {
        try {
            const el = e.target;
            if (!el) return;
            const text = (el.innerText || el.value || el.ariaLabel || el.title || el.alt || '').trim().slice(0, 80);
            const data = {
                type: 'click',
                tag: el.tagName.toLowerCase(),
                id: el.id || '',
                name: el.name || '',
                className: el.className || '',
                role: el.getAttribute('role') || '',
                typeAttr: el.getAttribute('type') || '',
                text: text,
                css: getCssSelector(el),
                xpath: getXPath(el),
                url: window.location.href,
                title: document.title
            };
            if (window.__pyRecordAction) {
                window.__pyRecordAction(data);
            }
        } catch (err) {}
    }, true);

    // Capture Inputs & Changes
    let inputTimeout = null;
    document.addEventListener('input', (e) => {
        try {
            const el = e.target;
            if (!el || !('value' in el)) return;
            clearTimeout(inputTimeout);
            inputTimeout = setTimeout(() => {
                const data = {
                    type: 'input',
                    tag: el.tagName.toLowerCase(),
                    id: el.id || '',
                    name: el.name || '',
                    typeAttr: el.type || '',
                    value: el.value || '',
                    placeholder: el.placeholder || '',
                    css: getCssSelector(el),
                    xpath: getXPath(el),
                    url: window.location.href,
                    title: document.title
                };
                if (window.__pyRecordAction) {
                    window.__pyRecordAction(data);
                }
            }, 500);
        } catch (err) {}
    }, true);

    document.addEventListener('change', (e) => {
        try {
            const el = e.target;
            if (!el) return;
            let val = el.value || '';
            if (el.type === 'checkbox' || el.type === 'radio') {
                val = el.checked ? 'CHECKED' : 'UNCHECKED';
            }
            const data = {
                type: 'change',
                tag: el.tagName.toLowerCase(),
                id: el.id || '',
                name: el.name || '',
                typeAttr: el.type || '',
                value: val,
                css: getCssSelector(el),
                xpath: getXPath(el),
                url: window.location.href,
                title: document.title
            };
            if (window.__pyRecordAction) {
                window.__pyRecordAction(data);
            }
        } catch (err) {}
    }, true);

    console.log('[UAIC RECORDER] Injected and listening for user actions.');
})();
"""


def log_step(action_type: str, portal: str, element_desc: str, details: str, screenshot_rel: str = ""):
    global step_counter
    step_counter += 1
    ts = datetime.now().strftime("%H:%M:%S")

    # Console output
    print(f"\n[STEP {step_counter:03d} | {ts}] {portal.upper()} >> {action_type.upper()}")
    print(f"   Target:  {element_desc}")
    print(f"   Details: {details}")
    if screenshot_rel:
        print(f"   Visual:  {screenshot_rel}")
    sys.stdout.flush()

    # Markdown table row
    img_link = f"[Screenshot]({screenshot_rel})" if screenshot_rel else "—"
    row = f"| **{step_counter}** | `{ts}` | {portal} | `{action_type}` | `{element_desc}` | {details} | {img_link} |\n"
    with open(md_log_file, "a", encoding="utf-8") as f:
        f.write(row)

    # JSONL log
    record = {
        "step": step_counter,
        "timestamp": ts,
        "portal": portal,
        "action": action_type,
        "element": element_desc,
        "details": details,
        "screenshot": screenshot_rel
    }
    with open(jsonl_log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def get_portal_name(url: str) -> str:
    u = url.lower()
    if "broward" in u:
        return "Broward County"
    elif "hillsclerk" in u or "hover" in u:
        return "Hillsborough County (HOVER)"
    elif "miamidade" in u:
        return "Miami-Dade County (OCS)"
    elif "travis" in u:
        return "Travis County"
    elif "dallas" in u:
        return "Dallas County"
    elif "harris" in u:
        return "Harris County"
    return "Portal"


async def setup_page_hooks(page: Page, tab_num: int):
    if page in hooked_pages:
        return
    hooked_pages.add(page)

    logger.info(f"Setting up action recorder on Tab {tab_num}: {page.url}")

    async def _handle_browser_action(event: dict):
        action_type = event.get("type", "action")
        portal = get_portal_name(event.get("url", page.url))
        tag = event.get("tag", "")
        eid = event.get("id", "")
        name = event.get("name", "")
        text = event.get("text", "")
        css = event.get("css", "")
        val = event.get("value", "")

        elem_ident = f"#{eid}" if eid else (f"[name='{name}']" if name else f"<{tag}> {css}")
        if text:
            elem_ident += f' ("{text}")'

        details = ""
        if action_type in ("input", "change"):
            details = f"Entered/Selected value: `{val}`"
        elif action_type == "click":
            details = f"Clicked `{tag}` element with selector `{css}`"
        else:
            details = f"Action `{action_type}` on `{elem_ident}`"

        # Capture screenshot for major clicks
        screenshot_rel = ""
        if action_type == "click":
            try:
                ss_filename = f"step_{step_counter+1:03d}_{action_type}_{re.sub(r'[^a-zA-Z0-9]', '_', text or eid or tag)[:20]}.png"
                ss_path = images_dir / ss_filename
                await page.screenshot(path=str(ss_path), full_page=False)
                screenshot_rel = f"Images/{ss_filename}"
            except Exception:
                pass

        log_step(action_type, portal, elem_ident, details, screenshot_rel)

        # Check for results table on click
        asyncio.create_task(inspect_results_and_pagination(page, portal))

    # Expose binding
    try:
        await page.expose_function("__pyRecordAction", _handle_browser_action)
    except Exception:
        pass

    # Inject on navigation
    try:
        await page.evaluate(INJECTED_RECORDER_JS)
    except Exception:
        pass

    async def _on_nav(frame: Frame):
        if frame == page.main_frame:
            portal = get_portal_name(frame.url)
            log_step("navigation", portal, f"URL: {frame.url}", f"Page transitioned to: `{frame.url}`")
            try:
                await page.evaluate(INJECTED_RECORDER_JS)
            except Exception:
                pass
            asyncio.create_task(inspect_results_and_pagination(page, portal))

    page.on("framenavigated", _on_nav)


async def inspect_results_and_pagination(page: Page, portal: str):
    """Checks if search results table or pagination controls appeared."""
    await asyncio.sleep(1.0)
    try:
        tables_data = await page.evaluate("""() => {
            const tables = Array.from(document.querySelectorAll('table')).map(t => {
                const headers = Array.from(t.querySelectorAll('th')).map(th => th.innerText.trim()).filter(Boolean);
                const rows = t.querySelectorAll('tr').length;
                return {
                    id: t.id,
                    className: t.className,
                    headers: headers,
                    rowCount: rows
                };
            }).filter(t => t.rowCount > 1 && t.headers.length >= 2);

            const pagination = Array.from(document.querySelectorAll('.pagination, [class*="paginate"], [class*="page"], nav[aria-label*="page" i], [id*="page" i], .rgPager')).map(p => ({
                id: p.id,
                className: p.className,
                text: (p.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 120)
            }));

            return { tables: tables, pagination: pagination };
        }""")

        if tables_data.get("tables"):
            for t in tables_data["tables"]:
                hdrs = ", ".join([f"`{h}`" for h in t["headers"][:8]])
                log_step("results_table", portal, f"Table #{t['id'] or t['className']}", f"Found table with {t['rowCount']} rows. Headers: {hdrs}")

        if tables_data.get("pagination"):
            for p in tables_data["pagination"]:
                if p["text"]:
                    log_step("pagination", portal, f"Pager #{p['id'] or p['className']}", f"Controls detected: `{p['text']}`")
    except Exception:
        pass


async def main():
    print("=================================================================")
    print("  PARALLEL REAL-TIME WALKTHROUGH RECORDER RUNNING")
    print("=================================================================")
    print("Connecting to live Chrome on port 9222...")
    sys.stdout.flush()

    pw = await async_playwright().start()
    browser = await pw.chromium.connect_over_cdp("http://localhost:9222")
    context = browser.contexts[0]

    # Hook existing pages
    for idx, page in enumerate(context.pages):
        await setup_page_hooks(page, idx + 1)

    # Hook any newly opened pages/popups
    def _on_new_page(new_page: Page):
        asyncio.create_task(setup_page_hooks(new_page, len(context.pages)))

    context.on("page", _on_new_page)

    print("\n[ACTIVE] Parallel recorder is live! Listening across all open tabs.")
    print("Perform your manual workflow directly in Chrome. Every action will be recorded.")
    print(f"Log Output: {md_log_file}")
    print("=================================================================\n")
    sys.stdout.flush()

    # Keep running
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
