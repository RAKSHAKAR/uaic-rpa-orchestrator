"""Script to apply Attended GUI display logging in browser_manager.py."""
from pathlib import Path

target = Path(__file__).resolve().parent.parent / "backend" / "app" / "automation" / "browser_manager.py"
text = target.read_text(encoding="utf-8")

old_snippet = (
    '        if sys.platform != "win32" and "DISPLAY" not in os.environ:\n'
    '            if not is_headless:\n'
    '                logger.info("Attended GUI requested but running in container without DISPLAY. Executing headlessly.")\n'
    '            is_headless = True\n'
    '            launch_args.extend(["--disable-gpu", "--disable-dev-shm-usage"])'
)

new_snippet = (
    '        if sys.platform != "win32":\n'
    '            if "DISPLAY" not in os.environ:\n'
    '                if not is_headless:\n'
    '                    logger.info("Attended GUI requested but running in container without DISPLAY. Executing headlessly.")\n'
    '                is_headless = True\n'
    '                launch_args.extend(["--disable-gpu", "--disable-dev-shm-usage"])\n'
    '            elif not is_headless:\n'
    '                logger.info(f"Attended GUI active on display {os.environ.get(\'DISPLAY\')}. Operator viewing available via noVNC (http://localhost:6080/vnc.html).")'
)

if old_snippet in text:
    updated = text.replace(old_snippet, new_snippet)
    target.write_text(updated, encoding="utf-8", newline="")
    print("browser_manager.py successfully updated with LF/CRLF match.")
else:
    # Try with CRLF
    old_crlf = old_snippet.replace("\n", "\r\n")
    new_crlf = new_snippet.replace("\n", "\r\n")
    if old_crlf in text:
        updated = text.replace(old_crlf, new_crlf)
        target.write_text(updated, encoding="utf-8", newline="")
        print("browser_manager.py successfully updated with CRLF match.")
    else:
        print("Target snippet not found in browser_manager.py")

