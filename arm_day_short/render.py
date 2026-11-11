"""Render the arm-day YouTube Short (1080x1920, 30 fps) from the puppet rig.

Run order:  python3 rig.py && python3 voice.py && python3 render.py
Output:     build/arm_day_short.mp4
"""
import json
import math
import os
import subprocess
import sys
from functools import lru_cache

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from script import SCENES

HERE = os.path.dirname(os.path.abspath(__file__))
RIG = os.path.join(HERE, "assets", "rig")
BUILD = os.path.join(HERE, "build")
os.makedirs(BUILD, exist_ok=True)

W, H, FPS = 1080, 1920, 30
PREVIEW = "--preview" in sys.argv          # render a handful of stills instead of video
ONLY = None
for a in sys.argv:
    if a.startswith("--only="):
        ONLY = a.split("=", 1)[1]

FONT_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_BLACK_IT = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
FONT_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

RED = (232, 30, 40)
RED_HOT = (255, 46, 46)
GREEN = (60, 230, 90)
WHITE = (255, 255, 255)
INK = (20, 20, 24)

# ------------------------------------------------------------------ rig
rig = json.load(open(os.path.join(RIG, "rig.json")))
RW, RH = rig["size"]
OX, OY = 220, 340                       # padding so raised arms stay on the canvas
CW, CH = RW + 2 * OX, RH + OY + 20


def load_layer(name):
    im = np.array(Image.open(os.path.join(RIG, name + ".png")).convert("RGBA")).astype(np.float32) / 255.0
    canvas = np.zeros((CH, CW, 4), np.float32)
    canvas[OY:OY + RH, OX:OX + RW] = im
    canvas[..., :3] *= canvas[..., 3:4]   # premultiply
    return canvas


def load_mask(name):
    m = np.array(Image.open(os.path.join(RIG, name + ".png"))).astype(np.float32) / 255.0
    canvas = np.zeros((CH, CW), np.float32)
    canvas[OY:OY + RH, OX:OX + RW] = m
    return canvas


BASE = load_layer("base")
LAYERS = {s: {"upper": load_layer("upper_" + s), "fore": load_layer("fore_" + s)} for s in "LR"}
MASKS = {s: {m: load_mask(f"mask_{m}_{s}") for m in ("biceps", "triceps", "forearm")} for s in "LR"}


def P(name):
    x, y = rig[name]
    return np.array([x + OX, y + OY], np.float64)


JOINT = {s: {"sh": P("shoulder_" + s), "el": P("elbow_" + s), "ha": P("hand_" + s)} for s in "LR"}
EYES = [P("head") + np.array([2, -23]), P("head") + np.array([50, -13])]  # near / far eye
EYES = [np.array([562 + OX, 127 + OY], float), np.array([610 + OX, 137 + OY], float)]
FEET = np.array([600 + OX, 1438 + OY], float)


