from pathlib import Path
import cv2
import numpy as np

src = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\video\2026-08\20e48bc5223d0b455548c73360654ced.mp4")
out = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_preview\long_source_review")
out.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(str(src))
times = [i * 2.0 for i in range(178)]
frames = []
for t in times:
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    if not ok:
        continue
    frame = cv2.resize(frame, (204, 360), interpolation=cv2.INTER_AREA)
    cv2.rectangle(frame, (0, 0), (204, 34), (0, 0, 0), -1)
    cv2.putText(frame, f"{int(t//60):02d}:{int(t%60):02d}", (8, 25), cv2.FONT_HERSHEY_SIMPLEX,
                0.68, (255, 255, 255), 2, cv2.LINE_AA)
    frames.append(frame)
cap.release()

per_sheet = 30
cols = 10
for sheet_idx in range((len(frames) + per_sheet - 1) // per_sheet):
    chunk = frames[sheet_idx * per_sheet:(sheet_idx + 1) * per_sheet]
    rows = []
    for i in range(0, per_sheet, cols):
        row = chunk[i:i + cols]
        while len(row) < cols:
            row.append(np.full((360, 204, 3), 246, np.uint8))
        rows.append(np.hstack(row))
    sheet = np.vstack(rows)
    cv2.imwrite(str(out / f"sheet_{sheet_idx+1:02d}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])

print(out)
