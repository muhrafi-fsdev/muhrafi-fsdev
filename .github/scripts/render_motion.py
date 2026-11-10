#!/usr/bin/env python3
"""Frame-rendered command-center animations for the GitHub profile.

The animation is drawn from discrete 25 FPS frames with independent lighting,
terminal activity, starfield, rocket exhaust and particles. No SVG transforms.
Outputs a high-quality animated WebP plus GIF fallback for each theme.
"""
from __future__ import annotations

import argparse
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = 1000
FPS_MS = 40
FRAMES = 80
OUT = Path("dist")
FONTPATHS = {
    "sans": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"],
    "bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf"],
    "mono": ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "DejaVuSansMono.ttf"],
}
THEMES = {
    "dark": {
        "bg": "#080D19", "panel": "#0D1829", "bar": "#121F32",
        "line": "#2B405C", "line2": "#1B2D44",
        "text": "#F4F8FF", "muted": "#ACBFD3", "dim": "#8198B2",
        "cyan": "#41D6EB", "violet": "#AB96FA", "green": "#51DAB8",
        "chip": "#142338", "flame": "#FFA14A",
    },
    "light": {
        "bg": "#F5F8FD", "panel": "#FFFFFF", "bar": "#E9F1F9",
        "line": "#B8CBDF", "line2": "#DFE8F2",
        "text": "#17283C", "muted": "#456079", "dim": "#667F97",
        "cyan": "#07829C", "violet": "#6654B2", "green": "#087D71",
        "chip": "#EDF4FB", "flame": "#EC7C28",
    },
}
ASCII_R = [
    "RRRRRRRRRRRR.", "RR::::::::::RR", "RR:::::::::::RR",
    "RR:::::RR:::::RR", "RR:::::R  RR::::R", "RR:::::R   RR:::R",
    "RR:::::RRRRR::::R", "RR::::::::::::RR", "RR::::::RR::::R",
    "RR:::::R  RR::::R", "RRRRRRR    RRRRRRR",
]
ROWS = [
    ("NAME", "Muhammad Rafi Priyo"),
    ("HANDLE", "@muhrafi-fsdev"),
    ("LOCATION", "Indonesia"),
    ("EDUCATION", "Telkom University"),
    ("ROLE", "Full-Stack Developer"),
    ("FOCUS", "Web / AI / IoT"),
    ("BUILDING", "NusaMind / NusaMonitor"),
    ("PORTFOLIO", "riyooprivateweb.my.id"),
]
FONT_CACHE = {}


def font(size: int, family: str = "sans"):
    key = (size, family)
    if key not in FONT_CACHE:
        for candidate in FONTPATHS[family]:
            try:
                FONT_CACHE[key] = ImageFont.truetype(candidate, size)
                break
            except OSError:
                pass
        else:
            raise RuntimeError(f"Missing font: {family}")
    return FONT_CACHE[key]


def rgb(hexcolor):
    return tuple(bytes.fromhex(hexcolor.lstrip("#")))


def glow_dot(im, point, color, intensity=1.0, radius=7):
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(overlay)
    r, g, b = rgb(color)
    x, y = point
    gd.ellipse((x-radius*2, y-radius*2, x+radius*2, y+radius*2),
               fill=(r, g, b, int(44 * intensity)))
    blur = overlay.filter(ImageFilter.GaussianBlur(8))
    im.alpha_composite(blur)
    dr = ImageDraw.Draw(im)
    dr.ellipse((x-radius/2, y-radius/2, x+radius/2, y+radius/2),
               fill=(r, g, b, int(180+70*intensity)))


def shell(im, t, height, terminal_title):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((3, 3, W-4, height-4), radius=17,
                        fill=t["bg"], outline=t["line"], width=2)
    d.rounded_rectangle((20, 18, W-21, 60), radius=9, fill=t["bar"])
    for cx, col in ((39, "#FB6862"), (56, "#FDBE4A"), (73, "#42C86E")):
        d.ellipse((cx-4, 35, cx+4, 43), fill=col)
    d.text((92, 30), terminal_title, font=font(14, "mono"), fill=t["muted"])
    d.line((20, 62, W-21, 62), fill=t["line"], width=1)


def text(d, xy, value, size, tcolor, family="sans", anchor=None):
    d.text(xy, value, font=font(size, family), fill=tcolor, anchor=anchor)


