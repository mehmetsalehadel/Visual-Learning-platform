"""Draws the animation frames (PNG images) for a scene.

A scene is a dict from a lecture JSON file. Four kinds of scenes are supported
(checked in this order): flow, table, bullets, code (+ optional output).
Everything drawn on the images is Latin text (English); Arabic explanations
are shown by Streamlit under the image, so no Arabic text shaping is needed here.
"""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).parent / "fonts"
W, H = 1280, 720
MARGIN = 48
TOP = 140  # content area starts here
BOTTOM = H - 34

SANS, SANS_B = "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"
MONO, MONO_B = "DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"

C = {
    "bg": (13, 17, 28),
    "panel": (21, 27, 43),
    "panel2": (30, 38, 60),
    "border": (45, 55, 85),
    "text": (232, 236, 247),
    "muted": (125, 138, 170),
    "dim": (70, 80, 110),
    "accent": (96, 165, 250),
    "accent2": (167, 139, 250),
    "ok": (74, 222, 128),
    "err": (248, 113, 113),
    "warn": (251, 191, 36),
}
SYN = {
    "plain": (226, 232, 240),
    "comment": (110, 140, 125),
    "string": (251, 191, 128),
    "keyword": (192, 132, 252),
    "number": (134, 239, 172),
    "builtin": (125, 211, 252),
}

_cache: dict = {}


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    key = (name, int(size))
    if key not in _cache:
        _cache[key] = ImageFont.truetype(str(FONT_DIR / name), int(size))
    return _cache[key]


def _fit(name: str, text: str, max_w: float, start: int, minimum: int = 14):
    size = start
    while size > minimum and font(name, size).getlength(text) > max_w:
        size -= 1
    return font(name, size)


# --------------------------------------------------------------------------
# syntax highlighting (small, regex based - good enough for teaching snippets)
# --------------------------------------------------------------------------
KEYWORDS = set(
    "import from if elif else for while in def return try except with as not and or "
    "is lambda pass break continue class raise finally True False None".split()
)
BUILTINS = set("print input int float str bool len type open range iter".split())
TOKEN_RE = re.compile(
    r"(?P<comment>\#.*)"
    r"|(?P<string>[rbfRBF]{0,2}(?:\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'))"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<word>[A-Za-z_]\w*)"
)


def _tokenize(text: str):
    segs, pos = [], 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            segs.append((text[pos:m.start()], "plain"))
        kind = m.lastgroup
        tok = m.group()
        if kind == "word":
            kind = "keyword" if tok in KEYWORDS else "builtin" if tok in BUILTINS else "plain"
        segs.append((tok, kind))
        pos = m.end()
    if pos < len(text):
        segs.append((text[pos:], "plain"))
    return segs


def highlight(lines: list[str]):
    result, in_tq = [], False
    for line in lines:
        segs, pos = [], 0
        if in_tq:
            end = line.find('"""')
            if end == -1:
                result.append([(line, "string")])
                continue
            segs.append((line[:end + 3], "string"))
            pos, in_tq = end + 3, False
        rest = line[pos:]
        tq = rest.find('"""')
        if tq != -1 and "#" not in rest[:tq]:
            segs += _tokenize(rest[:tq])
            after = rest[tq:]
            close = after.find('"""', 3)
            if close == -1:
                segs.append((after, "string"))
                in_tq = True
            else:
                segs.append((after[:close + 3], "string"))
                segs += _tokenize(after[close + 3:])
        else:
            segs += _tokenize(rest)
        result.append(segs)
    return result


# --------------------------------------------------------------------------
# shared pieces
# --------------------------------------------------------------------------
def _base(ctx: dict, title: str):
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    total, idx = ctx["total"], ctx["index"]
    d.rectangle((0, 0, int(W * idx / total), 4), fill=C["accent"])
    d.text((MARGIN, 24), f"{ctx['subject_en']}  /  {ctx['lesson_en']}", font=font(SANS, 18), fill=C["muted"])
    right = f"{idx} / {total}"
    f = font(SANS, 18)
    d.text((W - MARGIN - f.getlength(right), 24), right, font=f, fill=C["muted"])
    d.text((MARGIN, 60), title, font=_fit(SANS_B, title, W - 2 * MARGIN, 42, 24), fill=C["text"])
    d.rectangle((MARGIN, 118, MARGIN + 90, 121), fill=C["accent"])
    return img, d


def _panel(d, x, y, w, h, label, color=None, dim=False):
    d.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=C["panel"],
                        outline=C["dim"] if dim else C["border"], width=2)
    d.text((x + 22, y + 10), label, font=font(SANS_B, 15), fill=C["dim"] if dim else (color or C["muted"]))


# --------------------------------------------------------------------------
# code scene
# --------------------------------------------------------------------------
LABEL_H, PAD_B, GAP = 36, 16, 16
PLACEHOLDER = "\u25b6 Next to run"


