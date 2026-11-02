import subprocess
import os

vids = [
    r'E:\Desktop\301x12_Y_mini_sticky_notes_commercial.mp4',
    r'E:\Desktop\30315_15_colors_rainbow_sticky_notes_commercial.mp4',
    r'E:\Desktop\40609_sticky_index_tabs_commercial.mp4',
    r'E:\Desktop\5082_Y_L_5x8_sticky_notes_commercial.mp4',
    r'E:\Desktop\5084_N_L_5x8_sticky_notes_commercial.mp4',
    r'E:\Desktop\608_N_L_210_large_lined_sticky_notes_commercial.mp4',
    r'E:\Desktop\PSS_32x6_roll_sticky_notes_commercial.mp4'
]

out_dir = r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\video_audit'
os.makedirs(out_dir, exist_ok=True)

ffmpeg_exe = r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe'

for v in vids:
    if os.path.exists(v):
        name = os.path.basename(v).split('.')[0]
        # Extract 2 frames: one at 2s, one at 8s
        f1 = os.path.join(out_dir, f'{name}_f02s.jpg')
        f2 = os.path.join(out_dir, f'{name}_f08s.jpg')
        subprocess.run([ffmpeg_exe, '-y', '-ss', '00:00:02', '-i', v, '-vframes', '1', '-q:v', '2', f1], capture_output=True)
        subprocess.run([ffmpeg_exe, '-y', '-ss', '00:00:08', '-i', v, '-vframes', '1', '-q:v', '2', f2], capture_output=True)
        print(f"Extracted frames for {name}: f02s={os.path.exists(f1)}, f08s={os.path.exists(f2)}")