def rot2(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    # cv2 convention (positive = counter-clockwise on screen, y down)
    return np.array([[c, s], [-s, c]])


def affine(A, pivot, target):
    M = np.zeros((2, 3))
    M[:, :2] = A
    M[:, 2] = target - A @ pivot
    return M


def arm_transforms(side, U=0.0, phi=0.0, rot=0.0, smin=0.22):
    """U: upper-arm abduction (deg, + = away from body, in the picture plane)
    phi: elbow flexion towards the camera (deg) rendered as foreshortening
    rot: extra in-plane forearm rotation (deg, + = away from body)"""
    sgn = -1.0 if side == "L" else 1.0          # outward = clockwise for L, ccw for R
    j = JOINT[side]
    Ru = rot2(sgn * U)
    el_new = j["sh"] + Ru @ (j["el"] - j["sh"])
    Mu = affine(Ru, j["sh"], j["sh"])
    Rf = rot2(sgn * (U + rot))
    d0 = j["ha"] - j["el"]
    a = Rf @ (d0 / np.linalg.norm(d0))
    s = math.cos(math.radians(phi))
    if abs(s) < smin:
        s = smin if s >= 0 else -smin
    S = np.eye(2) + (s - 1.0) * np.outer(a, a)
    Af = S @ Rf
    Mf = affine(Af, j["el"], el_new)
    hand = el_new + Af @ d0
    return Mu, Mf, el_new, hand


def warp(img, M):
    return cv2.warpAffine(img, M.astype(np.float32), (CW, CH), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def over(dst, src):
    """premultiplied src over dst (both HxWx4)"""
    dst *= (1.0 - src[..., 3:4])
    dst += src
    return dst


# ------------------------------------------------------------------ drawing helpers (canvas space)
def new_rgba():
    return np.zeros((CH, CW, 4), np.float32)


def cv_color(rgb, a=1.0):
    return (rgb[0] / 255.0 * a, rgb[1] / 255.0 * a, rgb[2] / 255.0 * a, a)


SS = 4  # subpixel shift bits for cv2 anti-aliased drawing


def ipt(p):
    return (int(round(p[0] * (1 << SS))), int(round(p[1] * (1 << SS))))


def draw_dashed_arrow(layer, pts, color=GREEN, width=9, dash=26, gap=16):
    pts = [np.asarray(p, float) for p in pts]
    seg_len = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
    total = sum(seg_len)
    if total < 30:
        return
    col = cv_color(color)
    # walk along the polyline emitting dashes
    def at(dist):
        for i, L in enumerate(seg_len):
            if dist <= L or i == len(seg_len) - 1:
                t = 0 if L == 0 else min(dist / L, 1)
                return pts[i] + (pts[i + 1] - pts[i]) * t
            dist -= L
    d = 0.0
    end = total - 34
    while d < end:
        a, b = at(d), at(min(d + dash, end))
        cv2.line(layer, ipt(a), ipt(b), (0, 0, 0, 0.55), width + 6, cv2.LINE_AA, SS)
        cv2.line(layer, ipt(a), ipt(b), col, width, cv2.LINE_AA, SS)
        d += dash + gap
    tip = pts[-1]
    back = at(total - 40)
    v = tip - back
    v /= np.linalg.norm(v) + 1e-6
    n = np.array([-v[1], v[0]])
    tri = np.array([tip + v * 6, tip - v * 40 + n * 24, tip - v * 40 - n * 24])
    cv2.fillConvexPoly(layer, np.array([ipt(p) for p in tri]), (0, 0, 0, 0.55), cv2.LINE_AA, SS)
    tri2 = np.array([tip, tip - v * 34 + n * 18, tip - v * 34 - n * 18])
    cv2.fillConvexPoly(layer, np.array([ipt(p) for p in tri2]), col, cv2.LINE_AA, SS)


def draw_barbell(layer, hl, hr):
    y = (hl[1] + hr[1]) / 2
    x0, x1 = min(hl[0], hr[0]) - 150, max(hl[0], hr[0]) + 150
    cv2.line(layer, ipt((x0, y)), ipt((x1, y)), cv_color((70, 70, 76)), 18, cv2.LINE_AA, SS)
    cv2.line(layer, ipt((x0, y - 4)), ipt((x1, y - 4)), cv_color((185, 188, 196)), 6, cv2.LINE_AA, SS)
    for x, sgn in ((x0 + 40, -1), (x1 - 40, 1)):
        for k, (w_, h_) in enumerate([(30, 190), (24, 150)]):
            cx = x + sgn * k * 30
            cv2.rectangle(layer, ipt((cx - w_ / 2, y - h_ / 2)), ipt((cx + w_ / 2, y + h_ / 2)),
                          cv_color((30, 30, 34)), -1, cv2.LINE_AA, SS)
            cv2.rectangle(layer, ipt((cx - w_ / 2, y - h_ / 2)), ipt((cx + w_ / 2, y + h_ / 2)),
                          cv_color(RED), 3, cv2.LINE_AA, SS)
    # knurl hands over the bar: fists drawn back on top by caller if needed


def draw_dumbbell_end(layer, p, r=50):
    cv2.circle(layer, ipt(p), r * (1 << SS), cv_color((28, 28, 32)), -1, cv2.LINE_AA, SS)
    cv2.circle(layer, ipt(p), int(r * 0.72) * (1 << SS), cv_color((70, 70, 78)), 5, cv2.LINE_AA, SS)
    cv2.circle(layer, ipt(p), int(r * 0.22) * (1 << SS), cv_color((175, 178, 186)), -1, cv2.LINE_AA, SS)
    cv2.circle(layer, ipt(p), r * (1 << SS), cv_color(RED), 4, cv2.LINE_AA, SS)


def draw_dumbbell_vertical(layer, c, length=150):
    top, bot = c + np.array([0, -length / 2]), c + np.array([0, length / 2])
    cv2.line(layer, ipt(top), ipt(bot), cv_color((150, 152, 160)), 16, cv2.LINE_AA, SS)
    for p in (top, bot):
        ax = (70 * (1 << SS), 26 * (1 << SS))
        cv2.ellipse(layer, ipt(p), ax, 0, 0, 360, cv_color((28, 28, 32)), -1, cv2.LINE_AA, SS)
        cv2.ellipse(layer, ipt(p), ax, 0, 0, 360, cv_color(RED), 4, cv2.LINE_AA, SS)


def draw_rope(layer, hl, hr):
    anchor = np.array([(hl[0] + hr[0]) / 2, -200.0])
    knot = np.array([(hl[0] + hr[0]) / 2, min(hl[1], hr[1]) - 170])
    cv2.line(layer, ipt(anchor), ipt(knot), cv_color((120, 122, 130), 0.75), 5, cv2.LINE_AA, SS)
    for h in (hl, hr):
        cv2.line(layer, ipt(knot), ipt(h), cv_color((25, 25, 28)), 22, cv2.LINE_AA, SS)
        cv2.line(layer, ipt(knot), ipt(h), cv_color((205, 60, 50)), 6, cv2.LINE_AA, SS)
    cv2.circle(layer, ipt(knot), 18 * (1 << SS), cv_color((150, 152, 160)), -1, cv2.LINE_AA, SS)


# ------------------------------------------------------------------ poses / motion
def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def rep_curve(t, period=1.6):
    """0 at bottom, 1 at top. fast-ish concentric, pause, slow eccentric"""
    p = (t % period) / period
    if p < 0.36:
        return ease(p / 0.36)
    if p < 0.46:
        return 1.0
    if p < 0.94:
        return 1.0 - ease((p - 0.46) / 0.48)
    return 0.0


def lerp(a, b, t):
    return a + (b - a) * t


IDLE = dict(U=2.0, phi=0.0, rot=0.0)


def pose_idle(t):
    b = math.sin(t * 2.4) * 1.5
    return {"L": dict(U=2 + b, phi=6, rot=0), "R": dict(U=2 + b, phi=6, rot=0)}


def pose_flex(amount, t=0.0):
    """double-biceps; amount 0..1 blends from idle"""
    a = ease(amount)
    b = ease((amount - 0.25) / 0.75)
    pulse = math.sin(t * 9) * 3 * a
    d = dict(U=lerp(2, 86, a) + pulse, phi=lerp(0, 18, b), rot=lerp(0, 104, b))
    return {"L": d, "R": dict(d)}


def pose_curl(a, side="both"):
    up = dict(U=4, phi=lerp(4, 150, a), rot=lerp(0, -10, a))
    rest = dict(U=3, phi=6, rot=0)
    if side == "L":
        return {"L": up, "R": rest}
    if side == "R":
        return {"L": rest, "R": up}
    return {"L": up, "R": dict(up)}


def pose_overhead(a):
    """a=0 bent (dumbbell behind head) .. 1 locked out overhead"""
    U = 190
    d = dict(U=U, phi=lerp(59, 0, a), rot=lerp(121, 12.5, a), smin=0.3)
    return {"L": d, "R": dict(d)}


def pose_pushdown(a):
    """a=0 top (forearms ~horizontal) .. 1 locked out"""
    d = dict(U=lerp(-3, 4, a), phi=lerp(96, 2, a), rot=lerp(-14, 6, a))
    return {"L": d, "R": dict(d)}


# ------------------------------------------------------------------ character render
def render_character(pose, glow=None, props=None, arrows=None, behind_head=False, eye_glow=0.0):
    """Return premultiplied RGBA canvas plus joint info."""
    canvas = new_rgba()
    info = {}
    xf = {}
    for s in "LR":
        Mu, Mf, el, ha = arm_transforms(s, **pose[s])
        xf[s] = (Mu, Mf)
        info[s] = {"el": el, "ha": ha}

    back = new_rgba()
    if behind_head:
        for s in "LR":
            over(back, warp(LAYERS[s]["fore"], xf[s][1]))
        if props:
            props(back, info, "back")
        over(canvas, back)
    over(canvas, BASE.copy())
    for s in "LR":
        over(canvas, warp(LAYERS[s]["upper"], xf[s][0]))
        if not behind_head:
            over(canvas, warp(LAYERS[s]["fore"], xf[s][1]))

    if glow:
        gm = np.zeros((CH, CW), np.float32)
        for (muscle, strength) in glow.items():
            if strength <= 0.01:
                continue
            for s in "LR":
                if muscle in ("biceps", "triceps"):
                    gm = np.maximum(gm, warp(MASKS[s][muscle], xf[s][0]) * strength)
                elif muscle == "forearm":
                    gm = np.maximum(gm, warp(MASKS[s]["forearm"], xf[s][1]) * strength)
                elif muscle == "brachialis":
                    gm = np.maximum(gm, warp(MASKS[s]["biceps"], xf[s][0]) * strength * 0.75)
                    gm = np.maximum(gm, warp(MASKS[s]["forearm"], xf[s][1]) * strength * 0.9)
        if gm.max() > 0:
            gm = np.minimum(gm * 1.4, 1.0)
            col = np.array([1.0, 0.12, 0.1], np.float32)
            a = canvas[..., 3]
            mix = (gm * 0.72)[..., None]
            canvas[..., :3] = canvas[..., :3] * (1 - mix) + col * a[..., None] * mix
            bloom = cv2.GaussianBlur(gm, (0, 0), 18) * 0.8
            glow_l = np.dstack([bloom * col[0], bloom * col[1], bloom * col[2], bloom * 0.0])
            canvas[..., :3] += glow_l[..., :3]           # additive bloom

    if props:
        layer = new_rgba()
        props(layer, info, "front")
        over(canvas, layer)
    if arrows:
        layer = new_rgba()
        for pts in arrows:
            draw_dashed_arrow(layer, pts)
        over(canvas, layer)
    if eye_glow > 0:
        g = np.zeros((CH, CW), np.float32)
        for e in EYES:
            cv2.circle(g, (int(e[0]), int(e[1])), 9, 1.0, -1)
        core = cv2.GaussianBlur(g, (0, 0), 3) * eye_glow
        halo = cv2.GaussianBlur(g, (0, 0), 16) * eye_glow * 2.5
        canvas[..., 0] += core * 1.0 + halo * 1.0
        canvas[..., 1] += core * 0.95 + halo * 0.75
        canvas[..., 2] += core * 0.6 + halo * 0.1
    np.clip(canvas, 0, None, out=canvas)
    return canvas, info


def motion_arrows(pose_fn, steps=14, sides="LR", a0=0.0, a1=1.0, inset=0.12):
    """dashed path of the hands for a movement, shortened at both ends"""
    out = []
    for s in sides:
        pts = []
        for k in range(steps + 1):
            a = lerp(a0, a1, inset + (1 - 2 * inset) * k / steps)
            _, _, _, ha = arm_transforms(s, **pose_fn(a)[s])
            off = np.array([-95.0 if s == "L" else 95.0, 0.0])
            pts.append(ha + off)
        out.append(pts)
    return out


# ------------------------------------------------------------------ backgrounds (screen space)
def _grad_bg(c_in, c_out, power=1.6):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.62)) ** 2)
    d = np.clip(d, 0, 1) ** power
    c_in, c_out = np.array(c_in, np.float32) / 255, np.array(c_out, np.float32) / 255
    return c_in * (1 - d[..., None]) + c_out * d[..., None]


