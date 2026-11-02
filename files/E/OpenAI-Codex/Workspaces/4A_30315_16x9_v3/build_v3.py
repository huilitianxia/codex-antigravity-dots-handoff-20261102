from pathlib import Path
import math
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import imageio_ffmpeg


ROOT = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_v3")
ROOT.mkdir(parents=True, exist_ok=True)
SRC_LONG = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\video\2026-08\20e48bc5223d0b455548c73360654ced.mp4")
SRC_HORIZONTAL = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\video\2026-08\3c1f303d527014601959185ca514226a_raw.mp4")
IMG_PACK = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\702877124802.pt01.png")
IMG_TOWER = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\30315-1修改.png")
IMG_COLORS = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\30315-4.JPG")
IMG_LOGO = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_preview\logo_src\65.5.jpg")

SILENT = ROOT / "4A_30315_16x9_v3_refined_silent.mp4"
AUDIO = ROOT / "4A_30315_16x9_v3_refined_audio.wav"
FINAL = ROOT / "4A_30315_16x9_v3_refined.mp4"
POSTER = ROOT / "4A_30315_16x9_v3_refined_poster.jpg"

W, H, FPS, DURATION = 1920, 1080, 30, 45.0
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"
FONT_R = r"C:\Windows\Fonts\arial.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def text(draw, xy, value, size, fill, bold=False, anchor="la", stroke=0):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor,
              stroke_width=stroke, stroke_fill=(0, 0, 0, 120))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def crop_nonwhite(path, pad=8):
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im.convert("RGB"))
    mask = np.min(arr, axis=2) < 246
    ys, xs = np.where(mask)
    if len(xs):
        im = im.crop((max(0, xs.min()-pad), max(0, ys.min()-pad),
                      min(im.width, xs.max()+pad+1), min(im.height, ys.max()+pad+1)))
    return im


def fit_image(path, size, crop_white=False, contain=True):
    im = crop_nonwhite(path) if crop_white else Image.open(path).convert("RGBA")
    scale = min(size[0]/im.width, size[1]/im.height) if contain else max(size[0]/im.width, size[1]/im.height)
    im = im.resize((max(1, round(im.width*scale)), max(1, round(im.height*scale))), Image.Resampling.LANCZOS)
    return im


def bg():
    yy, xx = np.mgrid[0:H, 0:W]
    base = np.empty((H, W, 3), np.float32)
    base[:] = (248, 247, 241)
    glow1 = np.exp(-(((xx-320)/620)**2 + ((yy-230)/520)**2))[..., None]
    glow2 = np.exp(-(((xx-1600)/720)**2 + ((yy-820)/570)**2))[..., None]
    base = base*(1-glow1*.09) + np.array([255,235,102],np.float32)*glow1*.09
    base = base*(1-glow2*.065) + np.array([255,148,202],np.float32)*glow2*.065
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")


