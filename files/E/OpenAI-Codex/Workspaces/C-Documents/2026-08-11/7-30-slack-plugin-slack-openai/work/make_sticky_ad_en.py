from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio.v2 as imageio
import imageio_ffmpeg
import math, os, wave, subprocess

W,H,FPS,DUR=720,1280,30,25
ROOT=r"C:\Users\24243\Documents\Codex\2026-08-11\7-30-slack-plugin-slack-openai"
OUT=os.path.join(ROOT,"outputs"); os.makedirs(OUT,exist_ok=True)
SRC=Image.open(r"E:\Desktop\L1310466.png").convert("RGB")
PEEL=Image.open(os.path.join(ROOT,"work","assets_v2","hand_peel.png")).convert("RGB")
WRITE=Image.open(os.path.join(ROOT,"work","assets_v2","hand_write.png")).convert("RGB")
PLACE=Image.open(os.path.join(ROOT,"work","assets_v2","hand_place.png")).convert("RGB")
SILENT=os.path.join(ROOT,"work","sticky_ad_en_silent.mp4")
WAV=os.path.join(ROOT,"work","sticky_ad_en_audio.wav")
FINAL=os.path.join(OUT,"Hanlin_Paper_Sticky_Notes_English_25s.mp4")
POSTER=os.path.join(OUT,"Hanlin_Paper_Sticky_Notes_English_Cover.jpg")
FONT_B=r"C:\Windows\Fonts\arialbd.ttf"; FONT_R=r"C:\Windows\Fonts\arial.ttf"

def f(sz,b=True): return ImageFont.truetype(FONT_B if b else FONT_R,sz)
def cl(x,a=0,b=1): return max(a,min(b,x))
def ease(x): x=cl(x); return x*x*(3-2*x)
def cover(im,size,zoom=1.0,panx=.5,pany=.5):
    sw,sh=im.size; tw,th=size; s=max(tw/sw,th/sh)*zoom
    r=im.resize((int(sw*s),int(sh*s)),Image.Resampling.LANCZOS)
    x=int((r.width-tw)*cl(panx)); y=int((r.height-th)*cl(pany))
    return r.crop((x,y,x+tw,y+th))
