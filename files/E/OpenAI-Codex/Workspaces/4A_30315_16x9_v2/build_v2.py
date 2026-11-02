from pathlib import Path
import math
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg


ROOT = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_v2")
ROOT.mkdir(parents=True, exist_ok=True)
SRC = Path(r"E:\xwechat_files\wxid_81xkainbu5d822_de43\msg\video\2026-08\20e48bc5223d0b455548c73360654ced.mp4")
IMG_PACK = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\702877124802.pt01.png")
IMG_TOWER = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\30315-1修改.png")
IMG_COLORS = Path(r"D:\4A\印刷用图片\电商\亚马逊图片-2021\1-----4A Stiky notes\4A 30315\30315-4.JPG")
IMG_LOGO = Path(r"E:\OpenAI-Codex\Workspaces\4A_30315_16x9_preview\logo_src\65.5.jpg")

SILENT = ROOT / "4A_30315_16x9_v2_silent.mp4"
FINAL = ROOT / "4A_30315_16x9_v2.mp4"
POSTER = ROOT / "4A_30315_16x9_v2_poster.jpg"

W, H, FPS, DURATION = 1920, 1080, 30, 39.6
FONT_B = r"C:\Windows\Fonts\arialbd.ttf"
FONT_R = r"C:\Windows\Fonts\arial.ttf"