BG_GRAY = _grad_bg((244, 244, 246), (196, 197, 203))
# floor line for the studio look
_floor = np.clip((np.arange(H, dtype=np.float32) - 1520) / 400, 0, 1)[:, None, None] * 0.07
BG_GRAY = np.clip(BG_GRAY - _floor, 0, 1)
BG_RED = _grad_bg((236, 40, 46), (150, 12, 20), 1.3)
BG_DARK = _grad_bg((52, 52, 58), (14, 14, 18), 1.2)


def bg_stripes(t):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = ((xx + yy * 0.75 + t * 420) // 150) % 2
    red = np.array([200, 22, 34], np.float32) / 255
    gry = np.array([228, 228, 232], np.float32) / 255
    return red * v[..., None] + gry * (1 - v[..., None])


_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
_ANG = np.arctan2(_YY - H * 0.45, _XX - W / 2)


def bg_radial(t, base=(234, 234, 238), ray=(250, 250, 252)):
    v = (np.sin(_ANG * 18 + t * 0.9) > 0.35).astype(np.float32)
    v = cv2.GaussianBlur(v, (0, 0), 1.2)
    b = np.array(base, np.float32) / 255
    r = np.array(ray, np.float32) / 255
    img = b * (1 - v[..., None]) + r * v[..., None]
    return np.clip(img * (BG_GRAY / BG_GRAY.max()) * 1.02, 0, 1)


_STRIPE_CACHE = {}


def get_bg(kind, t):
    if kind == "gray":
        return BG_GRAY.copy()
    if kind == "red":
        return BG_RED.copy()
    if kind == "dark":
        return BG_DARK.copy()
    if kind == "stripes":
        k = int(t * FPS) % 45
        if k not in _STRIPE_CACHE:
            _STRIPE_CACHE[k] = bg_stripes(k / FPS)
        return _STRIPE_CACHE[k].copy()
    if kind == "radial":
        k = int(t * FPS) % 90
        key = ("r", k)
        if key not in _STRIPE_CACHE:
            _STRIPE_CACHE[key] = bg_radial(k / FPS * 2)
        return _STRIPE_CACHE[key].copy()
    raise ValueError(kind)


# ------------------------------------------------------------------ text (screen space)
@lru_cache(maxsize=None)
def font(path, size):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=512)
def text_rgba(text, size, fill=WHITE, stroke=12, stroke_fill=INK, path=FONT_BLACK, shadow=True):
    f = font(path, size)
    bbox = f.getbbox(text, stroke_width=stroke)
    w, h = bbox[2] - bbox[0] + 30, bbox[3] - bbox[1] + 30
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = 15 - bbox[0], 15 - bbox[1]
    if shadow:
        d.text((ox + 6, oy + 8), text, font=f, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120))
    d.text((ox, oy), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return np.array(im)


def rich_line(words, size, hot, path=FONT_BLACK, stroke=12):
    """compose a line of words, hot ones in red"""
    imgs = [text_rgba(w_, size, RED_HOT if w_ in hot else WHITE, stroke, INK, path) for w_ in words]
    space = int(size * 0.18)
    w = sum(i.shape[1] for i in imgs) - 30 * (len(imgs) - 1) + space * (len(imgs) - 1)
    h = max(i.shape[0] for i in imgs)
    out = np.zeros((h, w, 4), np.uint8)
    x = 0
    for i in imgs:
        y = (h - i.shape[0]) // 2
        region = out[y:y + i.shape[0], x:x + i.shape[1]]
        a = i[..., 3:4] / 255.0
        region[:] = (i * a + region * (1 - a)).astype(np.uint8)
        region[..., 3] = np.maximum(region[..., 3], i[..., 3])
        x += i.shape[1] - 30 + space
    return out


def paste(frame, img, cx, cy, scale=1.0, alpha=1.0, anchor="center"):
    """composite uint8 RGBA img onto float frame at screen position"""
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1.0) > 1e-3:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = img.shape[:2]
    if anchor == "center":
        x0, y0 = int(cx - w / 2), int(cy - h / 2)
    elif anchor == "left":
        x0, y0 = int(cx), int(cy - h / 2)
    else:
        x0, y0 = int(cx - w), int(cy - h / 2)
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    sub = img[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32) / 255.0
    a = sub[..., 3:4] * alpha
    frame[ya:yb, xa:xb] = frame[ya:yb, xa:xb] * (1 - a) + sub[..., :3] * a


