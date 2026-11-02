import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

out_dir = r"D:\4A\00_当前工作区_202611\voc_infographics"
os.makedirs(out_dir, exist_ok=True)

def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def draw_rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

# ==============================================================================
# 1. FULL ADHESIVE: HOW TO PEEL FLAT (NO CURLING / NO TEARING) - 2000x2000
# ==============================================================================
canvas1 = Image.new("RGB", (2000, 2000), (248, 250, 252))
draw1 = ImageDraw.Draw(canvas1)

# Top Header Banner
draw_rounded_rect(draw1, (40, 40, 1960, 250), 28, fill=(15, 23, 42))
draw1.text((1000, 110), "HOW TO PEEL FLAT WITHOUT CURLING", font=get_font(68, True), fill=(255, 255, 255), anchor="mm")
draw1.text((1000, 195), "90% Full Adhesive Back + 10% Bottom Non-Stick Grip Edge", font=get_font(40, False), fill=(253, 224, 71), anchor="mm")

# Left Card: Product Anatomy (702877118504.pt01.jpg + 305-FULL-GLUE-8.jpg)
draw_rounded_rect(draw1, (40, 290, 980, 1460), 28, fill=(255, 255, 255), outline=(203, 213, 225), width=4)
draw_rounded_rect(draw1, (40, 290, 980, 390), 28, fill=(30, 64, 175))
draw1.text((510, 340), "1. FIND THE NON-STICK GRIP EDGE", font=get_font(40, True), fill=(255, 255, 255), anchor="mm")

