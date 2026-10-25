#!/usr/bin/env python3
"""Generate the neon SVGs for the GitHub profile README.

Text is converted to glyph outlines (Orbitron / JetBrains Mono / Space Grotesk,
all SIL OFL) so the SVGs render identically inside <img> tags, where web fonts
cannot load. Animations use CSS inside the SVG and respect prefers-reduced-motion.

    pip install fonttools && python scripts/build_svgs.py
"""
import os, urllib.request
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")
FONT_DIR = os.environ.get("FONT_DIR", os.path.join(HERE, ".fonts"))
FONTS = {
    "orb": ("Orbitron[wght].ttf", "ofl/orbitron/Orbitron%5Bwght%5D.ttf"),
    "mono": ("JetBrainsMono[wght].ttf", "ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf"),
    "sans": ("SpaceGrotesk[wght].ttf", "ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"),
}
C = {"cyan": "#19f0ff", "magenta": "#ff2fd2", "lime": "#b8ff3c", "violet": "#a46bff", "amber": "#ffb020", "blue": "#3d8bff"}
BG = "#05060b"


def font_path(key):
    name, url = FONTS[key]
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        os.makedirs(FONT_DIR, exist_ok=True)
        urllib.request.urlretrieve("https://raw.githubusercontent.com/google/fonts/main/" + url, p)
    return p


class Face:
    """One font at one weight; emits <use> glyph references and the matching <defs>."""
    def __init__(self, key, wght, tag):
        f = instantiateVariableFont(TTFont(font_path(key)), {"wght": wght})
        self.gs, self.cmap = f.getGlyphSet(), f.getBestCmap()
        self.upm, self.hmtx, self.tag, self.used = f["head"].unitsPerEm, f["hmtx"], tag, set()

    def _gid(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))

    def width(self, s, size, ls=0):
        sc = size / self.upm
        return sum(self.hmtx[self._gid(ch)][0] for ch in s) * sc + ls * max(0, len(s) - 1)

    def text(self, s, x, y, size, anchor="start", ls=0, attrs=""):
        sc = size / self.upm
        w = self.width(s, size, ls)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        out, cur = [], 0.0
        for ch in s:
            g = self._gid(ch)
            if ch != " ":
                self.used.add(g)
                out.append('<use href="#%s-%s" x="%.0f"/>' % (self.tag, g, cur))
            cur += self.hmtx[g][0] + ls / sc
        return '<g transform="translate(%.1f %.1f) scale(%.5f %.5f)" %s>%s</g>' % (x0, y, sc, -sc, attrs, "".join(out))

    def defs(self):
        res = []
        for g in sorted(self.used):
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(pen)
            res.append('<path id="%s-%s" d="%s"/>' % (self.tag, g, pen.getCommands()))
        self.used = set()
        return "".join(res)


ORB = Face("orb", 900, "o")
ORB8 = Face("orb", 700, "p")
MONO = Face("mono", 500, "m")
MONOB = Face("mono", 700, "b")
SANS = Face("sans", 500, "s")
FACES = [ORB, ORB8, MONO, MONOB, SANS]

COMMON_STYLE = """
.pulse{fill:none;stroke-linecap:round;stroke-dasharray:60 940;animation:flow 2.8s linear infinite}
.spark{fill:none;stroke:#fff;stroke-linecap:round;stroke-width:2;stroke-dasharray:22 978;animation:flow2 2.8s linear infinite}
@keyframes flow{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}
@keyframes flow2{from{stroke-dashoffset:1019}to{stroke-dashoffset:19}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.pulse,.spark{display:none}}
"""


def glow_filter(fid, std=4, strength=1):
    merge = "".join('<feMergeNode in="b"/>' for _ in range(strength))
    return ('<filter id="%s" x="-30%%" y="-60%%" width="160%%" height="220%%">'
            '<feGaussianBlur in="SourceGraphic" stdDeviation="%s" result="b"/>'
            '<feMerge>%s<feMergeNode in="SourceGraphic"/></feMerge></filter>') % (fid, std, merge)


