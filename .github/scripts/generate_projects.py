#!/usr/bin/env python3
import json
import math
import os
import sys
from html import escape

W, MARGIN, GAP, CARD_W, CARD_H = 1180, 24, 16, 558, 170

THEMES = {
    "dark": {"bg":"#070B16","panel":"#0A101F","bar":"#0B1222","text":"#F8FAFC","muted":"#94A3B8","dim":"#475569","line":"rgba(255,255,255,0.10)"},
    "light": {"bg":"#F5F7FB","panel":"#FFFFFF","bar":"#EEF2F7","text":"#0F172A","muted":"#475569","dim":"#94A3B8","line":"rgba(15,23,42,0.10)"}
}
LANG_COLORS = {"TypeScript":"#3178C6","JavaScript":"#F1E05A","Python":"#3572A5","CSS":"#663399","HTML":"#E34C26","Shell":"#89E051"}

def build(items, theme):
    c = THEMES[theme]
    rows = math.ceil(len(items)/2)
    height = 58 + rows*(CARD_H+GAP) + 18
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="Featured projects">
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7C3AED"/><stop offset=".5" stop-color="#22D3EE"/><stop offset="1" stop-color="#10B981"/></linearGradient>
<style>.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.sans{{font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}</style></defs>
<rect width="{W}" height="{height}" fill="{c["bg"]}"/>
<text x="{MARGIN}" y="20" font-size="11" letter-spacing="2" fill="#22D3EE" class="mono">PROJECTS.LIST</text>
<text x="{MARGIN+130}" y="20" font-size="10" fill="{c["dim"]}" class="mono">./projects.sh --featured</text>
<line x1="{MARGIN}" y1="32" x2="{W-MARGIN}" y2="32" stroke="url(#accent)" stroke-width="1.5"/>''']

    for i, p in enumerate(items):
        x = MARGIN + (i%2)*(CARD_W+GAP)
        y = 48 + (i//2)*(CARD_H+GAP)
        accent = p.get("accent","#22D3EE")
        out.append(f'''<a href="https://github.com/{escape(p["repo"])}" target="_blank"><g transform="translate({x},{y})">
<rect width="{CARD_W}" height="{CARD_H}" rx="12" fill="{c["panel"]}" stroke="{c["line"]}"/>
<rect width="{CARD_W}" height="31" rx="12" fill="{c["bar"]}"/><rect y="18" width="{CARD_W}" height="13" fill="{c["bar"]}"/>
<line x1="0" y1="31" x2="{CARD_W}" y2="31" stroke="{c["line"]}"/>
<circle cx="17" cy="15.5" r="4" fill="{accent}"/>
<text x="29" y="20" font-size="10" fill="{c["muted"]}" class="mono">{escape(p["repo"])}</text>
<circle cx="{CARD_W-17}" cy="15.5" r="3.5" fill="#10B981"/>
<rect x="17" y="47" width="42" height="42" rx="10" fill="{accent}" opacity=".16" stroke="{accent}"/>
<text x="38" y="75" text-anchor="middle" font-size="20" font-weight="800" fill="{accent}" class="sans">{escape(p["name"][:1])}</text>
<text x="72" y="60" font-size="17" font-weight="800" fill="{c["text"]}" class="sans">{escape(p["name"])}</text>
<text x="72" y="82" font-size="10.5" fill="{c["muted"]}" class="sans">{escape(p.get("description","")[:82])}</text>''')
        tx = 72
        for tag in p.get("tags",[])[:3]:
            tw = max(48, len(tag)*6.4+18)
            out.append(f'<rect x="{tx}" y="102" width="{tw}" height="19" rx="9.5" fill="{accent}" opacity=".12" stroke="{accent}" stroke-opacity=".55"/>')
            out.append(f'<text x="{tx+tw/2}" y="115" text-anchor="middle" font-size="9" fill="{accent}" class="sans">{escape(tag)}</text>')
            tx += tw+7
        out.append(f'<text x="72" y="148" font-size="10" fill="{c["muted"]}" class="mono"><tspan fill="#22D3EE">★</tspan> {p.get("stars",0)} <tspan dx="16" fill="#A78BFA">⑂</tspan> {p.get("forks",0)}</text>')
        langs = p.get("languages",{})
        if langs:
            total = sum(langs.values()) or 1
            cursor = CARD_W-150
            for lang, amount in sorted(langs.items(), key=lambda x:x[1], reverse=True)[:4]:
                seg = 120*amount/total
                out.append(f'<rect x="{cursor}" y="139" width="{seg:.1f}" height="6" fill="{LANG_COLORS.get(lang,"#94A3B8")}"/>')
                cursor += seg
        out.append("</g></a>")
    out.append("</svg>")
    return "".join(out)

if __name__ == "__main__":
    source = sys.argv[1] if len(sys.argv)>1 else "merged.json"
    outdir = sys.argv[2] if len(sys.argv)>2 else "."
    with open(source, encoding="utf-8") as handle:
        items = json.load(handle)
    os.makedirs(outdir, exist_ok=True)
    for theme, filename in (("dark","projects.svg"),("light","projects-light.svg")):
        with open(os.path.join(outdir,filename),"w",encoding="utf-8") as handle:
            handle.write(build(items,theme))