def pop(t, dur=0.18, over_=1.25):
    """scale animation for text slams"""
    if t < 0:
        return 0.0
    if t >= dur:
        return 1.0
    k = t / dur
    return over_ + (1 - over_) * (1 - (1 - k) ** 3)


@lru_cache(maxsize=None)
def rounded_rect(w, h, r, fill, border=None, bw=0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=border, width=bw)
    return np.array(im)


@lru_cache(maxsize=None)
def title_card(num, title):
    """'01' red block + title on white pill"""
    num_img = text_rgba(num, 92, WHITE, 0, INK, FONT_BLACK_IT, shadow=False)
    size = 84 if len(title) < 14 else 66
    t_img = text_rgba(title, size, INK, 0, INK, FONT_BLACK_IT, shadow=False)
    bw = num_img.shape[1] + 30
    w = bw + t_img.shape[1] + 30
    h = 150
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 14, w + 10, h + 14], 26, fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, 0, w, h], 26, fill=(255, 255, 255, 255))
    d.rounded_rectangle([0, 0, bw, h], 26, fill=RED + (255,))
    d.rectangle([bw - 26, 0, bw, h], fill=RED + (255,))
    out = np.array(im)
    for img, x in ((num_img, (bw - num_img.shape[1]) // 2), (t_img, bw + 15)):
        y = (h - img.shape[0]) // 2
        reg = out[y:y + img.shape[0], x:x + img.shape[1]]
        a = img[..., 3:4] / 255.0
        reg[..., :3] = (img[..., :3] * a + reg[..., :3] * (1 - a)).astype(np.uint8)
    return out


@lru_cache(maxsize=None)
def sets_card(sets, reps, rest):
    w, h = 560, 250
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 14, w + 10, h + 14], 30, fill=(0, 0, 0, 90))
    d.rounded_rectangle([0, 0, w, h], 30, fill=(18, 18, 22, 240), outline=RED + (255,), width=6)
    f_big, f_lab, f_small = font(FONT_BLACK, 104), font(FONT_BOLD, 34), font(FONT_BLACK, 40)
    d.text((40, 18), sets, font=f_big, fill=RED_HOT)
    d.text((44, 136), "SETS", font=f_lab, fill=(230, 230, 235))
    rx = 215 if len(reps) <= 5 else 175
    rf = f_big if len(reps) <= 5 else font(FONT_BLACK, 76)
    d.text((rx, 18 if rf is f_big else 38), reps, font=rf, fill=WHITE)
    d.text((rx + 4, 136), "REPS", font=f_lab, fill=(230, 230, 235))
    d.line([(178, 40), (178, 200)], fill=(80, 80, 88), width=3)
    f_rest = font(FONT_BLACK, 30)
    label = f"REST  {rest}"
    tw = d.textlength(label, font=f_rest)
    d.rounded_rectangle([w - 60 - tw - 40, 186, w - 40, 232], 23, fill=RED + (255,))
    d.text((w - 60 - tw - 20, 189), label, font=f_rest, fill=(255, 255, 255))
    return np.array(im)


