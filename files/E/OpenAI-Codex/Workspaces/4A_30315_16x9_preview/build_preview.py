from pathlib import Path
import math
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg


OUT_DIR = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_preview")
OUT_DIR.mkdir(parents=True, exist_ok=True)
SOURCE = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\video\2026-08\3c1f303d527014601959185ca514226a_raw.mp4")
SILENT_VIDEO = OUT_DIR / "4A_30315_16x9_preview_silent.mp4"
FINAL_VIDEO = OUT_DIR / "4A_30315_16x9_preview_v1.mp4"
POSTER = OUT_DIR / "4A_30315_16x9_preview_poster.jpg"

W, H = 1920, 1080
FPS = 30
DURATION = 25.0

FONT_BOLD_PATH = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG_PATH = r"C:\Windows\Fonts\arial.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_REG_PATH, size)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def draw_text(draw, xy, text, size, color, bold=False, anchor="la", stroke=0, stroke_fill=(0, 0, 0, 0)):
    draw.text(xy, text, font=font(size, bold), fill=color, anchor=anchor,
              stroke_width=stroke, stroke_fill=stroke_fill)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_intro_background(t):
    yy, xx = np.mgrid[0:H, 0:W]
    base = np.zeros((H, W, 3), np.float32)
    base[:] = (247, 246, 241)
    glow = np.exp(-(((xx - 420) / 650) ** 2 + ((yy - 400) / 520) ** 2))[:, :, None]
    base = base * (1 - glow * 0.10) + np.array([255, 239, 123], np.float32) * glow * 0.10
    return np.clip(base, 0, 255).astype(np.uint8)


