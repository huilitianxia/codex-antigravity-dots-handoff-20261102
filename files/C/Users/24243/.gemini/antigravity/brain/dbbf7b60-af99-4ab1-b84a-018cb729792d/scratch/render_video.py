import subprocess
import os

ffmpeg_exe = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
raw_video = r"E:\Desktop\5082_Y_L_combined_raw.mp4"
final_video = r"E:\Desktop\5082_Y_L_5x8_sticky_notes_commercial.mp4"

# Subtitle styling:
# Shot 1 (0 to 8s)
# Shot 2 (8 to 16s)
# Shot 3 (16 to 24s)
vf_filters = [
    # Shot 1
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Premium Lined Sticky Notes (5x8 in)':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='4.4X More Writing Space  •  Ruled Lines for Daily Focus':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
    # Shot 2
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Smooth Peel & Zero Curl Technology':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='80 GSM Premium Thick Paper  •  Zero Ink Bleed-Through':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'",
    # Shot 3
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Sticks Firmly & Removes Cleanly':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,16.5,23.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Perfect for Monitors, Daily Planners & Office Desks':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,16.5,23.5)'"
]

vf_arg = ",".join(vf_filters)

cmd = [
    ffmpeg_exe,
    "-y",
    "-i", raw_video,
    "-vf", vf_arg,
    "-c:v", "libx264",
    "-crf", "19",
    "-preset", "medium",
    "-movflags", "+faststart",
    final_video
]

print("Running FFmpeg render...")
result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if result.returncode == 0:
    print(f"SUCCESS! Rendered final video to {final_video}")
    print(f"File size: {os.path.getsize(final_video)} bytes")
else:
    print("ERROR:")
    print(result.stderr)
