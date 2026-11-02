from pathlib import Path
import cv2
import numpy as np

src = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\file\2026-07\video_2.ts")
out = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_preview\reference_review")
out.mkdir(parents=True, exist_ok=True)
cap = cv2.VideoCapture(str(src))
frames = []
for t in [i * 1.0 for i in range(61)]:
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    if not ok:
        continue
    frame = cv2.resize(frame, (427, 240), interpolation=cv2.INTER_AREA)
    cv2.rectangle(frame, (0, 0), (427, 30), (0, 0, 0), -1)
    cv2.putText(frame, f"{int(t//60):02d}:{int(t%60):02d}", (8, 22), cv2.FONT_HERSHEY_SIMPLEX,
                0.58, (255, 255, 255), 2, cv2.LINE_AA)
    frames.append(frame)
cap.release()
cols = 5
per = 20
for si in range((len(frames)+per-1)//per):
    chunk=frames[si*per:(si+1)*per]
    rows=[]
    for i in range(0, per, cols):
        row=chunk[i:i+cols]
        while len(row)<cols: row.append(np.full((240,427,3),246,np.uint8))
        rows.append(np.hstack(row))
    cv2.imwrite(str(out/f"sheet_{si+1:02d}.jpg"),np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,92])
print(out)