def make_intro(t):
    frame = make_intro_background(t)
    im = Image.fromarray(frame).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    colors = [
        (255, 239, 73, 255), (255, 82, 169, 255), (98, 218, 146, 255),
        (82, 183, 234, 255), (153, 105, 214, 255), (255, 151, 71, 255),
        (255, 196, 207, 255), (191, 235, 86, 255)
    ]
    positions = [
        (80, 108, -7), (390, 690, 8), (690, 110, 6), (1420, 690, -8),
        (1560, 120, 7), (1030, 710, 5), (1210, 100, -4), (110, 730, -5)
    ]
    for i, ((x, y, ang), c) in enumerate(zip(positions, colors)):
        note = Image.new("RGBA", (280, 280), (0, 0, 0, 0))
        nd = ImageDraw.Draw(note, "RGBA")
        nd.rounded_rectangle((10, 10, 270, 270), radius=8, fill=(0, 0, 0, 34))
        nd.rounded_rectangle((0, 0, 260, 260), radius=6, fill=c)
        note = note.rotate(ang + math.sin(t * 1.4 + i) * 1.2, resample=Image.Resampling.BICUBIC, expand=True)
        float_y = int(math.sin(t * 1.8 + i * 0.7) * 8)
        im.alpha_composite(note, (x, y + float_y))
    d = ImageDraw.Draw(im, "RGBA")
    a = ease(t / 0.7)
    title_y = 400 + int((1 - a) * 22)
    draw_text(d, (960, title_y), "4A STICKY NOTES", 96, (26, 31, 38, int(255 * a)), True, "mm")
    draw_text(d, (960, title_y + 93), "Color your ideas. Make every note count.", 38,
              (66, 72, 82, int(235 * a)), False, "mm")
    rounded(d, (665, 585, 1255, 660), 38, (255, 255, 255, int(235 * a)),
            (22, 26, 31, int(35 * a)), 2)
    draw_text(d, (960, 622), "15 NEON COLORS  •  3 × 3 IN", 29, (35, 39, 45, int(255 * a)), True, "mm")
    return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def make_outro(t):
    frame = make_intro_background(t)
    im = Image.fromarray(frame).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    neon = [(255, 82, 169, 255), (255, 236, 70, 255), (95, 216, 145, 255), (82, 180, 232, 255), (149, 103, 210, 255)]
    for i, c in enumerate(neon):
        x = 95 + i * 150
        y = 165 + (i % 2) * 55
        d.rounded_rectangle((x + 12, y + 14, x + 262, y + 264), radius=9, fill=(0, 0, 0, 30))
        d.rounded_rectangle((x, y, x + 250, y + 250), radius=7, fill=c)
    draw_text(d, (1090, 265), "4A 30315", 48, (255, 75, 91, 255), True, "la")
    draw_text(d, (1090, 365), "15 Pads  •  100 Sheets/Pad", 43, (31, 35, 42, 255), True, "la")
    draw_text(d, (1090, 435), "1,500 Sheets Total", 36, (76, 81, 90, 255), False, "la")
    draw_text(d, (1090, 555), "PEEL. STICK. WRITE. REPEAT.", 40, (31, 35, 42, 255), True, "la")
    draw_text(d, (1090, 625), "Bright notes for work, study and everyday ideas.", 29, (84, 89, 98, 255), False, "la")
    return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def overlay_logo_and_caption(frame, t_global, label, sublabel, accent):
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")

    # Hide the mismatched legacy package card (5 pads / 400 sheets) in the source.
    # Replace it with the correct 4A 30315 specification card for this product.
    if label != "STICK. PEEL. RE-STICK.":
        rounded(d, (1190, 365, 1488, 650), 24, (255, 255, 255, 238), (29, 34, 41, 38), 2)
        draw_text(d, (1230, 415), "4A 30315", 30, (239, 67, 86, 255), True, "la")
        draw_text(d, (1230, 480), "15 COLORS", 35, (30, 34, 40, 255), True, "la")
        draw_text(d, (1230, 535), "15 PADS", 29, (64, 69, 77, 255), True, "la")
        draw_text(d, (1230, 585), "1,500 SHEETS", 25, (91, 96, 104, 255), False, "la")

    # Cover legacy source captions while preserving the action.
    d.rectangle((0, 835, 1920, 1080), fill=(15, 18, 23, 150))
    rounded(d, (92, 882, 112, 1018), 10, accent)
    draw_text(d, (148, 910), label, 54, (255, 255, 255, 255), True, "la")
    draw_text(d, (150, 984), sublabel, 29, (239, 242, 246, 245), False, "la")

    # Quick color chip motif.
    chips = [(255, 79, 168, 255), (255, 237, 65, 255), (91, 219, 145, 255), (73, 182, 235, 255)]
    for i, c in enumerate(chips):
        d.rounded_rectangle((1545 + i * 70, 946, 1593 + i * 70, 994), radius=8, fill=c)

    im = Image.alpha_composite(im, ov)
    return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def decode_source():
    cap = cv2.VideoCapture(str(SOURCE))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {SOURCE}")
    src_fps = cap.get(cv2.CAP_PROP_FPS)
    cache = {"idx": -1, "frame": None}

    def get(sec):
        idx = int(round(sec * src_fps))
        if idx != cache["idx"]:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, fr = cap.read()
            if not ok:
                raise RuntimeError(f"Cannot decode frame at {sec:.3f}s")
            cache["idx"], cache["frame"] = idx, fr
        return cache["frame"].copy()

    return cap, get


def add_transition(frame, local_t, dur, at_start=True):
    edge = 0.22
    if at_start and local_t < edge:
        a = local_t / edge
        frame = cv2.convertScaleAbs(frame, alpha=a, beta=255 * (1 - a))
    if (not at_start) and local_t > dur - edge:
        a = (dur - local_t) / edge
        frame = cv2.convertScaleAbs(frame, alpha=max(0, a), beta=255 * (1 - max(0, a)))
    return frame