def grid_defs(pid="grid", step=20):
    return ('<pattern id="%s" width="%d" height="%d" patternUnits="userSpaceOnUse">'
            '<path d="M%d 0H0V%d" fill="none" stroke="#7d86ff" stroke-opacity=".09" stroke-width="1"/></pattern>') % (pid, step, step, step, step)


def trace(d, color, delay=0.0, dur=2.8, base_op=.3, width=2, pads=(), spark=True):
    s = ['<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s" stroke-linejoin="round"/>' % (d, color, base_op, width)]
    s.append('<path d="%s" class="pulse" pathLength="1000" stroke="%s" stroke-width="%s" stroke-opacity=".9" filter="url(#soft)" style="animation-delay:%.2fs;animation-duration:%.2fs"/>' % (d, color, width + 3, delay, dur))
    if spark:
        s.append('<path d="%s" class="spark" pathLength="1000" style="animation-delay:%.2fs;animation-duration:%.2fs"/>' % (d, delay, dur))
    for (x, y) in pads:
        s.append('<circle cx="%s" cy="%s" r="4" fill="%s" stroke="%s" stroke-width="2"/>' % (x, y, BG, color))
    return "".join(s)


def wrap(w, h, body, extra_style="", extra_defs="", title=""):
    defs = "".join(f.defs() for f in FACES)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="%s">'
            '<title>%s</title><style>%s%s</style><defs>%s%s%s%s</defs>%s</svg>') % (
        w, h, w, h, title, title, COMMON_STYLE, extra_style, glow_filter("soft", 3), glow_filter("glow", 5, 2), extra_defs, defs, body)


