#!/usr/bin/env python3
"""Render the Signal Lab profile banner.

Run from the repository root with Python 3.10+, Pillow with WebP support,
and the DejaVu Sans and DejaVu Sans Mono fonts (fonts-dejavu-core on Debian):
  python3 scripts/render_signal_banner.py
"""
from __future__ import annotations

from functools import lru_cache
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

WIDTH, HEIGHT = 1000, 354
FRAME_MS = 40
FRAME_COUNT = 100
OUT = Path(__file__).resolve().parents[1] / "assets" / "signal-lab"
PALETTES = {
    "dark": {
        "sky": ("#101626", "#3b3e64", "#bf8296"),
        "back": "#30364e", "mid": "#242e44", "front": "#151e30", "edge": "#535d79",
        "line": "#252f43", "panel": "#101626", "headline": "#f7f1e4",
        "muted": "#b0bcd1", "accent": "#ffd2a0", "signal": "#b0e2e3",
        "tower": "#203047", "tower_edge": "#9db6c4",
    },
    "light": {
        "sky": ("#eee8df", "#dad4e4", "#d5a69c"),
        "back": "#968eae", "mid": "#7a7b9c", "front": "#575d7f", "edge": "#a3a1c2",
        "line": "#d7ccce", "panel": "#f1e8e2", "headline": "#27273f",
        "muted": "#565670", "accent": "#86482f", "signal": "#30616e",
        "tower": "#f3e8d8", "tower_edge": "#3b415e",
    },
}
X, Y = 766, 184
PULSE_BOX = (620, 54, 912, 186)
PULSE_SCALE = 3


@lru_cache
def font(size: int, face: str) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(f"DejaVu{face}.ttf", size)


def rgb(value: str) -> tuple[int, int, int]:
    return ImageColor.getrgb(value)


def mix(a, b, amount):
    return tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


def terrain(draw, points, fill, edge=None):
    draw.polygon([*points, (WIDTH, HEIGHT), (0, HEIGHT)], fill=fill)
    if edge:
        draw.line(points, fill=edge, width=1)


def backdrop(p):
    im = Image.new("RGB", (WIDTH, HEIGHT))
    sky, dusk, horizon = map(rgb, p["sky"])
    panel = rgb(p["panel"])
    # A 2-D fade keeps the text clear while the right side opens to the horizon.
    fades = [max(0, min(1, (x - 436) / 350)) for x in range(WIDTH)]
    pixels = []
    for y in range(HEIGHT):
        row = mix(sky, dusk, y / 185) if y < 185 else mix(dusk, horizon, (y - 185) / 168)
        pixels.extend(mix(panel, row, a * a * (3 - 2 * a)) for a in fades)
    im.putdata(pixels)
    d = ImageDraw.Draw(im)
    for x, y, length in (
        (577, 122, 48), (610, 108, 98), (697, 96, 27), (806, 125, 47),
        (838, 136, 47), (892, 121, 80), (928, 179, 55), (644, 196, 41),
    ):
        d.line((x, y, x + length, y), fill=mix(im.getpixel((x, y)), rgb(p["accent"]), .25))
    glow = (878, 197)
    d.ellipse((glow[0] - 32, glow[1] - 32, glow[0] + 32, glow[1] + 32),
              fill=mix(rgb(p["sky"][2]), (255, 231, 206), .43))

    panels = [
        ([(444, 269), (510, 257), (560, 237), (597, 243), (641, 223), (668, 226),
          (696, 209), (716, 215), (750, 235), (779, 231), (803, 218), (833, 240),
          (864, 227), (883, 222), (909, 238), (963, 220), (1000, 231)], "back"),
        ([(430, 286), (500, 283), (557, 269), (594, 252), (628, 260), (673, 249),
          (701, 266), (757, 245), (786, 252), (809, 248), (847, 275), (908, 262),
          (932, 250), (975, 259), (1000, 248)], "mid"),
        ([(410, 315), (475, 312), (534, 295), (579, 306), (618, 293), (658, 299),
          (692, 278), (721, 266), (748, 267), (773, 263), (795, 271), (827, 276),
          (854, 291), (880, 288), (913, 304), (946, 290), (978, 298), (1000, 289)], "front"),
    ]
    for points, key in panels:
        terrain(d, points, p[key], mix(rgb(p[key]), rgb(p["edge"]), .63))

    # Contour marks follow the foreground ridge instead of covering the typography.
    for i in range(7):
        y = 314 + i * 6
        points = [(x, y + round(8 * sin(x / 50 + i * .10) + 3 * sin(x / 17)))
                  for x in range(525 + i * 10, 987, 4)]
        d.line(points, fill=mix(rgb(p["front"]), rgb(p["edge"]), .31 if i % 2 else .48))
    return im


