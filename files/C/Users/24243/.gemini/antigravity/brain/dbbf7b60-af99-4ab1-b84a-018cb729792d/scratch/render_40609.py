import subprocess
import os

ffmpeg_exe = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
src = r"E:\Desktop\40609_sticky_tabs_flow_video.mp4"
dst = r"E:\Desktop\40609_sticky_index_tabs_commercial.mp4"

def render():
    if not os.path.exists(src):
        print("Source video not found:", src)
        return False

    concat_list = r"E:\Desktop\40609_concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        f.write(f"file '{src}'\nfile '{src}'\n")

    raw_loop = r"E:\Desktop\40609_looped_raw.mp4"
    cmd_loop = [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", raw_loop]
    subprocess.run(cmd_loop, check=True)

    vf_filters = [
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='4A Sticky Index Tabs & Page Flags':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,0.5,7.5)'",
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Vibrant Pastel Colors  |  Repositionable & Translucent Design':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,0.5,7.5)'",
        "drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='Write On & Remove Cleanly  |  No Sticky Residue':fontcolor=white:fontsize=36:box=1:boxcolor=black@0.6:boxborderw=10:x=(w-text_w)/2:y=h-text_h-95:enable='between(t,8.5,15.5)'",
        "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Ideal for Books, Documents, Planners & Study Notes':fontcolor=#ECECEC:fontsize=24:box=1:boxcolor=black@0.6:boxborderw=8:x=(w-text_w)/2:y=h-text_h-55:enable='between(t,8.5,15.5)'"
    ]

    cmd_render = [
        ffmpeg_exe, "-y",
        "-i", raw_loop,
        "-vf", ",".join(vf_filters),
        "-c:v", "libx264",
        "-crf", "19",
        "-preset", "medium",
        "-movflags", "+faststart",
        dst
    ]
    print("Rendering 40609 commercial video...")
    res = subprocess.run(cmd_render, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode == 0:
        print(f"SUCCESS! File created: {dst}, Size: {os.path.getsize(dst)} bytes")
        return True
    else:
        print("Error:", res.stderr)
        return False

if __name__ == "__main__":
    render()