def fnt(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def txt(d, xy, s, size, fill, bold=False, anchor="la", stroke=0, stroke_fill=(0, 0, 0, 0)):
    d.text(xy, s, font=fnt(size, bold), fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=stroke_fill)


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def cover_fit_pil(path, box, contain=True, background=(248, 247, 241, 255), crop_white=False):
    im = Image.open(path).convert("RGBA")
    if crop_white:
        arr = np.asarray(im.convert("RGB"))
        mask = np.min(arr, axis=2) < 246
        ys, xs = np.where(mask)
        if len(xs):
            im = im.crop((max(0, xs.min()-8), max(0, ys.min()-8), min(im.width, xs.max()+9), min(im.height, ys.max()+9)))
    x0, y0, x1, y1 = box
    bw, bh = x1-x0, y1-y0
    scale = min(bw/im.width, bh/im.height) if contain else max(bw/im.width, bh/im.height)
    nw, nh = max(1, int(im.width*scale)), max(1, int(im.height*scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (bw, bh), background)
    canvas.alpha_composite(im, ((bw-nw)//2, (bh-nh)//2))
    return canvas


def base_bg():
    yy, xx = np.mgrid[0:H, 0:W]
    base = np.zeros((H, W, 3), np.float32)
    base[:] = (247, 246, 240)
    g1 = np.exp(-(((xx-350)/720)**2 + ((yy-260)/600)**2))[:, :, None]
    g2 = np.exp(-(((xx-1600)/650)**2 + ((yy-780)/550)**2))[:, :, None]
    base = base*(1-g1*.07)+np.array([255,239,125],np.float32)*g1*.07
    base = base*(1-g2*.05)+np.array([255,174,214],np.float32)*g2*.05
    return Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert("RGBA")


def intro(t):
    im = base_bg()
    d = ImageDraw.Draw(im, "RGBA")
    # Real 30315 package image.
    pack = cover_fit_pil(IMG_PACK, (70, 115, 1050, 910), contain=True, background=(0,0,0,0), crop_white=True)
    a = ease(t/0.8)
    pack = pack.resize((int(pack.width*(.94+.06*a)), int(pack.height*(.94+.06*a))), Image.Resampling.LANCZOS)
    im.alpha_composite(pack, (70, 105))
    d = ImageDraw.Draw(im, "RGBA")
    txt(d, (1120, 230), "4A 30315", 78, (236,62,82,255), True)
    txt(d, (1120, 340), "NEON ASSORTED", 58, (28,33,39,255), True)
    txt(d, (1120, 415), "STICKY NOTES", 58, (28,33,39,255), True)
    d.rounded_rectangle((1120,520,1745,606), radius=40, fill=(255,255,255,235), outline=(30,35,41,35), width=2)
    txt(d, (1432,563), "15 COLORS  •  3 × 3 IN", 31, (38,43,50,255), True, "mm")
    txt(d, (1120,690), "15 Pads  •  100 Sheets/Pad", 33, (60,66,74,255), True)
    txt(d, (1120,748), "1,500 Sheets Total", 29, (85,91,99,255))
    txt(d, (1120,840), "One note. Endless ideas.", 32, (41,46,53,255), False)
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def color_showcase(t):
    im = base_bg()
    d = ImageDraw.Draw(im, "RGBA")
    colors = cover_fit_pil(IMG_COLORS, (70, 110, 1130, 970), contain=True, background=(0,0,0,0), crop_white=False)
    # Remove the photographed lightbox corners by soft clipping into a clean card.
    mask = Image.new("L", colors.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,colors.width,colors.height), radius=36, fill=255)
    colors.putalpha(mask)
    im.alpha_composite(colors, (70,110))
    d = ImageDraw.Draw(im, "RGBA")
    txt(d, (1235, 235), "15 ASSORTED COLORS", 55, (28,33,39,255), True)
    txt(d, (1235, 340), "Bright choices for every idea.", 32, (76,82,90,255))
    chips=[(255,76,163,255),(255,230,58,255),(88,218,143,255),(71,181,235,255),(148,100,210,255),(255,147,65,255)]
    for i,c in enumerate(chips):
        x=1235+(i%3)*155; y=485+(i//3)*155
        d.rounded_rectangle((x,y,x+120,y+120),radius=16,fill=(0,0,0,30))
        d.rounded_rectangle((x-5,y-7,x+115,y+113),radius=14,fill=c)
    txt(d, (1235, 825), "4A 30315", 34, (236,62,82,255), True)
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def outro(t):
    im = base_bg()
    tower = cover_fit_pil(IMG_TOWER, (90, 55, 770, 1030), contain=True, background=(0,0,0,0), crop_white=True)
    im.alpha_composite(tower, (90,50))
    d = ImageDraw.Draw(im, "RGBA")
    txt(d, (880, 220), "4A 30315", 66, (236,62,82,255), True)
    txt(d, (880, 325), "PEEL. STICK. WRITE.", 55, (28,33,39,255), True)
    txt(d, (880, 402), "MAKE IT YOURS.", 55, (28,33,39,255), True)
    d.rounded_rectangle((880,525,1725,620),radius=44,fill=(255,255,255,235),outline=(32,36,42,32),width=2)
    txt(d,(1302,572),"15 COLORS  •  15 PADS  •  1,500 SHEETS",28,(42,47,54,255),True,"mm")
    txt(d,(880,720),"3 × 3 in / 76 × 76 mm",32,(77,83,91,255))
    txt(d,(880,785),"100 sheets per pad",32,(77,83,91,255))
    return cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def crop_vertical(frame, target_w=1920, target_h=1080):
    # Place the portrait source in a 16:9 canvas with a blurred extension, while keeping the hand/action readable.
    bg = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
    bg = cv2.GaussianBlur(bg, (0,0), 32)
    bg = cv2.convertScaleAbs(bg, alpha=.66, beta=18)
    scale = target_h / frame.shape[0]
    fg = cv2.resize(frame, (int(frame.shape[1]*scale), target_h), interpolation=cv2.INTER_LANCZOS4)
    x = (target_w-fg.shape[1])//2
    # soft side shadow
    cv2.rectangle(bg,(x-12,0),(x+fg.shape[1]+12,target_h),(0,0,0),-1)
    bg[:,x:x+fg.shape[1]]=fg
    return bg


def overlay_action(frame, title, detail, accent, show_product_tag=True):
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
    ov=Image.new("RGBA",im.size,(0,0,0,0)); d=ImageDraw.Draw(ov,"RGBA")
    # Persistent 4A crown identity without covering the real action.
    d.rounded_rectangle((1628,34,1872,188),radius=28,fill=(255,255,255,232),outline=(255,255,255,120),width=2)
    logo = Image.open(IMG_LOGO).convert("RGBA").crop((790,260,1195,560))
    logo.thumbnail((220,140), Image.Resampling.LANCZOS)
    ov.alpha_composite(logo, (1640+(220-logo.width)//2, 40+(140-logo.height)//2))
    d.rectangle((0,842,1920,1080),fill=(14,17,22,165))
    d.rounded_rectangle((102,889,122,1020),radius=9,fill=accent)
    txt(d,(160,910),title,52,(255,255,255,255),True)
    txt(d,(160,982),detail,29,(239,242,246,245))
    chips=[(255,76,163,255),(255,231,58,255),(87,218,142,255),(72,181,235,255)]
    for i,c in enumerate(chips): d.rounded_rectangle((1545+i*67,950,1590+i*67,995),radius=8,fill=c)
    return cv2.cvtColor(np.asarray(Image.alpha_composite(im,ov).convert("RGB")),cv2.COLOR_RGB2BGR)


class Decoder:
    def __init__(self,path):
        self.cap=cv2.VideoCapture(str(path)); self.fps=self.cap.get(cv2.CAP_PROP_FPS)
        self.last_idx=-1
    def get(self,sec):
        idx=int(round(sec*self.fps))
        if idx != self.last_idx + 1:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,idx)
        ok,fr=self.cap.read(); self.last_idx=idx
        if not ok: raise RuntimeError(sec)
        return fr
    def close(self): self.cap.release()


# start, duration, src_start, title, detail, accent
SEGMENTS=[
    (8.4, 6.0, 8.4, "PEEL & PLACE", "Easy to handle, with a practical adhesive edge.", (255,77,163,255)),
    (14.4, 6.2, 31.9, "PRESS THE ADHESIVE EDGE", "Secure at the top; a natural free edge is normal.", (88,217,142,255)),
    (20.6, 6.4, 0.0, "SMOOTH WRITING", "A clean paper surface for quick, effortless notes.", (71,181,235,255)),
    (27.0, 5.8, 42.5, "STICK. ORGANIZE. CREATE.", "Build clear layouts, one colorful note at a time.", (255,229,60,255)),
    (32.8, 3.8, 350.0, "15 COLORS. MORE POSSIBILITIES.", "Mix colors and shapes to make ideas stand out.", (153,101,211,255)),
]


def build_video():
    dec=Decoder(SRC)
    wr=cv2.VideoWriter(str(SILENT),cv2.VideoWriter_fourcc(*"mp4v"),FPS,(W,H))
    for n in range(int(DURATION*FPS)):
        t=n/FPS
        if t<4.8: fr=intro(t)
        elif t<8.4: fr=color_showcase(t-4.8)
        elif t>=36.6: fr=outro(t-36.6)
        else:
            s=next(x for x in SEGMENTS if x[0]<=t<x[0]+x[1])
            st,dur,src,title,detail,accent=s; local=t-st
            raw=dec.get(src+local)
            fr=crop_vertical(raw)
            fr=cv2.convertScaleAbs(fr,alpha=1.05,beta=2)
            fr=overlay_action(fr,title,detail,accent)
            # short white dissolves only at segment entrances
            if local<.18:
                a=local/.18; fr=cv2.convertScaleAbs(fr,alpha=a,beta=255*(1-a))
        wr.write(fr)
        if n==int(2.1*FPS): cv2.imwrite(str(POSTER),fr,[cv2.IMWRITE_JPEG_QUALITY,94])
    wr.release(); dec.close()


def bgm_filter():
    # Original light, upbeat synth bed. Product sections are fuller; action sections are deliberately quieter.
    freqs=[261.63,329.63,392.00,523.25,293.66,369.99,440.00,587.33]
    parts=[]; labels=[]; idx=0
    for beat in range(80):
        start=beat*.5; freq=freqs[(beat//2)%len(freqs)]
        # Product intro/outro: stronger. Core action demo: softer.
        full = start<8.4 or start>=36.6
        vol=0.30 if full else 0.07
        parts.append(f"sine=frequency={freq}:sample_rate=48000:duration=0.30,volume={vol},afade=t=out:st=0.12:d=0.18,adelay={int(start*1000)}|{int(start*1000)}[m{idx}]")
        labels.append(f"[m{idx}]"); idx+=1
        if beat%2==1:
            vol2=0.15 if full else 0.035
            parts.append(f"sine=frequency={freq*2}:sample_rate=48000:duration=0.14,volume={vol2},afade=t=out:st=0.05:d=0.09,adelay={int((start+.25)*1000)}|{int((start+.25)*1000)}[m{idx}]")
            labels.append(f"[m{idx}]"); idx+=1
    parts.append("anoisesrc=color=pink:sample_rate=48000:duration=39.6,highpass=f=1400,lowpass=f=5000,volume=0.004[mnoise]")
    labels.append("[mnoise]")
    parts.append("".join(labels)+f"amix=inputs={len(labels)}:duration=longest:normalize=0,alimiter=limit=0.85,atrim=duration={DURATION}[music]")
    return ";".join(parts)


def mux():
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    # Map original action audio with the exact same source offsets as the picture.
    # Intro/outro remain music-led; action segments retain authentic, frame-aligned sound.
    action_specs=[(8.4,6.0,8.4),(31.9,6.2,14.4),(0.0,6.4,20.6),(42.5,5.8,27.0),(350.0,3.8,32.8)]
    filters=[bgm_filter()]
    alabs=[]
    for i,(src,dur,dst) in enumerate(action_specs):
        delay=int(dst*1000)
        filters.append(f"[1:a]atrim=start={src}:duration={dur},asetpts=PTS-STARTPTS,volume=1.35,highpass=f=90,lowpass=f=12000,adelay={delay}|{delay}[orig{i}]")
        alabs.append(f"[orig{i}]")
    filters.append("[music]"+"".join(alabs)+f"amix=inputs={1+len(alabs)}:duration=longest:normalize=0,alimiter=limit=0.92,atrim=duration={DURATION}[mix]")
    cmd=[ff,"-y","-i",str(SILENT),"-i",str(SRC),"-filter_complex",";".join(filters),
         "-map","0:v:0","-map","[mix]","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",str(FINAL)]
    subprocess.run(cmd,check=True)


if __name__=="__main__":
    build_video(); mux(); print(FINAL)