def inset_circle(frame, char_canvas, center_canvas, t_in, cx=815, cy=600, r=165, zoom=2.0):
    """red-ringed magnifier showing the target muscle (like the reference's anatomy bubble)"""
    k = pop(t_in, 0.22, 1.3)
    if k <= 0:
        return
    rr = int(r * k)
    src_r = r / zoom
    x0, y0 = int(center_canvas[0] - src_r), int(center_canvas[1] - src_r)
    size = int(2 * src_r)
    crop = np.zeros((size, size, 4), np.float32)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + size, CW), min(y0 + size, CH)
    crop[ya - y0:yb - y0, xa - x0:xb - x0] = char_canvas[ya:yb, xa:xb]
    disc = cv2.resize(crop, (2 * rr, 2 * rr), interpolation=cv2.INTER_LINEAR)
    bgc = np.ones((2 * rr, 2 * rr, 3), np.float32) * np.array([0.93, 0.93, 0.95])
    rgb = disc[..., :3] + bgc * (1 - disc[..., 3:4])
    yy, xx = np.mgrid[0:2 * rr, 0:2 * rr]
    d = np.sqrt((xx - rr + 0.5) ** 2 + (yy - rr + 0.5) ** 2)
    m_in = np.clip(rr - 10 - d, 0, 1)[..., None]
    m_ring = (np.clip(rr - d, 0, 1) - np.clip(rr - 10 - d, 0, 1))[..., None]
    shadow = np.clip(rr + 14 - d, 0, 1)[..., None] * 0.35
    x0s, y0s = cx - rr, cy - rr
    if x0s < 0 or y0s < 0 or x0s + 2 * rr > W or y0s + 2 * rr > H:
        return
    region = frame[y0s + 8:y0s + 8 + 2 * rr, x0s + 4:x0s + 4 + 2 * rr]
    region[:] = region * (1 - shadow)
    region = frame[y0s:y0s + 2 * rr, x0s:x0s + 2 * rr]
    red = np.array(RED, np.float32) / 255
    region[:] = region * (1 - m_in - m_ring) + rgb * m_in + red * m_ring


# ------------------------------------------------------------------ camera
SHOT = {
    "full": (545 + OX, 735 + OY, 1.08),
    "fullwide": (545 + OX, 700 + OY, 0.92),
    "medium": (548 + OX, 430 + OY, 1.75),
    "mediumhigh": (548 + OX, 300 + OY, 1.55),
    "close": (566 + OX, 230 + OY, 2.7),
    "arms": (548 + OX, 520 + OY, 1.45),
    "overhead": (548 + OX, 250 + OY, 1.25),
    "cta": (548 + OX, 440 + OY, 1.05),
    "flexmed": (548 + OX, 430 + OY, 1.05),
    "exfull": (545 + OX, 735 + OY, 0.98),
    "exfull_oh": (545 + OX, 640 + OY, 0.88),
}


def camera_matrix(shot, t_shot, sway_t, punch=True, dy_screen=0.0):
    cx, cy, z = SHOT[shot]
    if punch:
        z *= 1.0 + 0.10 * math.exp(-t_shot / 0.09)
    z *= 1.0 + 0.012 * t_shot                       # slow push-in
    ang = math.sin(sway_t * 1.3) * 0.5             # idle sway around the feet
    R = rot2(ang)
    # rotate the character around its feet, then scale/translate into the screen
    A = z * R
    tgt = np.array([W / 2, H / 2 + dy_screen])
    t = tgt - z * (R @ (np.array([cx, cy]) - FEET) + FEET)
    M = np.zeros((2, 3))
    M[:, :2] = A
    M[:, 2] = t + 0  # FEET rotated in place
    return M, z