img_pt01 = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\6-----4A Full Adhesive Notes\302-FULL GLUE\702877118504.pt01.jpg").convert("RGB")
img_pt01.thumbnail((860, 580), Image.Resampling.LANCZOS)
canvas1.paste(img_pt01, (510 - img_pt01.width // 2, 420))

img_strip = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\6-----4A Full Adhesive Notes\305-FULL GLUE\305-FULL-GLUE-8.jpg").convert("RGB")
img_strip.thumbnail((880, 240), Image.Resampling.LANCZOS)
canvas1.paste(img_strip, (510 - img_strip.width // 2, 1030))

# Callout box inside Left Card
draw_rounded_rect(draw1, (70, 1260, 950, 1430), 18, fill=(239, 246, 255), outline=(59, 130, 246), width=3)
draw1.text((510, 1310), "NOTE: Dashed Line is on Top Cover Sheet Only!", font=get_font(34, True), fill=(30, 58, 138), anchor="mm")
draw1.text((510, 1365), "All inner sheets are 100% blank & unperforated.", font=get_font(30, False), fill=(30, 64, 175), anchor="mm")
draw1.text((510, 1405), "The bottom strip below the line is glue-free for easy gripping.", font=get_font(27, False), fill=(51, 65, 85), anchor="mm")

# Right Card: Side-to-Side Peel Action (702877118559.pt06.jpg)
draw_rounded_rect(draw1, (1020, 290, 1960, 1460), 28, fill=(255, 255, 255), outline=(22, 163, 74), width=5)
draw_rounded_rect(draw1, (1020, 290, 1960, 390), 28, fill=(22, 163, 74))
draw1.text((1490, 340), "2. PEEL SIDE-TO-SIDE (HORIZONTALLY)", font=get_font(38, True), fill=(255, 255, 255), anchor="mm")

img_pt06 = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\6-----4A Full Adhesive Notes\305-FULL GLUE\702877118559.pt06.jpg").convert("RGB")
img_pt06.thumbnail((840, 760), Image.Resampling.LANCZOS)
canvas1.paste(img_pt06, (1490 - img_pt06.width // 2, 420))

# Draw horizontal arrow overlay on img_pt06 showing peel direction
arrow_y = 960
draw_rounded_rect(draw1, (1120, arrow_y - 38, 1860, arrow_y + 38), 38, fill=(22, 163, 74))
draw1.text((1490, arrow_y), "PEEL HORIZONTALLY ALONG EDGE  --->", font=get_font(34, True), fill=(255, 255, 255), anchor="mm")

# Green DO vs Red DON'T inside Right Card
draw_rounded_rect(draw1, (1050, 1210, 1930, 1320), 16, fill=(240, 253, 244), outline=(22, 163, 74), width=3)
draw1.text((1490, 1250), "CORRECT: Peel Side-to-Side from Non-Stick Corner", font=get_font(32, True), fill=(21, 128, 61), anchor="mm")
draw1.text((1490, 1292), "Sheet stays 100% flat & adheres flush to walls, monitors & paper.", font=get_font(27, False), fill=(22, 101, 52), anchor="mm")

draw_rounded_rect(draw1, (1050, 1335, 1930, 1440), 16, fill=(254, 242, 242), outline=(220, 38, 38), width=3)
draw1.text((1490, 1372), "AVOID: Do Not Yank Straight Up from Bottom", font=get_font(32, True), fill=(185, 28, 28), anchor="mm")
draw1.text((1490, 1412), "Pulling vertically against full-back adhesive causes paper to curl.", font=get_font(27, False), fill=(153, 27, 27), anchor="mm")

# Bottom Banner: Best Surfaces Guide
draw_rounded_rect(draw1, (40, 1500, 1960, 1960), 28, fill=(255, 255, 255), outline=(203, 213, 225), width=4)
draw_rounded_rect(draw1, (40, 1500, 1960, 1595), 28, fill=(15, 23, 42))
draw1.text((1000, 1548), "3. APPLY TO CLEAN, DRY, SMOOTH SURFACES FOR MAXIMUM HOLD", font=get_font(40, True), fill=(255, 255, 255), anchor="mm")

surfaces = [
    ("Monitors & Glass", "Sticks flat without falling", (22, 163, 74), (240, 253, 244)),
    ("Notebooks & Planners", "Won't flip or catch in bags", (22, 163, 74), (240, 253, 244)),
    ("Smooth Doors & Fridges", "Full-back hold against drafts", (22, 163, 74), (240, 253, 244)),
    ("Avoid Dusty / Textured Walls", "Wipe surface dry before sticking", (217, 119, 6), (254, 252, 232)),
]
for idx, (title, desc, col, bg) in enumerate(surfaces):
    x0 = 70 + idx * 470
    x1 = x0 + 440
    draw_rounded_rect(draw1, (x0, 1630, x1, 1925), 20, fill=bg, outline=col, width=3)
    draw1.text(((x0 + x1) // 2, 1730), title, font=get_font(29, True), fill=col, anchor="mm")
    draw1.text(((x0 + x1) // 2, 1815), desc, font=get_font(27, False), fill=(51, 65, 85), anchor="mm")

out1 = os.path.join(out_dir, "01_Full_Adhesive_How_To_Peel_Flat_2000x2000.jpg")
canvas1.save(out1, quality=95)
print("Saved:", out1)

# ==============================================================================
# 2. PSS 32x6 ROLL STICKY NOTES: 3-STEP CLEAN CUT GUIDE - 2000x2000
# ==============================================================================
canvas2 = Image.new("RGB", (2000, 2000), (248, 250, 252))
draw2 = ImageDraw.Draw(canvas2)

draw_rounded_rect(draw2, (40, 40, 1960, 250), 28, fill=(15, 23, 42))
draw2.text((1000, 110), "HOW TO DISPENSE & CUT CLEANLY EVERY TIME", font=get_font(64, True), fill=(255, 255, 255), anchor="mm")
draw2.text((1000, 195), "4A Full-Adhesive Roll Sticky Notes with Built-In Serrated Dispenser (0.6 in x 393 in)", font=get_font(36, False), fill=(253, 224, 71), anchor="mm")

draw_rounded_rect(draw2, (40, 290, 1960, 1280), 28, fill=(255, 255, 255), outline=(203, 213, 225), width=4)
img_roll = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\8-----4A Roll Sticky Notes\4A PSS 32\pss 32x6-3.jpg").convert("RGB")
img_roll.thumbnail((1760, 900), Image.Resampling.LANCZOS)
canvas2.paste(img_roll, (1000 - img_roll.width // 2, 330))

steps_roll = [
    ("STEP 1: KEEP UNDER GUIDE BAR", "Ensure the paper strip feeds underneath the clear plastic guide bar before pulling.", (30, 64, 175), (239, 246, 255)),
    ("STEP 2: STEADY ROLL WITH THUMB", "Lightly press your thumb on the top of the roll once you pull out your desired length.", (22, 163, 74), (240, 253, 244)),
    ("STEP 3: TEAR DIAGONALLY AT 45°", "Pull the strip down and across the serrated edge at a 45° angle for a crisp, flat cut.", (217, 119, 6), (254, 252, 232)),
]
for idx, (st, sd, col, bg) in enumerate(steps_roll):
    x0 = 40 + idx * 650
    x1 = x0 + 620
    draw_rounded_rect(draw2, (x0, 1320, x1, 1950), 24, fill=bg, outline=col, width=4)
    draw_rounded_rect(draw2, (x0, 1320, x1, 1430), 24, fill=col)
    draw2.text(((x0 + x1) // 2, 1375), st, font=get_font(34, True), fill=(255, 255, 255), anchor="mm")
    # Wrap text manually
    words = sd.split()
    lines, cur = [], ""
    for w in words:
        if len(cur + " " + w) <= 30:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for l_idx, line in enumerate(lines):
        draw2.text(((x0 + x1) // 2, 1560 + l_idx * 55), line, font=get_font(33, False), fill=(30, 41, 59), anchor="mm")

out2 = os.path.join(out_dir, "02_PSS_32x6_Roll_Dispenser_Clean_Cut_Guide_2000x2000.jpg")
canvas2.save(out2, quality=95)
print("Saved:", out2)

# ==============================================================================
# 3. 4A 5082-Y-Lx2: WHAT'S IN THE BOX (2 PACKS x 2 PADS = 4 PADS TOTAL) - 2000x2000
# ==============================================================================
canvas3 = Image.new("RGB", (2000, 2000), (248, 250, 252))
draw3 = ImageDraw.Draw(canvas3)

draw_rounded_rect(draw3, (40, 40, 1960, 260), 28, fill=(15, 23, 42))
draw3.text((1000, 110), "WHAT'S IN YOUR ORDER: 4 PADS TOTAL (200 SHEETS)", font=get_font(60, True), fill=(255, 255, 255), anchor="mm")
draw3.text((1000, 198), "Delivered as 2 Shrink-Wrapped Twin-Packs (Each Pack Contains 2 Stacked Pads)", font=get_font(38, False), fill=(253, 224, 71), anchor="mm")

img_5082 = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\1-----4A Stiky notes\4A 5082-Y-L\5082-Y-L-1.JPG").convert("RGB")
# Crop tighter around the pad in 5082-Y-L-1.JPG
w, h = img_5082.size
crop_box = (int(w * 0.25), int(h * 0.02), int(w * 0.72), int(h * 0.98))
pad_crop = img_5082.crop(crop_box)
pad_crop.thumbnail((650, 1020), Image.Resampling.LANCZOS)

# Left Twin-Pack
draw_rounded_rect(draw3, (60, 300, 920, 1540), 28, fill=(255, 255, 255), outline=(30, 64, 175), width=4)
draw_rounded_rect(draw3, (60, 300, 920, 400), 28, fill=(30, 64, 175))
draw3.text((490, 350), "TWIN-PACK #1 (2 PADS / 100 SHEETS)", font=get_font(36, True), fill=(255, 255, 255), anchor="mm")
canvas3.paste(pad_crop, (490 - pad_crop.width // 2, 430))
draw_rounded_rect(draw3, (110, 1430, 870, 1515), 16, fill=(239, 246, 255), outline=(59, 130, 246), width=3)
draw3.text((490, 1472), "2 Pads of 50 Sheets Stacked Together in 1 Wrap", font=get_font(30, True), fill=(30, 58, 138), anchor="mm")

# Plus Sign in Middle
draw3.ellipse((940, 840, 1060, 960), fill=(22, 163, 74))
draw3.text((1000, 900), "+", font=get_font(84, True), fill=(255, 255, 255), anchor="mm")

# Right Twin-Pack
draw_rounded_rect(draw3, (1080, 300, 1940, 1540), 28, fill=(255, 255, 255), outline=(30, 64, 175), width=4)
draw_rounded_rect(draw3, (1080, 300, 1940, 400), 28, fill=(30, 64, 175))
draw3.text((1510, 350), "TWIN-PACK #2 (2 PADS / 100 SHEETS)", font=get_font(36, True), fill=(255, 255, 255), anchor="mm")
canvas3.paste(pad_crop, (1510 - pad_crop.width // 2, 430))
draw_rounded_rect(draw3, (1130, 1430, 1890, 1515), 16, fill=(239, 246, 255), outline=(59, 130, 246), width=3)
draw3.text((1510, 1472), "2 Pads of 50 Sheets Stacked Together in 1 Wrap", font=get_font(30, True), fill=(30, 58, 138), anchor="mm")

# Bottom Summary Box
draw_rounded_rect(draw3, (60, 1580, 1940, 1950), 28, fill=(240, 253, 244), outline=(22, 163, 74), width=5)
draw3.text((1000, 1675), "2 SHRINK-WRAPPED TWIN-PACKS  x  2 PADS PER PACK  =  4 PADS TOTAL", font=get_font(44, True), fill=(21, 128, 61), anchor="mm")
draw3.text((1000, 1765), "Each individual pad contains 50 lined sheets (5 x 8 in) -> 100 sheets per wrapped pack -> 200 sheets total.", font=get_font(33, False), fill=(22, 101, 52), anchor="mm")
draw3.text((1000, 1855), "Please open the outer film wrap to separate the 2 stacked pads inside each pack!", font=get_font(36, True), fill=(185, 28, 28), anchor="mm")

out3 = os.path.join(out_dir, "03_5082_Y_Lx2_4Pads_Packaging_Clarity_2000x2000.jpg")
canvas3.save(out3, quality=95)
print("Saved:", out3)
