from PIL import Image, ImageDraw, ImageFont


def draw_cursor(draw, x, y, clicked=False, action_label=""):
    arrow = [
        (x, y),
        (x, y + 20),
        (x + 5, y + 16),
        (x + 9, y + 24),
        (x + 13, y + 22),
        (x + 9, y + 14),
        (x + 15, y + 14),
    ]
    shadow = [(px + 1, py + 1) for px, py in arrow]
    draw.polygon(shadow, fill=(0, 0, 0))
    draw.polygon(arrow, fill=(255, 255, 255), outline=(15, 23, 42), width=1)

    if clicked:
        draw.ellipse([(x - 8, y - 8), (x + 8, y + 8)], outline=(245, 158, 11), width=2)
        draw.ellipse([(x - 14, y - 14), (x + 14, y + 14)], outline=(56, 189, 248), width=1)

    if action_label:
        try:
            lbl_font = ImageFont.truetype("arialbd.ttf", 11)
        except Exception:
            lbl_font = ImageFont.load_default()
        bbox = draw.textbbox((x + 18, y + 10), action_label, font=lbl_font)
        pad_box = [(bbox[0] - 4, bbox[1] - 2), (bbox[2] + 4, bbox[3] + 2)]
        draw.rectangle(pad_box, fill=(15, 23, 42), outline=(56, 189, 248), width=1)
        draw.text((x + 18, y + 10), action_label, fill=(241, 245, 249), font=lbl_font)

def stamp_executive_frame_padded(
    base_img: Image.Image,
    portal_name: str,
    party_info: str,
    step_num: int,
    total_steps: int,
    step_title: str,
    url: str,
    status_text: str,
    cursor_pos: tuple[int, int] | None = None,
    cursor_clicked: bool = False,
    cursor_label: str = "",
    schema_text: str = "5 fields (CaseNumber, CaseStyle, FilingDate, CaseStatus, CaseType)",
) -> Image.Image:
    base_w, base_h = base_img.size
    top_bar_height = 54
    bot_bar_height = 36
    total_h = base_h + top_bar_height + bot_bar_height

    # Create composite canvas
    img = Image.new("RGB", (base_w, total_h), color=(15, 23, 42))
    # Paste untouched browser screenshot between top and bottom banners
    img.paste(base_img.convert("RGB"), (0, top_bar_height))

    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arial.ttf", 19)
        font_small = ImageFont.truetype("arial.ttf", 12)
        font_bold = ImageFont.truetype("arialbd.ttf", 13)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # Draw Top Header
    draw.line([(0, top_bar_height), (base_w, top_bar_height)], fill=(56, 189, 248), width=2)
    draw.text((16, 6), f"PORTAL: {portal_name.upper()} | PARTY: {party_info.upper()}", fill=(245, 158, 11), font=font_large)
    trunc_url = url if len(url) < 95 else url[:92] + "..."
    draw.text((16, 30), f"Step {step_num}/{total_steps}: {step_title} | URL: {trunc_url}", fill=(226, 232, 240), font=font_small)

    tag_text = "● LIVE ATTENDED AUTOMATION (GOOGLE CHROME)"
    draw.text((base_w - 390, 18), tag_text, fill=(34, 197, 94), font=font_bold)

    # Draw Bottom Header
    draw.line([(0, total_h - bot_bar_height), (base_w, total_h - bot_bar_height)], fill=(71, 85, 105), width=1)
    draw.text(
        (16, total_h - bot_bar_height + 9),
        f"UAIC Orchestrator (IMP-2026-1030-003) | Schema: {schema_text} | Claim: 800221153",
        fill=(148, 163, 184),
        font=font_small,
    )
    draw.text((base_w - 340, total_h - bot_bar_height + 9), f"Pipeline: {status_text}", fill=(56, 189, 248), font=font_bold)

    # Draw cursor offset by top_bar_height
    if cursor_pos:
        cx, cy = cursor_pos
        draw_cursor(draw, cx, cy + top_bar_height, clicked=cursor_clicked, action_label=cursor_label)

    return img

# Test with test_f1_dev_off.png and test_f2_dev_on.png
f1 = Image.open("docs/test_f1_dev_off.png")
res1 = stamp_executive_frame_padded(
    f1,
    "BROWARD COUNTY CLERK OF COURTS (FL)",
    "SYSTEM SETUP",
    1,
    5,
    "Google Chrome Launched — Moving Mouse Pointer to 'Developer mode' Toggle Switch",
    "chrome://extensions",
    "DEV MODE (OFF)",
    cursor_pos=(1248, 35),
    cursor_clicked=False,
    cursor_label="Hover Developer Mode",
)
res1.save("docs/padded_test_f1.png")
print("Saved docs/padded_test_f1.png")

f2 = Image.open("docs/test_f2_dev_on.png")
res2 = stamp_executive_frame_padded(
    f2,
    "BROWARD COUNTY CLERK OF COURTS (FL)",
    "SYSTEM SETUP",
    2,
    5,
    "Developer Mode Toggled ON (Blue Switch) — 'Load unpacked' Action Toolbar Visible",
    "chrome://extensions",
    "DEV MODE (ON)",
    cursor_pos=(1248, 35),
    cursor_clicked=True,
    cursor_label="Click: Dev Mode ON",
)
res2.save("docs/padded_test_f2.png")
print("Saved docs/padded_test_f2.png")

f3 = Image.open("docs/test_f3_ext_card.png")
res3 = stamp_executive_frame_padded(
    f3,
    "BROWARD COUNTY CLERK OF COURTS (FL)",
    "SYSTEM SETUP",
    4,
    5,
    "AntiCaptcha Extension Active (v0.83, ID: fignfifoniblkonapihmkfakmlgkbkcf) — Opening Options",
    "chrome://extensions",
    "EXTENSION MOUNTED",
    cursor_pos=(445, 282),
    cursor_clicked=True,
    cursor_label="Click: Configuration Options",
)
res3.save("docs/padded_test_f3.png")
print("Saved docs/padded_test_f3.png")

f4 = Image.open("docs/test_f4_ext_options.png")
res4 = stamp_executive_frame_padded(
    f4,
    "BROWARD COUNTY CLERK OF COURTS (FL)",
    "SYSTEM SETUP",
    5,
    5,
    "Anti-Captcha Configuration Verified — API Key & Automated Solvers Operational",
    "chrome://extensions",
    "CONFIG CONFIRMED",
    cursor_pos=(730, 528),
    cursor_clicked=True,
    cursor_label="✓ Save & Return",
)
res4.save("docs/padded_test_f4.png")
print("Saved docs/padded_test_f4.png")