def _code_layout(code_lines, out_lines):
    """Pick the largest font that fits, stacking the output under the code ('v')
    or putting it beside the code ('s')."""
    cw, avail_h = W - 2 * MARGIN, BOTTOM - TOP
    code_len = max(len(l) for l in code_lines + [""])
    out_len = max([len(l) for l in out_lines] + [len(PLACEHOLDER)]) if out_lines else 0
    for size in range(26, 13, -1):
        lh = int(size * 1.5)
        adv = font(MONO, size).getlength("M")
        code_h = LABEL_H + len(code_lines) * lh + PAD_B
        out_h = LABEL_H + len(out_lines) * lh + PAD_B if out_lines else 0
        code_need, out_need = code_len * adv + 44, out_len * adv + 44
        if code_need <= cw and out_need <= cw and code_h + (GAP + out_h if out_lines else 0) <= avail_h:
            return "v", size
        if out_lines and code_need + out_need + GAP <= cw and max(code_h, out_h) <= avail_h:
            return "s", size
    return "v", 14


def _scene_code(scene, ctx):
    code_lines = scene["code"].split("\n")
    output = scene.get("output")
    out_lines = output.split("\n") if output else []
    layout, size = _code_layout(code_lines, out_lines)
    lh, mono = int(size * 1.5), font(MONO, size)
    adv = mono.getlength("M")
    hl = highlight(code_lines)
    cw = W - 2 * MARGIN
    code_h = LABEL_H + len(code_lines) * lh + PAD_B
    out_h = LABEL_H + len(out_lines) * lh + PAD_B if out_lines else 0

    # geometry of the two panels: (x, y, w, h)
    if layout == "s":
        code_need = max(len(l) for l in code_lines) * adv + 44
        out_need = max([len(l) for l in out_lines] + [len(PLACEHOLDER)]) * adv + 44
        code_w = code_need + (cw - code_need - out_need - GAP) * 0.55
        h = max(code_h, out_h)
        code_box = (MARGIN, TOP, code_w, h)
        out_box = (MARGIN + code_w + GAP, TOP, cw - code_w - GAP, h)
    else:
        code_box = (MARGIN, TOP, cw, code_h)
        out_box = (MARGIN, TOP + code_h + GAP, cw, out_h)

    def draw_frame(show_output: bool):
        img, d = _base(ctx, scene["title"])
        x0, y0, w0, h0 = code_box
        _panel(d, x0, y0, w0, h0, scene.get("code_label", "Python"), C["accent"])
        y = y0 + LABEL_H
        for segs in hl:
            x = x0 + 22
            for txt, kind in segs:
                d.text((x, y), txt, font=mono, fill=SYN[kind])
                x += mono.getlength(txt)
            y += lh
        if out_lines:
            ox, oy, ow, oh = out_box
            color = C["err"] if scene.get("error") else C["ok"]
            _panel(d, ox, oy, ow, oh, scene.get("output_label", "Output"), color, dim=not show_output)
            y = oy + LABEL_H
            if show_output:
                for line in out_lines:
                    d.text((ox + 22, y), line, font=mono, fill=color)
                    y += lh
            else:
                d.text((ox + 22, y), PLACEHOLDER, font=mono, fill=C["dim"])
        return img

    return [draw_frame(False), draw_frame(True)] if out_lines else [draw_frame(True)]


# --------------------------------------------------------------------------
# bullets scene
# --------------------------------------------------------------------------
def _scene_bullets(scene, ctx):
    items = scene["bullets"]
    img, d = _base(ctx, scene["title"])
    avail_h, avail_w = BOTTOM - TOP - 20, W - 2 * MARGIN - 60
    size = 36
    while size > 20:
        lh = size * 1.7
        if len(items) * lh <= avail_h and all(font(SANS, size).getlength(t) <= avail_w for t in items):
            break
        size -= 1
    f, lh = font(SANS, size), size * 1.7
    y = TOP + 20
    for t in items:
        r = size // 6
        cy = y + size * 0.65
        d.ellipse((MARGIN + 6, cy - r, MARGIN + 6 + 2 * r, cy + r), fill=C["accent"])
        d.text((MARGIN + 44, y), t, font=f, fill=C["text"])
        y += lh
    return [img]