def hero_frame(theme, index):
    t = THEMES[theme]
    phase = index/FRAMES
    time = 2*math.pi*phase
    im = Image.new("RGBA", (W, 540), (0, 0, 0, 0))
    shell(im, t, 540, "muhrafi-fsdev  ~  ./profile.sh --live")
    d = ImageDraw.Draw(im)
    text(d, (25, 76), "IDENTITY.MAP", 13, t["muted"], "mono")
    text(d, (420, 76), "SYSTEM.INFO", 13, t["muted"], "mono")
    d.rounded_rectangle((22, 98, 407, 511), radius=12, fill=t["panel"], outline=t["line"], width=2)
    d.rounded_rectangle((418, 98, 976, 511), radius=12, fill=t["panel"], outline=t["line"], width=2)
    d.rounded_rectangle((39, 114, 390, 155), radius=9, fill=t["chip"])
    text(d, (53, 128), "ASCII_IDENTITY://RAFI", 14, t["cyan"], "mono")
    # The glyphs do not move: luminance flows gently through characters.
    for i, line in enumerate(ASCII_R):
        wave = (math.sin(time + i*0.46) + 1)/2
        if theme == "dark":
            color = (
                round(52 + 62*wave),
                round(181 + 33*wave),
                round(218 + 25*wave),
            )
        else:
            color = (11+int(23*wave), 102+int(27*wave), 141+int(29*wave))
        text(d, (62, 175+i*26), line, 20, color, "mono")
    # Independent light-trace: not a translation of the entire image.
    track_y = 178 + 262 * ((1-math.cos(time))/2)
    d.rounded_rectangle((48, track_y, 378, track_y+2), radius=1, fill=t["cyan"])
    d.line((48, 464, 378, 464), fill=t["line"])
    log = [
        "boot: workspace online",
        "sync: projects indexed",
        "edge: telemetry ready",
        "build: shipping ideas",
    ][(index//20) % 4]
    chars = 7+(index % 20)*2
    text(d, (50, 475), "> "+log[:chars] + ("_" if index % 12 < 6 else " "), 13, t["muted"], "mono")
    text(d, (50, 502), "LOCAL-FIRST / BUILD / REFINE", 11, t["dim"], "mono")
    # Real profile fields retain a fixed baseline to eliminate jitter.
    d.rounded_rectangle((433, 114, 963, 386), radius=9, fill=t["chip"], outline=t["line"])
    text(d, (452, 125), "// PROFILE.SYS", 14, t["cyan"], "mono")
    d.line((448, 151, 947, 151), fill=t["line"])
    for i, (label, value) in enumerate(ROWS):
        y=160+i*27
        text(d,(450,y),label,12,t["cyan"],"mono")
        text(d,(632,y-2),value,16,t["text"],"bold")
        if i<7:
            d.line((450,y+23,947,y+23),fill=t["line2"])
    text(d,(441,401),"PROFILE.SNAPSHOT",12,t["cyan"],"mono")
    for x,num,lab in [(508,"06","FEATURED"),(685,"03","FOCUS AREAS"),(867,"ID","INDONESIA")]:
        text(d,(x,418),num,23,t["text"],"bold")
        text(d,(x,451),lab,10,t["muted"],"mono")
    d.line((610,417,610,466),fill=t["line"])
    d.line((787,417,787,466),fill=t["line"])
    text(d,(440,475),"TOOLS / TECHNOLOGIES",11,t["cyan"],"mono")
    x=615
    for label,width in [("HTML",58),("CSS",51),("JS",42),("Python",79),("Docker",80)]:
        d.rounded_rectangle((x,473,x+width,499),radius=7,fill=t["chip"],outline=t["line"])
        text(d,(x+9,480),label,11,t["text"],"bold")
        x+=width+8
    # Three telemetry LEDs and a graph with sampled (not translated) activity.
    status=0.6+0.4*(math.sin(time)**2)
    for n in range(3):
        x=919+n*15
        c=t["green"] if n<2 else t["cyan"]
        d.ellipse((x,36,x+7,43),fill=c)
    bar_x=22
    for i in range(62):
        h=2+8*(0.5+0.5*math.sin(time*1.35+i*0.18))
        d.line((bar_x+i*9,529,bar_x+i*9,529-h),fill=t["line"],width=2)
    return im.convert("RGB")


def rocket_sprite(t, k):
    # Layered sprite rendered independently and gently rotated for life-like drift.
    spr=Image.new("RGBA",(150,250),(0,0,0,0))
    dr=ImageDraw.Draw(spr)
    x=75
    pulse=(math.sin(2*math.pi*k/13)+1)/2
    length=48+int(18*pulse)
    dr.polygon([(x-21,146),(x+21,146),(x+11,146+length),(x,158+length),(x-11,146+length)],
               fill="#FF9D42")
    dr.polygon([(x-13,146),(x+13,146),(x+7,146+length*.68),(x,160+length*.72),(x-7,146+length*.68)],
               fill="#FFE5AA")
    dr.polygon([(x-11,14),(x,0),(x+11,14)],fill=t["green"])
    dr.rounded_rectangle((x-23,18,x+23,123),radius=13,fill="#D9E2F1",outline="#8B9BB0",width=3)
    dr.rectangle((x-26,53,x-9,111), fill=t["cyan"])
    dr.rectangle((x+9,53,x+26,111), fill=t["violet"])
    dr.polygon([(x-24,95),(x-52,131),(x-17,122)],fill=t["cyan"])
    dr.polygon([(x+24,95),(x+52,131),(x+17,122)],fill=t["violet"])
    dr.rounded_rectangle((x-14,42,x+14,73),radius=8,fill="#102439",outline=t["cyan"],width=3)
    dr.ellipse((x-7,49,x+7,63),fill="#187A97")
    dr.rectangle((x-18,123,x+18,144),fill="#AFC3DC")
    angle=1.4*math.sin(2*math.pi*k/FRAMES)
    return spr.rotate(angle,resample=Image.Resampling.BICUBIC,expand=False)


def rocket_frame(theme, index):
    t=THEMES[theme]
    phase=index/FRAMES
    time=2*math.pi*phase
    im=Image.new("RGBA",(W,326),(0,0,0,0))
    shell(im,t,326,"mission-control://muhrafi-fsdev")
    d=ImageDraw.Draw(im)
    text(d,(39,85),"LAUNCH.SEQUENCE",15,t["cyan"],"mono")
    text(d,(37,117),"Building Ideas Into Production",29,t["text"],"bold")
    text(d,(39,159),"Full-stack  /  Local AI  /  Web platforms  /  IoT",15,t["muted"])
    for x,title,value,color in [(39,"CURRENT BUILD","NusaMind Systems",t["green"]),(289,"NEXT MILESTONE","NusaMonitor ID",t["violet"])]:
        d.rounded_rectangle((x,193,x+234,280),radius=10,fill=t["panel"],outline=t["line"],width=2)
        d.rounded_rectangle((x+13,211,x+17,264),radius=2,fill=color)
        text(d,(x+28,209),title,11,t["muted"],"mono")
        text(d,(x+28,240),value,16,t["text"],"bold")
    # Starfield: each point has its own luminance and slight parallax.
    rng=random.Random(2048)
    for i in range(36):
        x=rng.randint(577,966)
        y=rng.randint(85,288)
        offset=rng.random()*math.tau
        amp=(math.sin(time*1.2+offset)+1)/2
        rad=1+(i%7==0)
        color=t["cyan"] if i%4==0 else t["dim"]
        if amp>.30:
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=color)
    # Exhaust particles are individually regenerated each frame.
    for i in range(23):
        seed=(i*0.6180339887)%1
        progress=(phase*1.8+seed)%1
        spread=15+58*progress
        px=791+math.sin(i*2.31+phase*4)*spread
        py=219+progress*104
        size=max(1,4-int(3*progress))
        color=["#FFB353","#F97940","#9F94EE","#45D9E7"][i%4]
        d.ellipse((px-size,py-size,px+size,py+size),fill=color)
    # Semi-transparent animated vapor, not a translated single SVG.
    smoke=Image.new("RGBA",im.size,(0,0,0,0))
    sd=ImageDraw.Draw(smoke)
    for j in range(9):
        progress=(phase*1.4+j/9)%1
        px=790+math.sin(j*2.9)*24*(progress+.2)
        py=250+progress*69
        radius=7+13*progress
        r,g,b=rgb(t["violet"])
        sd.ellipse((px-radius,py-radius,px+radius,py+radius),fill=(r,g,b,int((1-progress)*36)))
    im.alpha_composite(smoke.filter(ImageFilter.GaussianBlur(5)))
    bob=int(7*math.sin(time))
    sprite=rocket_sprite(t,index)
    im.alpha_composite(sprite,(714,71+bob))
    text(d,(963,307),"BUILD / TEST / REFINE",11,t["dim"],"mono",anchor="ra")
    return im.convert("RGB")


def save_animation(mode: str, name: str, build):
    frames=[build(mode,k) for k in range(FRAMES)]
    # Quality-first animated WebP; cross-browser GIF fallback.
    webp=OUT/f"{name}-{mode}.webp"
    gif=OUT/f"{name}-{mode}.gif"
    frames[0].save(
        webp,format="WEBP",save_all=True,append_images=frames[1:],
        duration=FPS_MS,loop=0,quality=80,method=4,
    )
    palette=frames[0].quantize(colors=128,dither=Image.Dither.NONE)
    gifs=[frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
    gifs[0].save(
        gif,format="GIF",save_all=True,append_images=gifs[1:],
        duration=FPS_MS,loop=0,optimize=True,disposal=2,
    )
    print(f"{webp}: {webp.stat().st_size:,} bytes; {gif}: {gif.stat().st_size:,} bytes",flush=True)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--theme",choices=["dark","light","all"],default="all")
    parser.add_argument("--frames",type=int,default=80)
    args=parser.parse_args()
    global FRAMES
    FRAMES=args.frames
    if not 12 <= FRAMES <= 120:
        raise ValueError("frames must be between 12 and 120")
    OUT.mkdir(parents=True,exist_ok=True)
    modes=["dark","light"] if args.theme=="all" else [args.theme]
    for mode in modes:
        save_animation(mode,"command-center",hero_frame)
        save_animation(mode,"rocket-launch",rocket_frame)


if __name__=="__main__":
    main()