def build_video():
    cap, get = decode_source()
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(SILENT_VIDEO), fourcc, FPS, (W, H))
    if not writer.isOpened():
        raise RuntimeError("Could not open video writer")

    segments = [
        # timeline start, duration, source start, source rate, headline, detail, accent
        (2.35, 4.45, 15.30, 1.0, "PEELS SMOOTHLY", "Easy, controlled removal — sheet after sheet.", (255, 81, 164, 255)),
        (6.80, 4.25, 38.35, 1.0, "STICKS FLAT", "Presses down cleanly for a neat, curl-free finish.", (255, 229, 63, 255)),
        (11.05, 4.25, 31.00, 1.0, "SMOOTH WRITING", "A clean paper surface for quick, effortless notes.", (69, 183, 236, 255)),
        (15.30, 5.20, 53.55, 1.0, "STICK. PEEL. RE-STICK.", "Reposition notes with reliable everyday hold.", (91, 218, 144, 255)),
    ]

    total_frames = int(round(DURATION * FPS))
    for n in range(total_frames):
        t = n / FPS
        if t < 2.35:
            frame = make_intro(t)
        elif t >= 20.50:
            frame = make_outro(t - 20.50)
        else:
            seg = next(s for s in segments if s[0] <= t < s[0] + s[1])
            start, dur, src, rate, title, detail, accent = seg
            local = t - start
            frame = get(src + local * rate)
            if frame.shape[1] != W or frame.shape[0] != H:
                frame = cv2.resize(frame, (W, H), interpolation=cv2.INTER_LANCZOS4)
            frame = cv2.convertScaleAbs(frame, alpha=1.06, beta=3)
            frame = overlay_logo_and_caption(frame, t, title, detail, accent)
            frame = add_transition(frame, local, dur, at_start=True)
        writer.write(frame)
        if n == int(1.3 * FPS):
            cv2.imwrite(str(POSTER), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 93])
    writer.release()
    cap.release()


def audio_filter():
    # A light original instrumental bed made from simple synth layers, plus gentle paper/write cues.
    notes = [261.63, 329.63, 392.00, 523.25, 293.66, 369.99, 440.00, 587.33]
    parts = []
    labels = []
    idx = 0
    for beat in range(25):
        f = notes[beat % len(notes)]
        start = beat * 1.0
        parts.append(f"sine=frequency={f}:sample_rate=48000:duration=0.34,volume=0.035,afade=t=out:st=0.18:d=0.16,adelay={int(start*1000)}|{int(start*1000)}[a{idx}]")
        labels.append(f"[a{idx}]")
        idx += 1
        if beat % 2 == 0:
            f2 = f * 2
            parts.append(f"sine=frequency={f2}:sample_rate=48000:duration=0.16,volume=0.018,afade=t=out:st=0.06:d=0.10,adelay={int((start+0.5)*1000)}|{int((start+0.5)*1000)}[a{idx}]")
            labels.append(f"[a{idx}]")
            idx += 1
    # Soft percussive ticks mark feature changes.
    for start in [2.35, 6.80, 11.05, 15.30, 20.50]:
        parts.append(f"anoisesrc=color=pink:sample_rate=48000:duration=0.08,highpass=f=2200,lowpass=f=6200,volume=0.035,afade=t=out:st=0.015:d=0.065,adelay={int(start*1000)}|{int(start*1000)}[a{idx}]")
        labels.append(f"[a{idx}]")
        idx += 1
    # Paper-peel style swishes and a subtle writing texture.
    for start, duration in [(2.8, 0.48), (16.0, 0.42), (18.0, 0.42)]:
        parts.append(f"anoisesrc=color=white:sample_rate=48000:duration={duration},highpass=f=1200,lowpass=f=8200,volume=0.018,afade=t=in:st=0:d=0.06,afade=t=out:st={duration-0.10}:d=0.10,adelay={int(start*1000)}|{int(start*1000)}[a{idx}]")
        labels.append(f"[a{idx}]")
        idx += 1
    parts.append(f"anoisesrc=color=pink:sample_rate=48000:duration=3.2,highpass=f=1800,lowpass=f=4800,volume=0.006,afade=t=in:st=0:d=0.25,afade=t=out:st=2.8:d=0.4,adelay=11600|11600[a{idx}]")
    labels.append(f"[a{idx}]")
    mix = "".join(labels) + f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.85,atrim=duration={DURATION}[mix]"
    return ";".join(parts + [mix])


def mux_audio():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y", "-i", str(SILENT_VIDEO),
        "-filter_complex", audio_filter(),
        "-map", "0:v:0", "-map", "[mix]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(FINAL_VIDEO)
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_video()
    mux_audio()
    print(FINAL_VIDEO)