def station(d, p):
    d.line((716, 269, 744, 269, 746, 261, 786, 261, 790, 269, 811, 269),
           fill=p["tower_edge"], width=2)
    d.polygon([(752, 264), (762, 204), (771, 204), (784, 264)], fill=p["tower"],
              outline=p["tower_edge"], width=2)
    d.line((758, 226, 774, 226, 755, 250, 780, 250, 759, 226, 777, 238, 756, 238),
           fill=p["tower_edge"], width=1)
    d.line((X, 203, X, 170), fill=p["tower_edge"], width=3)
    d.line((746, 200, 786, 200), fill=p["tower_edge"], width=2)
    for x, y in [(745, 200), (786, 200), (760, 211), (773, 211), (X, 176)]:
        d.rectangle((x - 2, y - 1, x + 2, y + 1), fill=p["accent"])


def labels(d, p):
    def label(x, y, value, size, face, color, anchor="lt"):
        d.text((x, y), value, font=font(size, face), fill=p[color], anchor=anchor)

    d.rectangle((44, 40, 51, 47), fill=p["accent"])
    label(64, 37, "PERSONAL BUILD LOG  /  ID", 15, "SansMono", "accent")
    d.line((44, 68, 491, 68), fill=p["line"])
    label(39, 104, "Signal Lab", 82, "Sans-Bold", "headline")
    label(45, 204, "WEB  /  LOCAL AI  /  TELECOM", 21, "SansMono", "muted")
    d.line((44, 252, 491, 252), fill=p["line"])
    label(44, 278, "@muhrafi-fsdev", 21, "SansMono", "headline")
    label(964, 36, "RF / 01", 15, "SansMono", "muted", anchor="rt")
    d.line((918, 64, 963, 64, 963, 76), fill=p["tower_edge"])
    d.line((44, 324, 95, 324), fill=p["accent"], width=2)


def animation(base, p, frame):
    im = base.copy()
    d = ImageDraw.Draw(im)
    phase = frame / FRAME_COUNT
    left, top, right, bottom = PULSE_BOX
    size = (right - left, bottom - top)
    scale = PULSE_SCALE
    pulse_color = rgb(p["signal"])
    mask = Image.new("L", (size[0] * scale, size[1] * scale))
    strokes = ImageDraw.Draw(mask)
    for run, offset in enumerate((0, .25, .5, .75)):
        age = (phase + offset) % 1
        radius = 13 + 125 * age
        intensity = sin(pi * age) ** 1.15
        steps = 44
        points = [(round((X - left + radius * cos(pi * (1.13 + .74 * j / steps))) * scale),
                   round((Y - top + radius * .86 * sin(pi * (1.13 + .74 * j / steps))) * scale))
                  for j in range(steps + 1)]
        for j, (a, b) in enumerate(zip(points, points[1:])):
            taper = sin(pi * (j + 1) / (steps + 1)) ** .48
            opacity = round((228 if run % 2 == 0 else 184) * taper * intensity)
            strokes.line((a, b), fill=opacity, width=5)
    im.paste(pulse_color, (left, top, right, bottom), mask.resize(size, Image.Resampling.LANCZOS))
    for i, (x, y) in enumerate([(829, 100), (700, 125), (889, 88), (643, 158), (917, 143)]):
        luma = .20 + .55 * (.5 + .5 * sin(2 * pi * (phase + i * .14)))
        c = mix(base.getpixel((x, y)), rgb(p["accent"]), luma)
        d.line((x - 2, y, x + 2, y), fill=c)
        d.line((x, y - 2, x, y + 2), fill=c)
    d.ellipse((X - 3, 168, X + 3, 174),
              fill=mix(rgb(p["tower_edge"]), rgb(p["accent"]), .5 + .5 * cos(phase * 4 * pi)))
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, palette in PALETTES.items():
        base = backdrop(palette)
        painter = ImageDraw.Draw(base)
        station(painter, palette)
        labels(painter, palette)
        frames = [animation(base, palette, frame) for frame in range(FRAME_COUNT)]
        frames[0].save(OUT / f"signal-{theme}-still.webp", quality=88, method=6)
        frames[0].save(OUT / f"signal-{theme}.webp", save_all=True, append_images=frames[1:],
                       duration=FRAME_MS, loop=0, lossless=True, quality=90, method=5, minimize_size=True)


if __name__ == "__main__":
    main()