# --------------------------------------------------------------------------
# table scene
# --------------------------------------------------------------------------
def _scene_table(scene, ctx):
    t = scene["table"]
    headers, rows = t["headers"], t["rows"]
    mono_cols = set(t.get("mono_cols", []))
    avail_w, avail_h = W - 2 * MARGIN, BOTTOM - TOP
    pad = 18

    def fnt(col, bold=False):
        return font(MONO_B if bold else MONO, size) if col in mono_cols else font(SANS_B if bold else SANS, size)

    for size in range(26, 13, -1):
        widths = []
        for c in range(len(headers)):
            cells = [font(SANS_B, size).getlength(headers[c])] + [fnt(c).getlength(r[c]) for r in rows]
            widths.append(max(cells) + 2 * pad)
        row_h = int(size * 2.0)
        if sum(widths) <= avail_w and row_h * (len(rows) + 1) <= avail_h:
            break
    extra = (avail_w - sum(widths)) / len(widths)
    widths = [w + max(0, extra) for w in widths]

    img, d = _base(ctx, scene["title"])
    x0, y = MARGIN, TOP
    d.rounded_rectangle((x0, y, x0 + avail_w, y + row_h * (len(rows) + 1)), radius=12, fill=C["panel"],
                        outline=C["border"], width=2)
    d.rounded_rectangle((x0, y, x0 + avail_w, y + row_h), radius=12, fill=C["panel2"])
    x = x0
    for c, h in enumerate(headers):
        d.text((x + pad, y + row_h / 2), h, font=font(SANS_B, size), fill=C["accent"], anchor="lm")
        x += widths[c]
    for i, row in enumerate(rows):
        y += row_h
        d.line((x0, y, x0 + avail_w, y), fill=C["border"], width=1)
        x = x0
        for c, cell in enumerate(row):
            color = C["warn"] if c in mono_cols else C["text"]
            d.text((x + pad, y + row_h / 2), cell, font=fnt(c), fill=color, anchor="lm")
            x += widths[c]
    return [img]


# --------------------------------------------------------------------------
# flow scene (boxes + arrows, revealed step by step)
# --------------------------------------------------------------------------
def _wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def _box(d, x, y, w, h, text, fill, outline, text_color):
    d.rounded_rectangle((x, y, x + w, y + h), radius=16, fill=fill, outline=outline, width=3)
    for size in range(24, 12, -1):
        f = font(SANS_B, size)
        lines = _wrap(text, f, w - 18)
        if len(lines) <= 3 and all(f.getlength(l) <= w - 18 for l in lines):
            break
    lh = size * 1.3
    ty = y + h / 2 - lh * len(lines) / 2 + lh / 2
    for line in lines:
        d.text((x + w / 2, ty), line, font=f, fill=text_color, anchor="mm")
        ty += lh


def _arrow(d, x1, x2, cy, color):
    d.line((x1 + 4, cy, x2 - 6, cy), fill=color, width=3)
    d.polygon([(x2 - 4, cy), (x2 - 16, cy - 8), (x2 - 16, cy + 8)], fill=color)


def _scene_flow(scene, ctx):
    steps = scene["flow"]
    branches = scene.get("branches")
    n = len(steps)
    gap = 34 if n > 5 else 46
    bw = (W - 2 * MARGIN - gap * (n - 1)) / n
    bh = 124
    top = 200 if branches else 270
    cy = top + bh / 2
    frames = []

    def draw(k, show_branches):
        img, d = _base(ctx, scene["title"])
        for i, label in enumerate(steps):
            x = MARGIN + i * (bw + gap)
            if i < k - 1 or (i == k - 1 and show_branches):
                _box(d, x, top, bw, bh, label, (36, 34, 80), C["accent2"], C["text"])
            elif i == k - 1:
                _box(d, x, top, bw, bh, label, C["accent"], C["accent"], C["bg"])
            else:
                _box(d, x, top, bw, bh, label, C["bg"], C["dim"], C["dim"])
            if i < n - 1:
                _arrow(d, x + bw, x + bw + gap, cy, C["accent2"] if i + 1 < k else C["dim"])
        if show_branches:
            last_cx = MARGIN + (n - 1) * (bw + gap) + bw / 2
            by, bw2 = top + bh + 90, 190
            mid_y = top + bh + 40
            centers = [W / 2 - 170, W / 2 + 170]
            d.line((last_cx, top + bh, last_cx, mid_y), fill=C["muted"], width=3)
            d.line((min(centers), mid_y, max(max(centers), last_cx), mid_y), fill=C["muted"], width=3)
            for cx, br in zip(centers, branches):
                good = br.get("kind") == "good"
                col = C["ok"] if good else C["err"]
                d.line((cx, mid_y, cx, by), fill=C["muted"], width=3)
                d.polygon([(cx, by + 2), (cx - 8, by - 10), (cx + 8, by - 10)], fill=C["muted"])
                d.text((cx + 14, mid_y + 24), br["label"], font=font(SANS_B, 22), fill=col)
                _box(d, cx - bw2 / 2, by, bw2, 96, br["text"], C["panel"], col, col)
        return img

    for k in range(1, n + 1):
        frames.append(draw(k, False))
    if branches:
        frames.append(draw(n, True))
    return frames


def _scene_blank(scene, ctx):
    img, _ = _base(ctx, scene.get("title", ""))
    return [img]


def render_scene(scene: dict, ctx: dict) -> list[Image.Image]:
    """ctx = {subject_en, lesson_en, index (1-based), total}"""
    if scene.get("flow"):
        return _scene_flow(scene, ctx)
    if scene.get("table"):
        return _scene_table(scene, ctx)
    if scene.get("bullets"):
        return _scene_bullets(scene, ctx)
    if scene.get("code") is not None:
        return _scene_code(scene, ctx)
    return _scene_blank(scene, ctx)
