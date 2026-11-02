import subprocess
import os

ffmpeg_exe = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"

def build_video(name, s1_name, s2_name, s3_name, raw_out, final_out, captions):
    concat_txt = f"E:/Desktop/{name}_concat.txt"
    # use relative filenames since concat.txt is in E:/Desktop
    with open(concat_txt, 'w', encoding='utf-8') as f:
        f.write(f"file '{s1_name}'\nfile '{s2_name}'\nfile '{s3_name}'\n")
    
    # concat
    cmd_cat = [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_out]
    res_cat = subprocess.run(cmd_cat, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res_cat.returncode != 0:
        print(f"Concat error {name}:", res_cat.stderr[-200:])
        return False
    print(f"Raw video created: {raw_out} ({os.path.getsize(raw_out)} bytes)")
    
    # filter
    cmd_render = [
        ffmpeg_exe, "-y", "-i", raw_out,
        "-vf", ",".join(captions),
        "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-movflags", "+faststart",
        final_out
    ]
    res = subprocess.run(cmd_render, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"SUCCESS: {final_out} ({os.path.getsize(final_out)} bytes)")
        return True
    else:
        print(f"ERROR rendering {name}: {res.stderr[-200:]}")
        return False

# 1. PSS 32x6
pss_caps = [
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Roll Sticky Notes with Dispenser':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Built-in Precision Cutter  |  Pull & Cut Any Custom Length':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='100% Full Adhesive Backing':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Sticks Firmly to Curved Surfaces  |  Zero Edge Curling & Residue-Free':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='6 Vibrant Neon Colors Value Pack':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,16.5,23.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Ideal for Office Organization, Labeling & Lab Supplies':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,16.5,23.5)'"
]
build_video("pss", "pss_s1.mp4", "pss_s2.mp4", "pss_s3.mp4", "E:/Desktop/pss_raw.mp4", "E:/Desktop/PSS_32x6_roll_sticky_notes_commercial.mp4", pss_caps)

# 2. 5084-N-L
c5084_caps = [
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Large Lined Sticky Notes (5x8 in)':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='4.4X More Writing Area  |  Spacious Lines for Daily Agenda':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Smooth Peel & Strong Stick':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Sticks Flat on Whiteboards & Monitors  |  No Curling or Residue':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4 Vibrant Neon Colors (200 Sheets Total)':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,16.5,23.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Heavyweight 80 GSM Paper  |  Zero Ink Bleed-Through':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,16.5,23.5)'"
]
build_video("5084", "5084_s1.mp4", "5084_s2.mp4", "5084_s3.mp4", "E:/Desktop/5084_raw.mp4", "E:/Desktop/5084_N_L_5x8_sticky_notes_commercial.mp4", c5084_caps)

# 3. 301x12-Y
c301_caps = [
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Mini Sticky Notes (1.5x2 in, 1200 Sheets)':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='12 Pads Bulk Pack  |  Classic Canary Yellow for Quick Flags':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Perfect for Textbooks, Planners & Contracts':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Quick Page Indexing & Reminders  |  Clean Removal Without Tearing':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Compact, Portable & Pocket-Sized':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,16.5,23.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='4A Trusted Quality  |  Essential for Students, Teachers & Lawyers':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,16.5,23.5)'"
]
build_video("301", "301_s1.mp4", "301_s2.mp4", "301_s3.mp4", "E:/Desktop/301_raw.mp4", "E:/Desktop/301x12_Y_mini_sticky_notes_commercial.mp4", c301_caps)

print("--- ALL 3 VIDEOS RENDERED TO DESKTOP ---")