def composite_character(frame, canvas, M, z):
    # floor shadow
    sh = np.zeros((H, W), np.float32)
    fx, fy = (M[:, :2] @ FEET + M[:, 2])
    cv2.ellipse(sh, (int(fx - 20 * z), int(fy - 4 * z)), (int(260 * z), int(46 * z)), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 18 * z) * 0.33
    frame *= (1 - sh[..., None])
    scr = cv2.warpAffine(canvas, M.astype(np.float32), (W, H), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    frame *= (1 - np.clip(scr[..., 3:4], 0, 1))
    frame += scr[..., :3]


# ------------------------------------------------------------------ timeline
dur = json.load(open(os.path.join(BUILD, "vo", "durations.json")))
GAP = 0.28
timeline = []
t0 = 0.0
for sc in SCENES:
    d = dur[sc["id"]] + GAP
    if sc["id"] == "cta":
        d += 0.9
    timeline.append(dict(sc, start=t0, dur=d, vo_dur=dur[sc["id"]]))
    t0 += d
TOTAL = t0


def caption_chunks(sc):
    """split narration into 1-3 word chunks timed by character weight"""
    words = sc["vo"].upper().replace("—", " ").split()
    chunks, cur = [], []
    for w_ in words:
        cur.append(w_)
        if len(cur) == 3 or w_.endswith((".", ",", "?")) or (len(cur) == 2 and len(" ".join(cur)) > 13):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    weights = [sum(len(w_) + 2 for w_ in c) + (6 if c[-1].endswith((".", ",")) else 0) for c in chunks]
    tot = sum(weights)
    out, acc = [], 0.0
    for c, wgt in zip(chunks, weights):
        s = acc / tot * sc["vo_dur"]
        acc += wgt
        out.append((s, acc / tot * sc["vo_dur"], [w_ for w_ in c]))
    return out


for sc in timeline:
    sc["captions"] = caption_chunks(sc)


def draw_captions(frame, sc, t, y=1290):
    for (s, e, words) in sc["captions"]:
        if s <= t < e + 0.05:
            line = rich_line(tuple(words), 104, frozenset(sc["hot"]))
            k = pop(t - s, 0.12, 1.18)
            if line.shape[1] * k > W - 90:
                k *= (W - 90) / (line.shape[1] * k)
            paste(frame, line, W / 2, y, k)
            return


def big_word(frame, text, t, y=330, size=150, color=RED_HOT, path=FONT_BLACK, stroke=14):
    img = text_rgba(text, size, color, stroke, INK, path)
    k = pop(t, 0.16, 1.35)
    if img.shape[1] * k > W - 70:
        k *= (W - 70) / (img.shape[1] * k)
    paste(frame, img, W / 2, y, k)


# ------------------------------------------------------------------ scenes
def shot_at(shots, t):
    """shots: list of (start, name, extra) -> current shot and its local time"""
    cur = shots[0]
    for s in shots:
        if t >= s[0]:
            cur = s
    return cur, t - cur[0]


def scene_frame(sc, t, T):
    sid = sc["id"]
    D = sc["dur"]
    frame = None

    if sid == "hook":
        shots = [(0.0, "close"), (1.05, "flexmed"), (2.15, "full")]
        (s0, name), ts = shot_at(shots, t)
        flex = 0.0 if t < 1.05 else min((t - 1.05) / 0.45, 1.0)
        pose = pose_flex(flex, t) if flex > 0 else pose_idle(t)
        glow = {"biceps": 0.85 * ease((t - 1.7) / 0.4)} if t > 1.7 else None
        canvas, _ = render_character(pose, glow=glow)
        frame = get_bg("gray", t)
        M, z = camera_matrix(name, ts, T, dy_screen=120 if name == "full" else 0)
        composite_character(frame, canvas, M, z)
        if name == "close":
            big_word(frame, "ARM DAY", ts, y=300, color=WHITE)
        elif name == "flexmed":
            big_word(frame, "MASSIVE", ts, y=250, size=170)
        else:
            big_word(frame, "EVEN IN A T-SHIRT", ts, y=200, size=110, color=WHITE)
        draw_captions(frame, sc, t)
        return frame

    if sid == "not":
        shots = [(0.0, "medium", "stripes"), (1.1, "close", "red")]
        (s0, name, bg), ts = shot_at(shots, t)
        canvas, _ = render_character(pose_idle(T), eye_glow=0.0 if bg == "stripes" else min(ts / 0.2, 1.0))
        frame = get_bg(bg, t)
        M, z = camera_matrix(name, ts, T)
        composite_character(frame, canvas, M, z)
        if bg == "stripes":
            big_word(frame, "100 CURLS?", ts, y=320, size=150, color=WHITE)
            if ts > 0.55:
                k = pop(ts - 0.55, 0.14, 1.6)
                xs = rounded_rect(1, 1, 0, (0, 0, 0, 0))
                lay = np.zeros((260, 760, 4), np.uint8)
                cv2.line(lay, (40, 40), (720, 220), (255, 40, 40, 255), 34, cv2.LINE_AA)
                cv2.line(lay, (40, 220), (720, 40), (255, 40, 40, 255), 34, cv2.LINE_AA)
                paste(frame, lay, W / 2, 320, k)
        else:
            big_word(frame, "NOPE.", ts, y=320, size=170, color=WHITE)
        draw_captions(frame, sc, t)
        return frame

    if sid == "tri":
        shots = [(0.0, "full"), (1.25, "arms"), (2.4, "full")]
        (s0, name), ts = shot_at(shots, t)
        pulse = 0.65 + 0.35 * math.sin(t * 8)
        if t < 2.4:
            glow = {"triceps": pulse}
            pose = pose_idle(T)
        else:
            glow = {"triceps": pulse, "biceps": pulse}
            pose = pose_flex(min((t - 2.4) / 0.35, 1), T)
        canvas, info = render_character(pose, glow=glow)
        frame = get_bg("radial" if name == "arms" else "gray", t)
        M, z = camera_matrix(name, ts, T)
        composite_character(frame, canvas, M, z)
        if t < 2.4:
            big_word(frame, "TRICEPS", ts if name == "full" else 1, y=260)
            # 2/3 pie
            k = pop(ts - 0.15, 0.2, 1.3) if name == "full" else 1
            pie = np.zeros((300, 300, 4), np.uint8)
            cv2.circle(pie, (150, 150), 120, (255, 255, 255, 255), -1, cv2.LINE_AA)
            fill_t = ease((t - 0.3) / 0.8)
            cv2.ellipse(pie, (150, 150), (120, 120), -90, 0, 240 * fill_t, (232, 30, 40, 255), -1, cv2.LINE_AA)
            cv2.circle(pie, (150, 150), 120, (20, 20, 24, 255), 8, cv2.LINE_AA)
            paste(frame, pie, 190, 560, 0.85 * k)
            paste(frame, text_rgba("2/3", 96, WHITE, 10), 190, 760, k)
            if name == "arms":
                tri_c = M[:, :2] @ (JOINT["R"]["sh"] + np.array([20, 120])) + M[:, 2]
                inset_circle(frame, canvas, JOINT["R"]["sh"] + np.array([25, 130]), ts, cx=830, cy=560)
        else:
            big_word(frame, "TRAIN BOTH", ts, y=260, color=WHITE)
        draw_captions(frame, sc, t)
        return frame

    if sid in ("ex1", "ex2", "ex3", "ex4"):
        return exercise_frame(sc, t, T)
    if sid == "ex5":
        return superset_frame(sc, t, T)
    if sid == "recap":
        return recap_frame(sc, t, T)
    if sid == "cta":
        return cta_frame(sc, t, T)
    raise ValueError(sid)


def exercise_setup(sid, a, t):
    """pose, props, glow-muscle, arrows, behind_head for an exercise at rep amount a"""
    if sid == "ex1":
        pose = pose_curl(a)
        def props(layer, info, where):
            if where == "front":
                draw_barbell(layer, info["L"]["ha"], info["R"]["ha"])
        arrows = motion_arrows(lambda x: pose_curl(x))
        return pose, props, "biceps", arrows, False
    if sid == "ex2":
        p = 1.9
        side = "L" if (t % (2 * p)) < p else "R"
        pose = pose_curl(a, side)
        def props(layer, info, where):
            if where == "front":
                for s in "LR":
                    draw_dumbbell_end(layer, info[s]["ha"])
        arrows = motion_arrows(lambda x: pose_curl(x, side), sides=side)
        return pose, props, "brachialis", arrows, False
    if sid == "ex3":
        pose = pose_overhead(a)
        def props(layer, info, where):
            if where == "back":
                c = (info["L"]["ha"] + info["R"]["ha"]) / 2
                draw_dumbbell_vertical(layer, c + np.array([0, -20]))
        arrows = motion_arrows(lambda x: pose_overhead(x), sides="L", inset=0.1)
        return pose, props, "triceps", arrows, True
    if sid == "ex4":
        pose = pose_pushdown(a)
        def props(layer, info, where):
            if where == "front":
                draw_rope(layer, info["L"]["ha"], info["R"]["ha"])
        arrows = motion_arrows(lambda x: pose_pushdown(x))
        return pose, props, "triceps", arrows, False
    raise ValueError(sid)


def exercise_frame(sc, t, T):
    sid = sc["id"]
    D = sc["dur"]
    b1, b2 = 1.5, min(D - 1.5, 4.2)
    full = "exfull_oh" if sid == "ex3" else "exfull"
    shots = [(0.0, "overhead" if sid == "ex3" else "medium"), (b1, full), (b2, "arms" if sid != "ex3" else "overhead")]
    (s0, name), ts = shot_at(shots, t)
    period = 1.9 if sid == "ex2" else 1.6
    a = rep_curve(t + 0.2, period)
    pose, props, muscle, arrows, behind = exercise_setup(sid, a, t)
    isfull = name.startswith("exfull")
    g = 0.25 + 0.75 * a if name != "medium" else 0.15 + 0.5 * a
    glow = {muscle: g}
    canvas, info = render_character(pose, glow=glow, props=props,
                                    arrows=arrows if isfull else None, behind_head=behind)
    frame = get_bg("gray", t)
    M, z = camera_matrix(name, ts, T, dy_screen=150 if isfull else 0)
    composite_character(frame, canvas, M, z)

    # title card slides in at the start and stays
    tc = title_card(sc["num"], sc["title"])
    k = pop(t - 0.05, 0.2, 1.25)
    slide = (1 - ease(t / 0.25)) * -400
    paste(frame, tc, W / 2 + slide, 210, min(k, 1.0 * k), alpha=1.0)
    if isfull:
        paste(frame, sets_card(sc["sets"], sc["reps"], sc["rest"]), W / 2, 1500, pop(ts - 0.1, 0.2, 1.25))
        # anatomy bubble on the target muscle (right arm as seen on screen)
        if sid == "ex3":
            c = (JOINT["R"]["sh"] + info["R"]["el"]) / 2
            inset_circle(frame, canvas, c, ts - 0.25, cx=860, cy=560, r=140, zoom=1.9)
        else:
            j = JOINT["R"]
            c = j["sh"] + (j["el"] - j["sh"]) * 0.55 + (np.array([10, 0]) if muscle == "triceps" else np.array([0, 0]))
            if muscle == "brachialis":
                c = j["el"] + np.array([0, -30])
            inset_circle(frame, canvas, c, ts - 0.25, cx=860, cy=560, r=140, zoom=1.9)
    elif s0 > 0:  # third shot: coaching tip
        tip = text_rgba(sc["tip"], 92, WHITE, 0, INK, FONT_BLACK_IT, shadow=False)
        bar = rounded_rect(tip.shape[1] + 40, 130, 24, RED + (255,))
        k = pop(ts - 0.05, 0.18, 1.25)
        paste(frame, bar, W / 2, 420, k)
        paste(frame, tip, W / 2, 420, k)
    draw_captions(frame, sc, t)
    return frame


def superset_frame(sc, t, T):
    cut = 1.05
    idx = min(int(t // cut), int((sc["dur"] - 0.5) // cut))
    ts = t - idx * cut
    curl = idx % 2 == 0
    a = rep_curve(ts * 1.35 + 0.15, 1.2)
    if curl:
        pose = pose_curl(a)
        props = lambda layer, info, w_: draw_barbell(layer, info["L"]["ha"], info["R"]["ha"]) if w_ == "front" else None
        glow = {"biceps": 0.3 + 0.7 * a}
    else:
        pose = pose_pushdown(a)
        props = lambda layer, info, w_: draw_rope(layer, info["L"]["ha"], info["R"]["ha"]) if w_ == "front" else None
        glow = {"triceps": 0.3 + 0.7 * a}
    canvas, _ = render_character(pose, glow=glow, props=props)
    frame = get_bg("radial", t)
    M, z = camera_matrix("exfull" if idx % 3 != 2 else "arms", ts, T, dy_screen=150 if idx % 3 != 2 else 0)
    composite_character(frame, canvas, M, z)
    paste(frame, title_card(sc["num"], sc["title"]), W / 2, 210, pop(t, 0.2, 1.25))
    lab = "CURLS" if curl else "PUSHDOWNS"
    paste(frame, text_rgba(lab, 118, RED_HOT if curl else WHITE, 13), W / 2, 410, pop(ts, 0.14, 1.3))
    if t > 2.0:
        paste(frame, sets_card(sc["sets"], sc["reps"], sc["rest"]), W / 2, 1500, pop(t - 2.0, 0.2, 1.25))
    draw_captions(frame, sc, t)
    return frame


RECAP = [("01", "BARBELL CURL", "4 x 8-10"), ("02", "HAMMER CURL", "3 x 10-12"),
         ("03", "OVERHEAD EXT", "3 x 10-12"), ("04", "ROPE PUSHDOWN", "3 x 12-15"),
         ("05", "SUPERSET", "2 x FAIL")]


@lru_cache(maxsize=None)
def recap_row(num, name, sr):
    w, h = 900, 132
    im = Image.new("RGBA", (w + 12, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 10, w + 8, h + 10], 24, fill=(0, 0, 0, 80))
    d.rounded_rectangle([0, 0, w, h], 24, fill=(255, 255, 255, 250))
    d.rounded_rectangle([0, 0, 130, h], 24, fill=RED + (255,))
    d.rectangle([104, 0, 130, h], fill=RED + (255,))
    d.text((24, 22), num, font=font(FONT_BLACK_IT, 72), fill=WHITE)
    d.text((156, 38), name, font=font(FONT_BLACK_IT, 50), fill=INK)
    f = font(FONT_BLACK, 46)
    tw = d.textlength(sr, font=f)
    d.text((w - 30 - tw, 38), sr, font=f, fill=RED)
    return np.array(im)


def recap_frame(sc, t, T):
    canvas, _ = render_character(pose_flex(1.0, T), glow={"biceps": 0.6, "triceps": 0.6})
    frame = get_bg("dark", t)
    M, z = camera_matrix("fullwide", t, T, punch=False, dy_screen=330)
    composite_character(frame, canvas, M, z)
    frame *= 0.55
    paste(frame, text_rgba("THE WORKOUT", 112, WHITE, 12), W / 2, 220, pop(t, 0.16, 1.3))
    for i, row in enumerate(RECAP):
        ti = t - 0.12 - i * 0.16
        if ti < 0:
            continue
        slide = (1 - ease(ti / 0.22)) * 700
        paste(frame, recap_row(*row), W / 2 + slide, 400 + i * 158, 1.0)
    pill = text_rgba("REST 60s  •  ADD WEIGHT WEEKLY", 54, WHITE, 0, INK, FONT_BLACK, shadow=False)
    bar = rounded_rect(pill.shape[1] + 50, 100, 50, RED + (255,))
    k = pop(t - 1.1, 0.18, 1.25)
    paste(frame, bar, W / 2, 1230, k)
    paste(frame, pill, W / 2, 1230, k)
    return frame


def cta_frame(sc, t, T):
    flex = min(t / 0.4, 1)
    canvas, _ = render_character(pose_flex(flex, T), glow={"biceps": 0.5 + 0.4 * math.sin(t * 7)}, eye_glow=0.0)
    frame = get_bg("red", t)
    M, z = camera_matrix("cta", t, T)
    composite_character(frame, canvas, M, z)
    big_word(frame, "SAVE THIS", t, y=250, size=150, color=WHITE)
    if t > 1.35:
        k = pop(t - 1.35, 0.16, 1.3)
        btn = rounded_rect(640, 150, 75, (255, 255, 255, 255))
        paste(frame, btn, W / 2, 1460, k)
        paste(frame, text_rgba("FOLLOW +", 88, RED, 0, INK, FONT_BLACK, shadow=False), W / 2, 1460, k)
        bounce = abs(math.sin((t - 1.35) * 6)) * 26
        arrow = np.zeros((120, 120, 4), np.uint8)
        cv2.fillConvexPoly(arrow, np.array([[10, 30], [110, 30], [60, 105]]), (255, 255, 255, 255), cv2.LINE_AA)
        for x in (W / 2 - 230, W / 2 + 230):
            paste(frame, arrow, x, 1290 + bounce, k)
    draw_captions(frame, sc, t, y=1640 if t > 1.35 else 1290)
    return frame


# ------------------------------------------------------------------ main
def frame_at(T):
    for sc in timeline:
        if sc["start"] <= T < sc["start"] + sc["dur"]:
            return sc, scene_frame(sc, T - sc["start"], T)
    sc = timeline[-1]
    return sc, scene_frame(sc, sc["dur"] - 1e-3, T)


def finish(frame):
    # subtle vignette + grain for the animated-film look
    return np.clip(frame, 0, 1)


VIGN = None


def to_u8(frame):
    global VIGN
    if VIGN is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        VIGN = (1 - 0.18 * np.clip(d - 0.55, 0, 1) ** 1.5)[..., None]
    return (np.clip(frame * VIGN, 0, 1) * 255 + 0.5).astype(np.uint8)


def cut_times():
    cuts, slams = [], []
    for sc in timeline:
        s, D, sid = sc["start"], sc["dur"], sc["id"]
        cuts.append(s)
        local = {"hook": [1.05, 2.15], "not": [1.1], "tri": [1.25, 2.4]}.get(sid, [])
        if sid in ("ex1", "ex2", "ex3", "ex4"):
            local = [1.5, min(D - 1.5, 4.2)]
            slams.append(s + 0.05)
        if sid == "ex5":
            local = [k * 1.05 for k in range(1, int((D - 0.5) / 1.05) + 1)]
            slams.append(s)
        if sid == "not":
            slams.append(s + 0.55)
        if sid == "cta":
            slams.append(s + 1.35)
        cuts += [s + x for x in local if x < D]
    return cuts, slams


def main():
    cuts, slams = cut_times()
    with open(os.path.join(BUILD, "timeline.json"), "w") as f:
        json.dump({"total": TOTAL, "cuts": cuts, "slams": slams,
                   "scenes": [{k: v for k, v in sc.items() if k in ("id", "start", "dur", "vo_dur")} for sc in timeline]},
                  f, indent=1)
    if PREVIEW:
        os.makedirs(os.path.join(BUILD, "preview"), exist_ok=True)
        for sc in timeline:
            if ONLY and sc["id"] != ONLY:
                continue
            for frac in (0.15, 0.45, 0.8):
                T = sc["start"] + sc["dur"] * frac
                _, fr = frame_at(T)
                Image.fromarray(to_u8(fr)).resize((540, 960)).save(
                    os.path.join(BUILD, "preview", f"{sc['id']}_{int(frac*100):02d}.png"))
        print("previews written")
        return
    n = int(math.ceil(TOTAL * FPS))
    lo, hi = 0, n
    out = os.path.join(BUILD, "video_silent.mp4")
    for a in sys.argv:
        if a.startswith("--range="):
            k, parts = map(int, a.split("=", 1)[1].split("/"))
            step = int(math.ceil(n / parts))
            lo, hi = k * step, min(n, (k + 1) * step)
            out = os.path.join(BUILD, f"part{k}.mp4")
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(lo, hi):
        _, fr = frame_at(i / FPS)
        proc.stdin.write(to_u8(fr).tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{n}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out, f"{TOTAL:.2f}s")


if __name__ == "__main__":
    main()