def contain(im,size):
    tw,th=size; sw,sh=im.size; s=min(tw/sw,th/sh)
    r=im.resize((int(sw*s),int(sh*s)),Image.Resampling.LANCZOS)
    out=Image.new("RGB",size,(255,255,255)); out.paste(r,((tw-r.width)//2,(th-r.height)//2))
    return out
def txt_center(d,y,text,fs,fill=(255,255,255,255),stroke=0,stroke_fill=(0,0,0,150)):
    ft=f(fs,True); bb=d.textbbox((0,0),text,font=ft,stroke_width=stroke)
    x=(W-(bb[2]-bb[0]))/2
    d.text((x,y),text,font=ft,fill=fill,stroke_width=stroke,stroke_fill=stroke_fill)
def top_overlay(im,kicker,title,sub=None,dark=False):
    ov=Image.new("RGBA",im.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
    od.rectangle((0,0,W,310),fill=(255,255,255,225) if not dark else (20,24,30,210))
    od.rounded_rectangle((40,44,220,86),radius=21,fill=(255,223,48,255))
    od.text((63,53),kicker,font=f(20,True),fill=(28,31,37,255))
    col=(26,30,36,255) if not dark else (255,255,255,255)
    txt_center(od,112,title,52,col)
    if sub: txt_center(od,184,sub,23,(78,83,91,255) if not dark else (225,228,232,255))
    ov=ov.filter(ImageFilter.GaussianBlur(0.1)); im.alpha_composite(ov)
def badge(im,y,text,accent=(255,222,45,255)):
    d=ImageDraw.Draw(im); ft=f(23,True); bb=d.textbbox((0,0),text,font=ft)
    ww=bb[2]-bb[0]+46; x=(W-ww)/2
    d.rounded_rectangle((x,y,x+ww,y+54),radius=27,fill=(23,27,33,225))
    d.ellipse((x+13,y+17,x+33,y+37),fill=accent)
    d.text((x+42,y+13),text,font=ft,fill=(255,255,255,255))
def brand_bug(im):
    d=ImageDraw.Draw(im); d.rounded_rectangle((24,1214,220,1252),radius=18,fill=(255,255,255,205))
    d.text((40,1222),"HANLIN PAPER",font=f(17,True),fill=(31,34,40,255))

COL=[(255,226,46,255),(255,103,145,255),(44,184,233,255),(163,218,66,255),(255,137,43,255),(136,104,203,255)]
def note(im,x,y,c,sz=88,angle=0,alpha=255):
    lay=Image.new("RGBA",(sz+24,sz+24),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((8,12,8+sz,12+sz),radius=5,fill=(20,25,30,45))
    d.rectangle((8,8,8+sz,8+sz),fill=c[:3]+(alpha,))
    if angle: lay=lay.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    im.alpha_composite(lay,(int(x-lay.width/2),int(y-lay.height/2)))

def frame(t):
    # 0-3.2: real product intro
    if t<3.2:
        u=ease(t/3.2)
        crop=SRC.crop((0,310,SRC.width,SRC.height))
        bg=cover(crop,(W,H),1.02+.05*u,.5,.50).filter(ImageFilter.GaussianBlur(1.2)).convert("RGBA")
        wash=Image.new("RGBA",(W,H),(255,255,255,190)); bg.alpha_composite(wash)
        d=ImageDraw.Draw(bg)
        d.rounded_rectangle((52,292,668,1045),radius=34,fill=(255,255,255,245),outline=(235,236,237,255),width=2)
        hero=cover(crop,(560,610),1.0,.5,.60).convert("RGBA")
        bg.alpha_composite(hero,(80,345))
        d=ImageDraw.Draw(bg)
        d.rounded_rectangle((210,78,510,126),radius=24,fill=(255,224,42,255))
        txt_center(d,88,"HANLIN PAPER",24,(28,31,37,255))
        txt_center(d,155,"COLOR YOUR IDEAS",49,(26,29,35,255))
        txt_center(d,222,"16 colors. One bright day.",24,(81,85,91,255))
        badge(bg,1110,"BRIGHT. BOLD. READY.")
        return bg.convert("RGB")

    # 3.2-7.4: hand writing
    if t<7.4:
        u=(t-3.2)/4.2
        bg=cover(WRITE,(W,H),1.02+.045*ease(u),.48,.50-.04*u).convert("RGBA")
        top_overlay(bg,"WRITE","SMOOTH WRITING","Clean lines. Easy flow.")
        # animated underline echoes pen movement
        d=ImageDraw.Draw(bg); q=ease(cl((u-.25)/.5))
        d.line((140,1000,140+440*q,1000),fill=(255,222,44,255),width=8)
        badge(bg,1070,"CLEAR & SMUDGE-RESISTANT")
        brand_bug(bg); return bg.convert("RGB")

    # 7.4-13.4: peel then re-stick through photo transition
    if t<13.4:
        u=(t-7.4)/6
        if u<.55:
            v=u/.55
            bg=cover(PEEL,(W,H),1.0+.055*ease(v),.50,.52-.04*v).convert("RGBA")
            top_overlay(bg,"PEEL","PEEL OFF SMOOTHLY","Lift the whole note. No curl.")
            # motion arrow
            d=ImageDraw.Draw(bg); q=ease(cl((v-.12)/.75))
            d.arc((310,560,650,920),145,145+130*q,fill=(255,218,32,255),width=10)
            badge(bg,1085,"CLEAN REMOVAL")
        else:
            v=(u-.55)/.45
            bg=cover(PLACE,(W,H),1.055-.045*ease(v),.50,.48).convert("RGBA")
            top_overlay(bg,"RESTICK","PRESS. PLACE. RESTICK.","Strong hold, again and again.")
            d=ImageDraw.Draw(bg); q=ease(cl(v/.55))
            d.ellipse((321-35*q,712-35*q,321+35*q,712+35*q),outline=(255,222,38,int(220*(1-q))),width=9)
            badge(bg,1085,"REPEATABLE ADHESIVE")
        brand_bug(bg); return bg.convert("RGB")

    # 13.4-18.5: glass / colorful arrangement
    if t<18.5:
        u=(t-13.4)/5.1
        bg=cover(PLACE,(W,H),1.03+.035*ease(u),.5,.47).convert("RGBA")
        top_overlay(bg,"CREATE","FLAT. FIRM. FUN.","Every color stays perfectly in place.")
        d=ImageDraw.Draw(bg)
        # sparkle accents, upbeat and clean
        for i,(x,y) in enumerate([(90,430),(624,500),(105,1000),(620,945)]):
            q=ease(cl((u-i*.08)/.32)); rr=18*q
            d.line((x-rr,y,x+rr,y),fill=(255,222,38,210),width=5)
            d.line((x,y-rr,x,y+rr),fill=(255,222,38,210),width=5)
        badge(bg,1085,"FLAT, EDGE TO EDGE")
        brand_bug(bg); return bg.convert("RGB")

    # 18.5-22.2: animated color burst + product
    if t<22.2:
        u=(t-18.5)/3.7
        bg=Image.new("RGBA",(W,H),(249,249,245,255)); d=ImageDraw.Draw(bg)
        d.ellipse((-180,-150,330,350),fill=(255,226,42,255)); d.ellipse((500,1030,850,1380),fill=(255,103,145,255))
        txt_center(d,88,"16 COLORS",62,(27,30,36,255)); txt_center(d,165,"ENDLESS IDEAS",42,(27,30,36,255))
        pts=[(140,390,-10),(360,340,5),(580,410,10),(155,650,7),(360,620,-6),(565,680,-10),(245,895,8),(475,900,-4)]
        for i,(x,y,a) in enumerate(pts):
            q=ease(cl((u*1.3-i*.07)/.28)); note(bg,x,y,COL[i%6],126,a,int(255*q))
        badge(bg,1075,"MIX. MATCH. MAKE IT YOURS.")
        brand_bug(bg); return bg.convert("RGB")

    # 22.2-25: end card
    u=ease((t-22.2)/2.8)
    bg=Image.new("RGBA",(W,H),(247,247,243,255)); d=ImageDraw.Draw(bg)
    d.ellipse((-220,-240,430,420),fill=(255,226,42,255)); d.ellipse((480,950,900,1370),fill=(255,103,145,255))
    txt_center(d,115,"HANLIN PAPER",58,(25,28,34,255))
    txt_center(d,193,"STICK WITH YOUR IDEAS",32,(66,70,78,255))
    prod=contain(SRC,(610,550)).convert("RGBA")
    card=Image.new("RGBA",(640,590),(255,255,255,245)); card.alpha_composite(prod,(15,20))
    card=card.resize((int(card.width*(.88+.12*u)),int(card.height*(.88+.12*u))),Image.Resampling.LANCZOS)
    bg.alpha_composite(card,((W-card.width)//2,330))
    for i,x in enumerate([108,205,302,399,496,593]): note(bg,x,1010,COL[i],76,-6+i*2)
    badge(bg,1100,"PEEL. WRITE. RESTICK.")
    return bg.convert("RGB")

def make_audio():
    sr=48000; n=sr*DUR; rng=np.random.default_rng(31415); x=np.zeros(n)
    bpm=116; beat=60/bpm
    # bright original synth-pop bed: bass, plucks, hats, claps
    chords=[[261.63,329.63,392.00],[220.00,261.63,329.63],[174.61,220.00,261.63],[196.00,246.94,293.66]]
    for bar in range(int(DUR/(beat*4))+1):
        st=bar*beat*4; chord=chords[bar%4]
        for k in range(8):
            s=int((st+k*beat/2)*sr)
            if s>=n: continue
            m=min(int(.34*sr),n-s); tt=np.arange(m)/sr; env=np.exp(-tt*7)
            for fr in chord: x[s:s+m]+=.018*np.sin(2*np.pi*fr*tt)*env
        # bass roots
        for k in range(4):
            s=int((st+k*beat)*sr); m=min(int(.28*sr),n-s)
            if m>0:
                tt=np.arange(m)/sr; x[s:s+m]+=.05*np.sin(2*np.pi*(chord[0]/2)*tt)*np.exp(-tt*5)
    # percussion
    for k in range(int(DUR/beat*2)):
        st=k*beat/2; s=int(st*sr); m=min(int(.08*sr),n-s)
        if m>0: x[s:s+m]+=.012*rng.normal(size=m)*np.exp(-np.arange(m)/(sr*.018))
    for k in range(1,int(DUR/beat),2):
        s=int(k*beat*sr); m=min(int(.13*sr),n-s)
        if m>0: x[s:s+m]+=.028*rng.normal(size=m)*np.exp(-np.arange(m)/(sr*.03))
    # tactile details
    for st in [7.8,10.4,11.1]:
        s=int(st*sr); m=min(int(.45*sr),n-s); env=np.sin(np.pi*np.arange(m)/m)**2
        x[s:s+m]+=.035*rng.normal(size=m)*env
    s=int(4.2*sr); m=int(2.5*sr); x[s:s+m]+=.008*rng.normal(size=m)*(.5+.5*np.sin(2*np.pi*7*np.arange(m)/sr))
    # final happy chime
    for st,fr in [(22.3,659.25),(22.52,783.99),(22.74,987.77)]:
        s=int(st*sr); m=min(int(.9*sr),n-s); tt=np.arange(m)/sr
        x[s:s+m]+=.075*np.sin(2*np.pi*fr*tt)*np.exp(-tt*4)
    x=np.tanh(x*1.35); pcm=(x*32767).astype('<i2')
    with wave.open(WAV,'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(np.repeat(pcm[:,None],2,axis=1).tobytes())

def main():
    wr=imageio.get_writer(SILENT,fps=FPS,codec='libx264',quality=8,pixelformat='yuv420p',macro_block_size=None)
    poster=None
    for i in range(FPS*DUR):
        fr=frame(i/FPS); wr.append_data(np.asarray(fr))
        if i==682: poster=fr.copy()
    wr.close(); poster.save(POSTER,quality=94)
    make_audio(); ff=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff,'-y','-i',SILENT,'-i',WAV,'-c:v','copy','-c:a','aac','-b:a','192k','-shortest',FINAL],check=True)
    print(FINAL)

if __name__=='__main__': main()
