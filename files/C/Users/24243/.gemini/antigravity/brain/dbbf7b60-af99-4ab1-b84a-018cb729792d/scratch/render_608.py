import subprocess
import os

ffmpeg_exe = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
s1 = r"E:\Desktop\608_shot1_writing.mp4"
s2 = r"E:\Desktop\608_shot2_peeling.mp4"
s3 = r"E:\Desktop\608_shot3_sticking.mp4"
concat_list = r"E:\Desktop\608_concat_list.txt"
raw_video = r"E:\Desktop\608_combined_raw.mp4"
final_video = r"E:\Desktop\608_N_L_210_large_lined_sticky_notes_commercial.mp4"

# Step 1: Create concat list
with open(concat_list, 'w', encoding='utf-8') as f:
    f.write(f"file '{s1}'\nfile '{s2}'\nfile '{s3}'\n")

# Step 2: Concat raw video
concat_cmd = [
    ffmpeg_exe, "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c", "copy",
    raw_video
]
print("Concatenating 3 shots...")
res_concat = subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res_concat.returncode != 0:
    print("Concat error:", res_concat.stderr)
    exit(1)
print(f"Raw combined video created: {os.path.getsize(raw_video)} bytes")

# Step 3: Burn dual-line professional English captions
vf_filters = [
    # Shot 1 (0 to 8s)
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Large Lined Sticky Notes (6x8 in)':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='5.3X More Writing Area  |  Spacious Lines for Daily Agendas':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
    # Shot 2 (8 to 16s)
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Smooth Peel & 80 GSM Thick Paper':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='7 Vibrant Neon Colors  |  Clean Tear & Zero Bleed-Through':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'",
    # Shot 3 (16 to 24s)
    "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Super Sticky Adhesive Band':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,16.5,23.5)'",
    "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Sticks Firmly Flat on Whiteboards, Monitors & Walls':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,16.5,23.5)'"
]

cmd = [
    ffmpeg_exe,
    "-y",
    "-i", raw_video,
    "-vf", ",".join(vf_filters),
    "-c:v", "libx264",
    "-crf", "19",
    "-preset", "medium",
    "-movflags", "+faststart",
    final_video
]

print("Rendering final video with subtitles...")
res_render = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res_render.returncode == 0:
    print(f"SUCCESS! Rendered final video to {final_video}")
    print(f"Final file size: {os.path.getsize(final_video)} bytes")
else:
    print("Render error:", res_render.stderr)