def intro(t):
    im = bg()
    pack = fit_image(IMG_PACK, (1020, 750), crop_white=True)
    a = ease(t/0.7)
    scale = 0.94 + 0.06*a
    pack = pack.resize((round(pack.width*scale), round(pack.height*scale)), Image.Resampling.LANCZOS)
    im.alpha_composite(pack, (55, 145))
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (1110, 230), "4A 30315", 82, (236,62,82,255), True)
    text(d, (1110, 345), "NEON ASSORTED", 58, (25,30,36,255), True)
    text(d, (1110, 420), "STICKY NOTES", 58, (25,30,36,255), True)
    d.rounded_rectangle((1110,520,1755,610), 42, fill=(255,255,255,238), outline=(20,25,30,35), width=2)
    text(d, (1432,565), "15 COLORS  •  3 × 3 IN", 32, (35,40,47,255), True, "mm")
    text(d, (1110, 705), "15 Pads  •  100 Sheets/Pad", 34, (63,68,76,255), True)
    text(d, (1110, 770), "1,500 Sheets Total", 31, (83,89,97,255))
    text(d, (1110, 865), "Bright notes. Clear ideas.", 33, (35,40,47,255))
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def colors_card(t):
    im = bg()
    photo = fit_image(IMG_COLORS, (1060, 810), contain=True)
    card = Image.new("RGBA", (1110, 860), (255,255,255,238))
    card.alpha_composite(photo, ((card.width-photo.width)//2, (card.height-photo.height)//2))
    mask = Image.new("L", card.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,card.width,card.height), 38, fill=255)
    card.putalpha(mask)
    im.alpha_composite(card, (55, 110))
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (1220, 240), "15 COLORS", 66, (25,30,36,255), True)
    text(d, (1220, 330), "ONE PACK", 66, (25,30,36,255), True)
    text(d, (1220, 435), "Color-code tasks, ideas,\nand reminders at a glance.", 33, (75,81,89,255))
    chips = [(255,73,159,255),(255,228,55,255),(91,216,141,255),(67,178,232,255),(150,99,210,255),(255,145,60,255)]
    for i,c in enumerate(chips):
        x = 1220 + (i%3)*165; y = 650 + (i//3)*125
        d.rounded_rectangle((x,y,x+125,y+92), 18, fill=(0,0,0,24))
        d.rounded_rectangle((x-6,y-8,x+119,y+84), 16, fill=c)
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def outro(t):
    im = bg()
    tower = fit_image(IMG_TOWER, (650, 1000), crop_white=True)
    im.alpha_composite(tower, (85, 40))
    d = ImageDraw.Draw(im, "RGBA")
    text(d, (850, 205), "4A 30315", 72, (236,62,82,255), True)
    text(d, (850, 320), "PEEL. STICK. WRITE.", 56, (25,30,36,255), True)
    text(d, (850, 397), "REPEAT.", 56, (25,30,36,255), True)
    d.rounded_rectangle((850,515,1740,610), 45, fill=(255,255,255,240), outline=(25,30,36,35), width=2)
    text(d, (1295,563), "15 COLORS  •  15 PADS  •  1,500 SHEETS", 29, (40,45,52,255), True, "mm")
    text(d, (850, 720), "3 × 3 in / 76 × 76 mm", 34, (76,82,90,255))
    text(d, (850, 785), "100 sheets per pad", 34, (76,82,90,255))
    text(d, (850, 895), "Make every note count.", 36, (35,40,47,255), True)
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def portrait_to_16x9(frame):
    bgframe = cv2.resize(frame, (W,H), interpolation=cv2.INTER_CUBIC)
    bgframe = cv2.GaussianBlur(bgframe, (0,0), 35)
    bgframe = cv2.convertScaleAbs(bgframe, alpha=0.67, beta=20)
    scale = H/frame.shape[0]
    fg = cv2.resize(frame, (round(frame.shape[1]*scale), H), interpolation=cv2.INTER_LANCZOS4)
    x = (W-fg.shape[1])//2
    cv2.rectangle(bgframe, (x-10,0), (x+fg.shape[1]+10,H), (18,18,18), -1)
    bgframe[:,x:x+fg.shape[1]] = fg
    return bgframe


def horizontal_clean(frame, zoom=1.0, cx=0.50):
    if frame.shape[1] != W or frame.shape[0] != H:
        frame = cv2.resize(frame, (W,H), interpolation=cv2.INTER_LANCZOS4)
    if zoom > 1:
        cw, ch = round(W/zoom), round(H/zoom)
        x0 = max(0, min(W-cw, round(W*cx-cw/2)))
        # Bias upward so old embedded lower captions are cropped away.
        y0 = max(0, min(H-ch, round((H-ch)*.12)))
        frame = cv2.resize(frame[y0:y0+ch, x0:x0+cw], (W,H), interpolation=cv2.INTER_LANCZOS4)
    return cv2.convertScaleAbs(frame, alpha=1.03, beta=1)


def logo_asset():
    logo = Image.open(IMG_LOGO).convert("RGBA").crop((790,260,1195,560))
    logo.thumbnail((205,130), Image.Resampling.LANCZOS)
    return logo


LOGO = logo_asset()


def overlay_action(frame, title, detail, accent, show_logo=True):
    im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0,0,0,0))
    d = ImageDraw.Draw(ov, "RGBA")
    if show_logo:
        d.rounded_rectangle((1655,28,1890,176), 27, fill=(255,255,255,228), outline=(255,255,255,110), width=2)
        ov.alpha_composite(LOGO, (1670+(205-LOGO.width)//2, 37+(130-LOGO.height)//2))
    # Transparent typography keeps the action visible; a restrained shadow preserves readability.
    d.rounded_rectangle((84,900,94,1018), 5, fill=accent)
    text(d, (120, 904), title, 45, (255,255,255,255), True, stroke=3)
    text(d, (120, 969), detail, 26, (246,248,251,252), stroke=2)
    return cv2.cvtColor(np.asarray(Image.alpha_composite(im,ov).convert("RGB")), cv2.COLOR_RGB2BGR)


class Decoder:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(str(path))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.last = -100

    def get(self, seconds):
        idx = round(seconds*self.fps)
        if idx != self.last + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = self.cap.read()
        self.last = idx
        if not ok:
            raise RuntimeError(f"Unable to decode {seconds}")
        return frame

    def close(self):
        self.cap.release()


# dst, duration, source, source_start, title, detail, accent, zoom, focus_x
SEGMENTS = [
    (7.5, 5.2, "long", 8.2, "PEEL. PLACE. PRESS.", "A practical adhesive edge that is easy to handle.", (255,72,159,255), 1.0, .5),
    (12.7, 5.5, "horizontal", 31.5, "SMOOTH WRITING", "A clean paper surface for quick, effortless notes.", (71,181,235,255), 1.32, .36),
    (18.2, 5.0, "horizontal", 49.0, "REMOVE CLEANLY", "Lift smoothly and leave the surface ready for what is next.", (255,225,60,255), 1.30, .36),
    (23.2, 4.0, "horizontal", 53.1, "STICK. LIFT. RE-STICK.", "Move the same reminder when priorities change.", (92,216,141,255), 1.08, .56),
    (27.2, 7.0, "horizontal", 57.0, "READY FOR MORE SURFACES", "Books, cups, walls, computers, cartons and wood.", (255,139,61,255), 1.0, .5),
    (34.2, 6.3, "long", 348.0, "15 COLORS. MORE POSSIBILITIES.", "Organize ideas with color, shapes and flexible layouts.", (151,99,210,255), 1.0, .5),
]


def build_video():
    writer = cv2.VideoWriter(str(SILENT), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W,H))
    long_dec = Decoder(SRC_LONG)
    horiz_dec = Decoder(SRC_HORIZONTAL)
    total = round(DURATION*FPS)
    for i in range(total):
        t = i/FPS
        if t < 4.2:
            frame = intro(t)
        elif t < 7.5:
            frame = colors_card(t-4.2)
        elif t >= 40.5:
            frame = outro(t-40.5)
        else:
            seg = next(s for s in SEGMENTS if s[0] <= t < s[0]+s[1])
            dst,dur,src,src_start,title,detail,accent,zoom,cx = seg
            local = t-dst
            raw = (long_dec if src=="long" else horiz_dec).get(src_start+local)
            frame = portrait_to_16x9(raw) if src=="long" else horizontal_clean(raw, zoom, cx)
            # The wide source already carries its own 4A mark unless the close crop removes it.
            add_logo = src == "long" or zoom > 1.20
            frame = overlay_action(frame, title, detail, accent, show_logo=add_logo)
            # Short exposure dip makes source changes feel intentional rather than abrupt.
            edge = min(local, dur-local)
            if edge < .16:
                strength = .08*(1-edge/.16)
                frame = cv2.convertScaleAbs(frame, alpha=1-strength, beta=255*strength)
        writer.write(frame)
        if i == 60:
            cv2.imwrite(str(POSTER), frame)
    writer.release()
    long_dec.close(); horiz_dec.close()


def add_tone(buf, start, duration, freq, amp, decay=2.5, pan=0.0, harmonics=(1.0,.22,.08)):
    sr = 48000
    a = max(0, round(start*sr)); b = min(len(buf), a+round(duration*sr))
    if b <= a: return
    tt = np.arange(b-a)/sr
    env = np.minimum(1.0, tt/.012) * np.exp(-decay*tt)
    wave = sum(h*np.sin(2*np.pi*freq*(j+1)*tt) for j,h in enumerate(harmonics))
    left = math.sqrt((1-pan)/2); right = math.sqrt((1+pan)/2)
    buf[a:b,0] += amp*left*env*wave
    buf[a:b,1] += amp*right*env*wave


def noise_event(buf, start, duration, amp, low, high, pan=0.0, kind="peel"):
    sr = 48000
    n = max(1, round(duration*sr))
    rng = np.random.default_rng(round(start*1000)+len(kind)*17)
    raw = rng.normal(0,1,n)
    sos = butter(3, [low/(sr/2), high/(sr/2)], btype="bandpass", output="sos")
    raw = sosfilt(sos, raw)
    raw /= max(1e-9, np.max(np.abs(raw)))
    tt = np.arange(n)/sr
    if kind == "write":
        env = (0.50+0.50*np.sin(2*np.pi*7.5*tt)**2) * np.minimum(1,tt/.05) * np.minimum(1,(duration-tt)/.08)
    else:
        env = np.minimum(1,tt/.018) * np.minimum(1,(duration-tt)/.10)
        env *= (1-.45*tt/max(duration,.001))
    a = round(start*sr); b = min(len(buf),a+n); raw = raw[:b-a]*env[:b-a]
    left = math.sqrt((1-pan)/2); right = math.sqrt((1+pan)/2)
    buf[a:b,0] += amp*left*raw
    buf[a:b,1] += amp*right*raw


def tap(buf, start, amp=.10, pan=0.0):
    # Soft fingertip/paper contact without a synthetic tonal click.
    noise_event(buf,start,.075,amp*.55,120,1350,pan,"tap")
    noise_event(buf,start+.012,.045,amp*.28,850,3200,pan,"tap2")


def build_audio():
    sr = 48000
    n = round(DURATION*sr)
    music = np.zeros((n,2), np.float64)
    # 120 BPM, bright major-key plucks, soft pads, bass, shaker and kick.
    chords = [(261.63,329.63,392.00),(220.00,261.63,329.63),(174.61,220.00,261.63),(196.00,246.94,293.66)]
    for beat in range(round(DURATION*2)):
        t = beat*.5
        chord = chords[(beat//8)%4]
        full = t < 7.5 or t >= 40.5
        level = 1.0 if full else .58
        note = chord[(beat//2)%3]
        add_tone(music,t,.42,note*2,.075*level,4.8,(-.25 if beat%2==0 else .25),(1,.18,.05))
        if beat%2==0:
            add_tone(music,t,.30,chord[0]/2,.085*level,5.0,0,(1,.12))
            tap(music,t,.035*level,0)
        if beat%4==2:
            noise_event(music,t,.10,.018*level,1800,9500,.25,"hat")
        if beat%8==0:
            for f in chord:
                add_tone(music,t,3.7,f,.018*level,.45,0,(1,.08))
    # Foley is rebuilt from scratch; no source audio or speech is retained.
    foley = np.zeros_like(music)
    noise_event(foley,7.9,.36,.032,300,3200,-.2,"peel")
    noise_event(foley,9.1,.28,.026,380,3500,.0,"peel")
    tap(foley,10.3,.035,.12); tap(foley,10.7,.030,.16)
    # Pencil-on-paper: quiet mid-frequency texture with changing hand pressure.
    noise_event(foley,13.2,4.25,.016,650,3100,.05,"write")
    noise_event(foley,18.7,.68,.035,260,3000,-.1,"peel")
    tap(foley,21.9,.030,.15)
    noise_event(foley,23.7,.42,.032,280,3200,-.05,"peel")
    tap(foley,24.8,.034,.10)
    noise_event(foley,25.6,.38,.030,280,3200,.1,"peel")
    tap(foley,26.4,.034,.12)
    for j,ts in enumerate([27.8,28.7,29.6,30.5,31.4,32.3,33.2]):
        tap(foley,ts,.022,(-.45+j*.15))
    # Gentle whooshes at section changes.
    for ts in [4.2,7.5,12.7,18.2,23.2,27.2,34.2,40.5]:
        noise_event(foley,max(0,ts-.18),.36,.035,500,8000,0,"whoosh")
    mix = music + foley
    peak = np.max(np.abs(mix))
    if peak > .94: mix *= .94/peak
    wavfile.write(AUDIO, sr, (mix*32767).astype(np.int16))


def mux():
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff,"-y","-i",str(SILENT),"-i",str(AUDIO),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","256k","-shortest","-movflags","+faststart",str(FINAL)], check=True)


if __name__ == "__main__":
    build_video()
    build_audio()
    mux()
    print(FINAL)