# ---------------------------------------------------------------- header
def header():
    W, H = 1000, 300
    b = []
    b.append('<rect width="%d" height="%d" rx="18" fill="%s"/>' % (W, H, BG))
    b.append('<rect width="%d" height="%d" rx="18" fill="url(#grid)"/>' % (W, H))
    b.append('<rect width="%d" height="%d" rx="18" fill="url(#gv)"/><rect width="%d" height="%d" rx="18" fill="url(#gc)"/><rect width="%d" height="%d" rx="18" fill="url(#gm)"/>' % (W, H, W, H, W, H))
    # circuit traces from the edges toward the title
    traces = [
        ("M0 70H70L100 100H190", "cyan", 0.0, [(190, 100)]),
        ("M0 150H40L70 120H150", "violet", 0.9, [(150, 120)]),
        ("M0 230H110L140 200H210", "magenta", 1.6, [(210, 200)]),
        ("M60 300V262L84 238H160", "cyan", 2.1, [(160, 238)]),
        ("M1000 70H930L900 100H810", "magenta", 0.4, [(810, 100)]),
        ("M1000 150H960L930 120H850", "violet", 1.3, [(850, 120)]),
        ("M1000 230H890L860 200H790", "cyan", 2.0, [(790, 200)]),
        ("M940 300V262L916 238H840", "lime", 0.7, [(840, 238)]),
        ("M300 0V20L320 40H420", "violet", 1.1, [(420, 40)]),
        ("M700 0V20L680 40H580", "violet", 0.2, [(580, 40)]),
    ]
    for d, col, dl, pads in traces:
        b.append(trace(d, C[col], dl, 3.2, .28, 1.6, pads))
    # bottom-center pad where the project bus starts
    b.append(trace("M500 262V300", C["violet"], 0.5, 1.4, .5, 2, [(500, 262)], spark=False))
    # title
    title = ORB.text("SUSHMIT GUJAR", 500, 136, 58, "middle", ls=5, attrs='fill="#eafeff"')
    b.append('<g class="flick"><g filter="url(#glowc)" opacity=".95">%s</g>%s</g>' % (title.replace('fill="#eafeff"', 'fill="%s"' % C["cyan"]), title))
    # subtitle
    sub = "Senior AI/ML Engineer  ·  AI Security  ·  Agentic AI"
    b.append('<g filter="url(#glowm)">%s</g>' % MONO.text(sub, 500, 182, 19, "middle", ls=.6, attrs='fill="#ffd9f6"'))
    # divider trace under subtitle
    b.append('<path d="M330 204H670" stroke="url(#lineg)" stroke-width="1.5"/>')
    b.append('<path d="M330 204H670" class="pulse" pathLength="1000" stroke="#fff" stroke-width="2.5" style="animation-duration:3.6s"/>')
    tag = "> building production AI that regulated enterprises can trust"
    b.append(MONO.text(tag, 500, 236, 14, "middle", attrs='fill="#a9b0cc"'))
    tw = MONO.width(tag, 14)
    b.append('<rect class="cursor" x="%.1f" y="224" width="8" height="15" fill="%s"/>' % (500 + tw / 2 + 4, C["lime"]))
    extra = """
.flick{animation:flick 7s linear infinite}
@keyframes flick{0%,18%,18.6%,19.4%,20%,61%,61.8%,100%{opacity:1}18.3%,19.7%{opacity:.45}61.4%{opacity:.75}}
.cursor{animation:blink 1.1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
"""
    defs = (grid_defs() +
            '<radialGradient id="gv" cx="50%" cy="0%" r="60%"><stop offset="0" stop-color="#6b2cff" stop-opacity=".45"/><stop offset="1" stop-color="#6b2cff" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="gc" cx="0%" cy="80%" r="45%"><stop offset="0" stop-color="#00b8d4" stop-opacity=".22"/><stop offset="1" stop-color="#00b8d4" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="gm" cx="100%" cy="30%" r="45%"><stop offset="0" stop-color="#ff1fb4" stop-opacity=".2"/><stop offset="1" stop-color="#ff1fb4" stop-opacity="0"/></radialGradient>' +
            ('<linearGradient id="lineg"><stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset=".5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>' % (C["cyan"], C["magenta"], C["cyan"])) +
            '<filter id="glowc" x="-20%" y="-80%" width="140%" height="260%"><feGaussianBlur stdDeviation="7" result="a"/><feGaussianBlur in="SourceGraphic" stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="a"/><feMergeNode in="a"/><feMergeNode in="b"/></feMerge></filter>'
            '<filter id="glowm" x="-10%" y="-80%" width="120%" height="260%"><feGaussianBlur in="SourceAlpha" stdDeviation="3" result="a"/><feFlood flood-color="#ff2fd2" flood-opacity=".9"/><feComposite in2="a" operator="in" result="g"/><feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    return wrap(W, H, "".join(b), extra, defs, "Sushmit Gujar · Senior AI/ML Engineer · AI Security · Agentic AI")


# ---------------------------------------------------------------- bus start
BUS_X = 34


def bus_start(n):
    W, H = 1000, 96
    b = ['<rect width="%d" height="%d" fill="none"/>' % (W, H)]
    d = "M500 0V30Q500 44 486 44H%d Q%d 44 %d 58V96" % (BUS_X + 14, BUS_X, BUS_X)
    b.append(trace(d, C["violet"], 0, 2.4, .5, 2, [(500, 2)]))
    b.append(ORB8.text("OPEN-SOURCE LAB", 540, 30, 16, ls=3, attrs='fill="%s" filter="url(#soft)"' % C["violet"]))
    b.append(MONO.text("// %d nodes online · results from committed, reproducible runs" % n, 540, 54, 12, attrs='fill="#7d84a3"'))
    b.append('<circle class="blip" cx="525" cy="24" r="4" fill="%s"/>' % C["lime"])
    extra = ".blip{animation:blip 2s ease-in-out infinite}@keyframes blip{50%{opacity:.3}}"
    return wrap(W, H, "".join(b), extra, "", "Open-source lab: project bus")


# ---------------------------------------------------------------- project card
def card(p, idx, last=False):
    W, H = 1000, 268
    col = C[p["color"]]
    b = []
    PX, PY, PW, PH = 76, 12, 912, 244
    # bus segment (continues across stacked cards)
    bus_end = 74 if last else H
    b.append('<path d="M%d 0V%d" stroke="%s" stroke-opacity=".5" stroke-width="2"/>' % (BUS_X, bus_end, C["violet"]))
    b.append('<path d="M%d 0V%d" class="pulse" pathLength="1000" stroke="%s" stroke-width="5" filter="url(#soft)" style="animation-duration:2.4s;animation-delay:%.2fs"/>' % (BUS_X, bus_end, C["violet"], idx * .5))
    if last:
        b.append('<path d="M%d 74h-10M%d 74h10M%d 80h-6M%d 80h6M%d 86h-2M%d 86h2" stroke="%s" stroke-width="2" stroke-opacity=".7"/>' % ((BUS_X,) * 6 + (C["violet"],)))
    b.append(trace("M%d 74H%d" % (BUS_X, PX), col, idx * .5 + .3, 1.2, .7, 2, [(BUS_X, 74)], spark=False))
    # panel
    b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="%s"/>' % (PX, PY, PW, PH, BG))
    b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="url(#pg)" stroke="%s" stroke-opacity=".55" stroke-width="1.5"/>' % (PX, PY, PW, PH, col))
    b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="18" fill="none" stroke="%s" stroke-opacity=".35" stroke-width="4" filter="url(#glow)"/>' % (PX, PY, PW, PH, col))
    b.append('<path d="M%d %dh-1" />' % (PX, PY))
    # top edge spark
    b.append('<path d="M%d %dH%d" class="pulse" pathLength="1000" stroke="#fff" stroke-width="2" style="animation-duration:4s;animation-delay:%.1fs"/>' % (PX + 20, PY, PX + PW - 20, idx * .7))
    b.append('<circle cx="%d" cy="74" r="5" fill="%s" stroke="%s" stroke-width="2"/>' % (PX, BG, col))
    # heading
    x0 = PX + 28
    b.append(MONO.text("NODE_%02d" % (idx + 1), x0, 44, 11.5, ls=1.5, attrs='fill="%s"' % col))
    cat = p["catlabel"].upper()
    cw = MONO.width(cat, 10.5, 1.2) + 18
    b.append('<rect x="%d" y="31" width="%.0f" height="18" rx="9" fill="%s" fill-opacity=".08" stroke="%s" stroke-opacity=".5"/>' % (x0 + 72, cw, col, col))
    b.append(MONO.text(cat, x0 + 81, 44, 10.5, ls=1.2, attrs='fill="%s"' % col))
    name = ORB.text(p["name"], x0, 92, 34, ls=1.5, attrs='fill="#ffffff"')
    b.append('<g filter="url(#glow)">%s</g>' % name.replace('fill="#ffffff"', 'fill="%s"' % col))
    b.append(name)
    b.append(MONO.text("> " + p["tagline"], x0, 118, 13, attrs='fill="%s"' % col))
    for i, line in enumerate(p["blurb"]):
        assert SANS.width(line, 13) < 556 - x0 - 12, line
        b.append(SANS.text(line, x0, 141 + i * 17, 13, attrs='fill="#a9b0cc"'))
    # stats 2x2
    sx, sy, sw, sh, g = 556, 30, 202, 58, 10
    for i, st in enumerate(p["stats"][:4]):
        cx = sx + (i % 2) * (sw + g)
        cy = sy + (i // 2) * (sh + g)
        b.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" fill-opacity=".05" stroke="%s" stroke-opacity=".25"/>' % (cx, cy, sw, sh, col, col))
        b.append('<path d="M%d %dH%d" stroke="%s" stroke-opacity=".7" stroke-width="1.5"/>' % (cx + 30, cy, cx + sw - 30, col))
        val = st["big"]
        vt = ORB8.text(val, cx + 12, cy + 30, 20, ls=.5, attrs='fill="#ffffff"')
        b.append('<g filter="url(#soft)">%s</g>%s' % (vt.replace('fill="#ffffff"', 'fill="%s"' % col), vt))
        if st.get("unit"):
            b.append(MONO.text(st["unit"], cx + 16 + ORB8.width(val, 20, .5), cy + 30, 12, attrs='fill="%s"' % col))
        assert MONO.width(st["label"], 9.5) < sw - 20, st["label"]
        b.append(MONO.text(st["label"], cx + 12, cy + 47, 9.5, attrs='fill="#9aa1bf"'))
    # pipeline row
    stages = p["pipeline"]
    n = len(stages)
    rx0, rx1, ry, rh = x0, PX + PW - 28, 186, 52
    gap = 26
    bw = (rx1 - rx0 - gap * (n - 1)) / n
    period = 0.5 * n + 1.2
    for i, st in enumerate(stages):
        bx = rx0 + i * (bw + gap)
        b.append('<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="9" fill="#070812" stroke="%s" stroke-opacity=".35"/>' % (bx, ry, bw, rh, col))
        b.append('<rect class="stg" x="%.1f" y="%d" width="%.1f" height="%d" rx="9" fill="none" stroke="%s" stroke-width="1.6" filter="url(#soft)" style="animation-delay:%.2fs;animation-duration:%.2fs"/>' % (bx, ry, bw, rh, col, i * .5, period))
        b.append(MONO.text("%02d" % (i + 1), bx + 10, ry + 16, 9, attrs='fill="%s" fill-opacity=".8"' % col))
        b.append(SANS.text(st["label"], bx + 10, ry + 31, 12.5, attrs='fill="#eceef5"'))
        assert MONO.width(st["sub"], 8.6) < bw - 16 and SANS.width(st["label"], 12.5) < bw - 16, st
        b.append(MONO.text(st["sub"], bx + 10, ry + 45, 8.6, attrs='fill="#7a819f"'))
        if i < n - 1:
            ax0, ax1, ay = bx + bw, bx + bw + gap, ry + rh / 2
            if st.get("fork_out") or stages[i + 1].get("fork"):
                for dy in (-12, 0, 12):
                    d = "M%.1f %.1fC%.1f %.1f %.1f %.1f %.1f %.1f" % (ax0, ay, ax0 + 12, ay, ax1 - 12, ay + dy, ax1, ay + dy)
                    b.append('<path d="%s" fill="none" stroke="%s" stroke-opacity=".45" stroke-width="1.5"/>' % (d, col))
                    b.append('<path d="%s" class="pulse" pathLength="1000" stroke="#fff" stroke-width="2" style="stroke-dasharray:300 700;animation-duration:1.3s;animation-delay:%.2fs"/>' % (d, i * .5))
            else:
                d = "M%.1f %.1fH%.1f" % (ax0, ay, ax1)
                b.append('<path d="%s" stroke="%s" stroke-opacity=".45" stroke-width="1.5"/>' % (d, col))
                b.append('<path d="%s" class="pulse" pathLength="1000" stroke="#fff" stroke-width="2.2" style="stroke-dasharray:350 650;animation-duration:1.3s;animation-delay:%.2fs"/>' % (d, i * .5))
                b.append('<path d="M%.1f %.1fl-6 -4v8z" fill="%s" fill-opacity=".8"/>' % (ax1 - 1, ay, col))
    # repo link hint
    link = "github.com/sushmit-gujar/%s ↗" % p["name"]
    b.append(MONO.text(link, PX + PW - 28, 168, 10.5, "end", attrs='fill="%s" fill-opacity=".85"' % col))
    extra = """
.stg{opacity:0;animation:stg 3s ease-in-out infinite}
@keyframes stg{0%%,100%%{opacity:0}10%%{opacity:1}35%%{opacity:.25}}
@media (prefers-reduced-motion:reduce){.stg{opacity:.6}}
"""
    defs = ('<linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s" stop-opacity=".10"/>'
            '<stop offset=".45" stop-color="#070812"/><stop offset="1" stop-color="#05060b"/></linearGradient>') % col
    return wrap(W, H, "".join(b), extra.replace("%%", "%"), defs, "%s: %s" % (p["name"], p["tagline"]))


# ---------------------------------------------------------------- stack
def stack():
    rows = [
        ("GENAI", "cyan", ["RAG", "Agentic AI", "Multi-agent systems", "LLM evaluation", "Embeddings", "Knowledge graphs", "Explainable AI"]),
        ("AI SECURITY", "magenta", ["MCP", "Guardrails", "OWASP LLM Top 10", "MITRE ATLAS", "SARIF", "CycloneDX ML-BOM"]),
        ("ML & MLOPS", "lime", ["Python", "Deep learning", "NLP", "MLflow", "Kubeflow", "Airflow", "Docker", "Kubernetes"]),
        ("DATA & CLOUD", "violet", ["PySpark", "SQL", "Azure Databricks", "Delta Lake", "Snowflake", "AWS Lambda", "Dgraph"]),
    ]
    W = 1000
    b, y = [], 18
    for label, colk, chips in rows:
        col = C[colk]
        b.append(MONOB.text(label, 18, y + 19, 11, ls=1.6, attrs='fill="%s"' % col))
        b.append('<path d="M130 %dH150" stroke="%s" stroke-opacity=".6" stroke-width="1.5"/>' % (y + 15, col))
        x = 158
        for ch in chips:
            w = MONO.width(ch, 12) + 22
            if x + w > W - 10:
                y += 36; x = 158
            b.append('<rect x="%.1f" y="%d" width="%.1f" height="28" rx="8" fill="%s" fill-opacity=".07" stroke="%s" stroke-opacity=".55"/>' % (x, y, w, col, col))
            b.append(MONO.text(ch, x + 11, y + 18.5, 12, attrs='fill="#e6e9f5"'))
            x += w + 8
        y += 44
    H = y + 6
    body = '<rect width="%d" height="%d" rx="16" fill="%s"/><rect width="%d" height="%d" rx="16" fill="url(#grid)"/>' % (W, H, BG, W, H) + "".join(b)
    return wrap(W, H, body, "", grid_defs(), "Tech stack")


PROJECTS = [
    dict(name="floe", color="blue", catlabel="Data engineering", tagline="Streaming lakehouse on Kubernetes, one command",
         blurb=["Wikipedia edits → Redpanda → exactly-once Apache Iceberg → dbt", "quality gate → FastAPI. Helm, KEDA on lag, Prometheus + Grafana,", "Trivy and a kind e2e test in CI. Measured on one 8-vCPU node."],
         stats=[dict(big="30,968", label="events/s · 1.2M burst, KEDA"), dict(big="2.39", unit="s", label="p95 produce → queryable"),
                dict(big="12.0", unit="s", label="burst → 6 replicas ready"), dict(big="0", label="dups/losses after SIGKILL")],
         pipeline=[dict(label="Ingest", sub="SSE · Redpanda"), dict(label="Stream", sub="contract · exactly-once"),
                   dict(label="Iceberg", sub="bronze · DLQ · MinIO"), dict(label="dbt gate", sub="DuckDB · 17 tests"), dict(label="Serve", sub="gold · FastAPI")]),
    dict(name="aiwatch", color="amber", catlabel="AI security", tagline="Find, fix + monitor AI-stack vulnerabilities",
         blurb=["Matches ML/LLM deps and MCP servers to live OSV advisories, flags", "risky loaders + HF refs, writes co-resolved fixes, and a daily", "Action reports NEW vs known via SARIF, issue and dashboard."],
         stats=[dict(big="272", label="findings auto-fixed · demo app"), dict(big="129", label="newly disclosed vs baseline"),
                dict(big="99.9", unit="%", label="agree w/ OSV · 900 pins"), dict(big="0.03", unit="s", label="offline scan · live 4.7 s")],
         pipeline=[dict(label="Inventory", sub="deps · MCP · code"), dict(label="OSV match", sub="GHSA · PYSEC · npm"),
                   dict(label="Fix", sub="co-resolved bumps"), dict(label="Monitor", sub="new · known · drift"), dict(label="Report", sub="SARIF · issue · dash")]),
    dict(name="loadsafe", color="cyan", catlabel="AI security", tagline="ML model supply-chain security scanner",
         blurb=["Statically audits pickle / PyTorch / joblib / NumPy, safetensors,", "ONNX, GGUF and Keras artifacts + Hugging Face repos before load.", "SARIF + CycloneDX ML-BOM · OWASP LLM03/04 · MITRE ATLAS."],
         stats=[dict(big="100", unit="%", label="detection · 26-file PoC corpus"), dict(big="0", unit="%", label="FPR · same corpus"),
                dict(big="0", unit="%", label="HIGH+ FPR · 5 HF checkpoints"), dict(big="~3.2", unit="GB/s", label="scan throughput")],
         pipeline=[dict(label="Model artifact", sub=".pt .pkl .onnx .gguf"), dict(label="Opcode disassembly", sub="symbolic pickle VM"),
                   dict(label="Rule engine", sub="callables · headers"), dict(label="SARIF / ML-BOM", sub="OWASP · ATLAS"), dict(label="CI gate", sub="fail build on HIGH")]),
    dict(name="mcp-warden", color="magenta", catlabel="AI security", tagline="Policy-as-code security gateway for MCP",
         blurb=["Least-privilege tool policies, PII / secret redaction, injection", "scanning, tool-definition pinning, approvals bound to exact calls", "and a tamper-evident, hash-chained audit log."],
         stats=[dict(big="30/30", label="attacks stopped · own suite"), dict(big="12/12", label="benign allowed · own suite"),
                dict(big="6/8", label="held-out, ensemble · rules 3/8"), dict(big="+0.78", unit="ms", label="p50 overhead per call")],
         pipeline=[dict(label="Agent", sub="any MCP client"), dict(label="Policy", sub="YAML allow-lists"),
                   dict(label="Redact / scan", sub="PII · secrets · injection"), dict(label="MCP server", sub="pinned tool defs"), dict(label="Audit log", sub="hash-chained")]),
    dict(name="hopscope", color="lime", catlabel="RAG & evals", tagline="GraphRAG vs vector RAG on multi-hop QA",
         blurb=["Benchmark harness on 1,000 HotpotQA questions: when does", "knowledge-graph retrieval (Personalized PageRank) beat vector RAG,", "and what does it cost? Paired bootstrap CIs, live results explorer."],
         stats=[dict(big="0.746", label="Full@5 graph+dense · vec 0.699"), dict(big="+4.7", unit="pts", label="95% CI +2.9 … +6.5"),
                dict(big="1,000", label="HotpotQA questions"), dict(big="2.4", unit="×", label="latency · 61 vs 26 ms p50")],
         pipeline=[dict(label="Question", sub="HotpotQA multi-hop", fork_out=True), dict(label="Retrievers", sub="vector | graph | hybrid", fork=True),
                   dict(label="Reader", sub="extractive QA · ONNX"), dict(label="Eval", sub="Full@5 · F1 · CI")]),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    files = {"header.svg": header(), "lab-bus.svg": bus_start(len(PROJECTS)), "stack.svg": stack()}
    for i, p in enumerate(PROJECTS):
        files["card-%s.svg" % p["name"]] = card(p, i, last=(i == len(PROJECTS) - 1))
    for k, v in files.items():
        with open(os.path.join(OUT, k), "w") as f:
            f.write(v)
        print(k, len(v))
