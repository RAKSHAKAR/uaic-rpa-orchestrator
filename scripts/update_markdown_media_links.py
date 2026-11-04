"""
Update media links in markdown files following directory restructuring.
- docs/*.png -> docs/images/*.png or images/*.png
- docs/recordings/frames/* -> docs/frames/* or frames/*
- docs/*.webp -> docs/recordings/*.webp or recordings/*.webp
"""
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"

# Collect all filenames in images, frames, recordings
images = {p.name for p in (DOCS_DIR / "images").glob("*.png")}
recordings = {p.name for p in (DOCS_DIR / "recordings").glob("*.webp")}

md_files = list(DOCS_DIR.glob("**/*.md")) + [ROOT_DIR / "README.md", ROOT_DIR / "AGENTS.md"]

updated_count = 0

for md_path in md_files:
    if not md_path.is_file():
        continue
    content = md_path.read_text(encoding="utf-8")
    original = content

    # Replace misplaced recordings/frames/ with frames/
    content = content.replace("docs/recordings/frames/", "docs/frames/")
    content = content.replace("recordings/frames/", "frames/")

    # For each image, fix relative or root paths
    # Replace (filename.png) or (/filename.png) or (docs/filename.png) with images/filename.png
    for img in images:
        content = re.sub(rf'\((?:docs/|/docs/|/)?{re.escape(img)}\)', f'(images/{img})', content)
        content = re.sub(rf'src=["\'](?:docs/|/docs/|/)?{re.escape(img)}["\']', f'src="images/{img}"', content)

    # For each recording, ensure it references recordings/
    for rec in recordings:
        content = re.sub(rf'\((?:docs/|/docs/|/)?{re.escape(rec)}\)', f'(recordings/{rec})', content)
        content = re.sub(rf'src=["\'](?:docs/|/docs/|/)?{re.escape(rec)}["\']', f'src="recordings/{rec}"', content)

    if content != original:
        md_path.write_text(content, encoding="utf-8")
        updated_count += 1
        print(f"Updated media links in: {md_path.relative_to(ROOT_DIR)}")

print(f"Total markdown files updated: {updated_count}")

