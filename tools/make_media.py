#!/usr/bin/env python3
"""Draws the addon's own textures (aged parchment, worn leather, cloth ribbons,
gilt fittings, illuminated ornaments) as 32-bit TGA files in ../Media.
Everything is procedural so nothing is copied from another addon or the game.

Usage: python -I make_media.py [out_dir]
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Media")
os.makedirs(OUT, exist_ok=True)
random.seed(20261111)

WHITE = (255, 255, 255, 255)


def save(img, name):
    path = os.path.join(OUT, name + ".tga")
    img.convert("RGBA").save(path)
    print("wrote", path, img.size)


def noise(size, scale, amp):
    """Blurred random noise in [-amp, amp] as a flat list."""
    small = Image.effect_noise((max(1, size[0] // scale), max(1, size[1] // scale)), 60).resize(size, Image.BICUBIC)
    small = small.filter(ImageFilter.GaussianBlur(max(0.5, scale / 2)))
    data = small.get_flattened_data() if hasattr(small, "get_flattened_data") else small.getdata()
    return [(p - 128) / 128.0 * amp for p in data]


def clamp(v):
    return int(max(0, min(255, v)))


def blotches(img, count, rmin, rmax, color, alpha):
    """Soft stains: radial falloff discs composited with low alpha."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x, y = random.randrange(img.width), random.randrange(img.height)
        r = random.randrange(rmin, rmax)
        a = random.randrange(alpha // 2, alpha + 1)
        steps = 6
        for i in range(steps, 0, -1):
            rr = r * i / steps
            d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(*color, int(a / steps)))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(img, layer)


def make_tileable(img):
    """Cross-fade the image with itself shifted by half, both axes."""
    w, h = img.size
    img2 = Image.new("RGBA", (w, h))
    img2.paste(img.crop((w // 2, 0, w, h)), (0, 0))
    img2.paste(img.crop((0, 0, w // 2, h)), (w // 2, 0))
    blended = Image.blend(img, img2, 0.5)
    img3 = Image.new("RGBA", (w, h))
    img3.paste(blended.crop((0, h // 2, w, h)), (0, 0))
    img3.paste(blended.crop((0, 0, w, h // 2)), (0, h // 2))
    return Image.blend(blended, img3, 0.5)


def masked(img, layer):
    """Composite `layer` onto `img` only where `img` already has alpha."""
    mask = img.split()[3]
    return Image.alpha_composite(img, Image.composite(layer, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask))


def bezier(p0, p1, p2, p3, steps=24):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def spiral(cx, cy, r0, r1, turns, start, steps=40, cw=1):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        a = start + cw * t * turns * 2 * math.pi
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def leaf(d, x, y, ang, size, fill):
    """A small pointed leaf (two arcs) at x,y pointing along ang."""
    pts = []
    for i in range(13):
        t = i / 12
        w = math.sin(t * math.pi) * size * 0.42
        px, py = t * size, w
        pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
    for i in range(12, -1, -1):
        t = i / 12
        w = -math.sin(t * math.pi) * size * 0.42
        px, py = t * size, w
        pts.append((x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)))
    d.polygon(pts, fill=fill)


# ---------------------------------------------------------------------------
def parchment():
    w = h = 512
    base = (228, 204, 154)
    burn = (112, 76, 38)
    n1 = noise((w, h), 48, 15)
    n2 = noise((w, h), 8, 7)
    n3 = noise((w, h), 2, 3)
    px = []
    for i in range(w * h):
        x, y = i % w, i // w
        d = n1[i] + n2[i] + n3[i]
        r, g, b = base[0] + d, base[1] + d * 1.05, base[2] + d * 1.25
        # toasted, darkened edges: strongest in the corners, modulated by noise
        ex = min(x, w - 1 - x) / w
        ey = min(y, h - 1 - y) / h
        e = min(ex, ey) + 0.35 * min(1.0, (ex * ey) ** 0.5)
        t = max(0.0, 0.20 - e) / 0.20
        t = (t ** 1.5) * (0.66 + n1[i] / 40.0)
        if t > 0:
            r, g, b = r + (burn[0] - r) * t, g + (burn[1] - g) * t, b + (burn[2] - b) * t
        px.append((clamp(r), clamp(g), clamp(b), 255))
    img = Image.new("RGBA", (w, h))
    img.putdata(px)
    img = blotches(img, 6, 40, 110, (150, 105, 55), 22)   # old water and ink stains
    # specks and fibres go on their own layer: drawing them straight onto the
    # page would overwrite the alpha and punch pin-holes through the paper
    marks = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(marks)
    for _ in range(40):  # tiny faint foxing specks
        x, y = random.randrange(w), random.randrange(h)
        draw.point((x, y), fill=(120, 80, 40, random.randrange(30, 60)))
    for _ in range(70):  # paper fibres
        x, y = random.randrange(w), random.randrange(h)
        ln = random.randrange(4, 14)
        ang = random.uniform(0, math.pi)
        draw.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))], fill=(130, 100, 60, random.randrange(25, 50)), width=1)
    img = Image.alpha_composite(img, marks)
    save(img, "Page")


def leather():
    w = h = 256
    base = (52, 26, 13)
    n1 = noise((w, h), 24, 12)
    n2 = noise((w, h), 5, 10)
    n3 = noise((w, h), 2, 5)
    px = []
    for i in range(w * h):
        d = n1[i] + n2[i] + n3[i]
        px.append((clamp(base[0] + d), clamp(base[1] + d * 0.7), clamp(base[2] + d * 0.5), 255))
    img = Image.new("RGBA", (w, h))
    img.putdata(px)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(26):  # creases
        x, y = random.randrange(w), random.randrange(h)
        pts = [(x, y)]
        ang = random.uniform(0, 2 * math.pi)
        for _ in range(random.randrange(4, 10)):
            ang += random.uniform(-0.6, 0.6)
            x += math.cos(ang) * random.randrange(6, 14)
            y += math.sin(ang) * random.randrange(6, 14)
            pts.append((x, y))
        d.line(pts, fill=(12, 6, 3, random.randrange(50, 90)), width=1)
    layer = layer.filter(ImageFilter.GaussianBlur(0.8))
    img = Image.alpha_composite(img, layer)
    img = blotches(img, 5, 30, 80, (120, 70, 38), 22)   # worn, polished patches
    save(make_tileable(img), "Leather")


def ribbon():
    w, h = 64, 128
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(4, 0), (60, 0), (60, 112), (32, 94), (4, 112)]
    d.polygon(pts, fill=WHITE)
    weave = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(weave)
    for y in range(0, h, 2):
        wd.line([(0, y), (w, y)], fill=(0, 0, 0, 16))
    for x in range(4, 60):
        t = (x - 4) / 56
        if t > 0.62:
            wd.line([(x, 0), (x, 114)], fill=(0, 0, 0, int(80 * (t - 0.62) / 0.38)))
        elif 0.06 < t < 0.3:
            wd.line([(x, 0), (x, 114)], fill=(255, 255, 255, int(50 * (1 - abs(t - 0.18) / 0.12))))
    # a darker band and gold edge threads near the hem
    wd.line([(4, 84), (60, 84)], fill=(0, 0, 0, 40), width=2)
    wd.line([(4, 87), (60, 87)], fill=(255, 220, 140, 90), width=1)
    for x in range(4, 60):  # frayed hem along the notch
        if random.random() < 0.5:
            yy = 112 - abs(x - 32) * 18 / 28
            wd.line([(x, yy - 1), (x, yy + random.randrange(0, 3))], fill=(0, 0, 0, 60))
    img = masked(img, weave)
    save(img, "Ribbon")
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon(pts, fill=(0, 0, 0, 170))
    save(sh.filter(ImageFilter.GaussianBlur(3)), "RibbonShadow")


def flourish():
    """A horizontal divider: vine scrolls curling out from a central lozenge."""
    w, h = 256, 32
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = 16
    for side in (1, -1):
        def X(x):
            return 128 + side * x
        # main stem with a gentle wave, curling into a spiral at the end
        stem = bezier((X(18), cy), (X(50), cy - 6), (X(80), cy + 6), (X(104), cy))
        d.line(stem, fill=WHITE, width=2)
        sp = spiral(X(112), cy, 9, 1.5, 0.9, math.pi if side > 0 else 0, cw=-side)
        d.line([stem[-1]] + sp, fill=WHITE, width=2)
        # leaves alternating above and below the stem
        for i, (lx, ang) in enumerate(((40, -0.9), (62, 0.9), (84, -0.9))):
            px, py = X(lx), cy + (3 if ang > 0 else -3)
            leaf(d, px, py, (math.pi / 2 if ang > 0 else -math.pi / 2) + 0.25 * side, 10, WHITE)
        # a small berry dot near the lozenge
        d.ellipse((X(12) - 2, cy - 2, X(12) + 2, cy + 2), fill=WHITE)
    d.polygon([(128, cy - 8), (136, cy), (128, cy + 8), (120, cy)], fill=WHITE)
    d.polygon([(128, cy - 4), (132, cy), (128, cy + 4), (124, cy)], fill=(255, 255, 255, 0))
    save(img.filter(ImageFilter.GaussianBlur(0.4)), "Flourish")


def rule():
    """A thin tapering rule with a lozenge at the left end (for sub-headings)."""
    w, h = 256, 16
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(14, 250):
        t = (x - 14) / 236
        a = int(255 * (1 - t ** 2.2))
        d.point((x, 8), fill=(255, 255, 255, a))
        if t < 0.5:
            d.point((x, 7), fill=(255, 255, 255, int(a * (1 - t * 2) * 0.8)))
    d.polygon([(6, 4), (10, 8), (6, 12), (2, 8)], fill=WHITE)
    save(img, "Rule")


def vine():
    """A corner ornament: vines with leaves and spirals running along two edges
    from the top-left corner. Mirrored in-game for the other corners."""
    s = 128
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # corner knot
    d.line(bezier((10, 118), (6, 60), (6, 20), (10, 10)), fill=WHITE, width=2)
    d.line(bezier((10, 10), (20, 6), (60, 6), (118, 10)), fill=WHITE, width=2)
    d.ellipse((7, 7, 13, 13), fill=WHITE)
    # branches peeling off each stem, curling into spirals
    for (sx, sy, dx, dy, cw) in ((8, 44, 1, 0.35, 1), (8, 84, 1, -0.2, -1), (44, 8, 0.35, 1, -1), (84, 8, -0.2, 1, 1)):
        ex, ey = sx + dx * 28, sy + dy * 28
        branch = bezier((sx, sy), (sx + dx * 10, sy + dy * 2), (sx + dx * 18, sy + dy * 22), (ex, ey))
        d.line(branch, fill=WHITE, width=2)
        ang = math.atan2(ey - branch[-3][1], ex - branch[-3][0])
        sp = spiral(ex + 5 * math.cos(ang), ey + 5 * math.sin(ang), 6, 1, 0.85, ang + math.pi, cw=cw)
        d.line([branch[-1]] + sp, fill=WHITE, width=1)
        leaf(d, branch[10][0], branch[10][1], ang - 1.1 * cw, 9, WHITE)
        leaf(d, branch[18][0], branch[18][1], ang + 1.1 * cw, 8, WHITE)
    # leaves along the main stems
    for y in (26, 62, 102):
        leaf(d, 10, y, 0.35, 11, WHITE)
    for x in (26, 62, 102):
        leaf(d, x, 10, math.pi / 2 - 0.35, 11, WHITE)
    # the stems fade out toward their far ends
    fade = Image.new("L", (s, s), 255)
    fp = fade.load()
    for y in range(s):
        for x in range(s):
            t = max(x, y) / s
            fp[x, y] = 255 if t < 0.55 else clamp(255 * (1 - (t - 0.55) / 0.45))
    img.putalpha(ImageChops.multiply(img.split()[3], fade))
    save(img.filter(ImageFilter.GaussianBlur(0.4)), "Vine")


def scroll():
    """A banner for section headings: a pale strip of parchment with curled
    ends, a ragged top and bottom and a soft shadow."""
    w, h = 256, 64
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top, bot = 16, 46
    pts = []
    for x in range(22, 236):
        pts.append((x, top + random.uniform(-1.2, 1.2) + 1.5 * math.sin(x / 9)))
    for x in range(235, 21, -1):
        pts.append((x, bot + random.uniform(-1.2, 1.2) + 1.5 * math.sin(x / 7)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.polygon(pts, fill=(236, 218, 176, 255))
    # curled left end (darker roll) and torn right end
    bd.polygon([(10, top + 4), (22, top), (22, bot), (10, bot - 4)], fill=(205, 182, 136, 255))
    bd.line([(22, top), (22, bot)], fill=(150, 118, 72, 150), width=2)
    for y in range(top, bot):
        bd.line([(236, y), (236 + random.randrange(0, 7), y)], fill=(238, 224, 186, 255))
        bd.line([(236 + random.randrange(2, 9), y), (236 + random.randrange(8, 13), y)], fill=(210, 188, 140, random.randrange(60, 160)))
    # shading: darker towards the ends and edges, faint fibres
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(22, 60):
        sd.line([(x, 0), (x, h)], fill=(90, 60, 30, int(80 * (1 - (x - 22) / 38))))
    for x in range(200, 246):
        sd.line([(x, 0), (x, h)], fill=(90, 60, 30, int(60 * ((x - 200) / 46))))
    for y in range(0, h):
        e = min(abs(y - top), abs(y - bot))
        if e < 5:
            sd.line([(0, y), (w, y)], fill=(90, 60, 30, int(40 * (1 - e / 5))))
    for _ in range(40):
        x, y = random.randrange(22, 236), random.randrange(top, bot)
        sd.line([(x, y), (x + random.randrange(3, 9), y + random.randrange(-1, 2))], fill=(140, 110, 70, 30))
    body = masked(body, shade)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(p[0] + 2, p[1] + 3) for p in pts], fill=(40, 20, 5, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, sh)
    img = Image.alpha_composite(img, body)
    save(img, "Scroll")


def dropcap():
    """An illuminated initial: a coloured field (tinted in-game) and a gilt frame
    with scrollwork. The letter itself is drawn with a font string."""
    s = 64
    field = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    fd = ImageDraw.Draw(field)
    fd.rounded_rectangle((6, 6, s - 6, s - 6), radius=5, fill=WHITE)
    # a lighter centre so the tint looks lit from within
    glow = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(26, 0, -2):
        gd.ellipse((32 - r, 32 - r, 32 + r, 32 + r), fill=(255, 255, 255, 6))
    field = masked(field, glow)
    # faint diagonal hatching for a cloth-of-gold feel
    hatch = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hatch)
    for k in range(-s, s, 4):
        hd.line([(k, 0), (k + s, s)], fill=(0, 0, 0, 14))
    field = masked(field, hatch)
    save(field, "DropCapField")

    frame = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    gold = (214, 170, 82, 255)
    dark = (110, 76, 28, 255)
    light = (250, 226, 160, 255)
    d.rounded_rectangle((3, 3, s - 3, s - 3), radius=7, outline=dark, width=5)
    d.rounded_rectangle((4, 4, s - 4, s - 4), radius=6, outline=gold, width=3)
    d.rounded_rectangle((5, 5, s - 5, s - 5), radius=5, outline=light, width=1)
    d.rounded_rectangle((8, 8, s - 8, s - 8), radius=3, outline=dark, width=1)
    # corner bosses and little tendrils reaching into the field
    for (cx, cy, sx, sy) in ((9, 9, 1, 1), (s - 9, 9, -1, 1), (9, s - 9, 1, -1), (s - 9, s - 9, -1, -1)):
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=dark)
        d.ellipse((cx - 3, cy - 3, cx + 2, cy + 2), fill=gold)
        d.point((cx - 1, cy - 1), fill=light)
        sp = spiral(cx + sx * 9, cy + sy * 9, 5, 1, 0.8, math.atan2(-sy, -sx), cw=sx * sy)
        d.line([(cx + sx * 4, cy + sy * 4)] + sp, fill=gold, width=1)
    save(frame, "DropCapFrame")


def map_edge():
    """A ragged, toasted rim laid over the map so it looks like a chart glued
    into the book. Transparent in the middle."""
    w, h = 512, 256
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    n = noise((w, h), 6, 9)
    n2 = noise((w, h), 24, 6)
    rim = (74, 50, 26)
    for y in range(h):
        for x in range(w):
            e = min(x, w - 1 - x, (y) * 2, (h - 1 - y) * 2)  # in "horizontal pixels" so the band is even
            e = e + n[y * w + x] * 1.6 + n2[y * w + x]
            if e < 0:
                a = 255
            elif e < 30:
                a = int(255 * (1 - e / 30) ** 1.4)
            else:
                a = 0
            if a > 0:
                k = clamp(a * 0.25)
                px[x, y] = (rim[0] + k // 4, rim[1] + k // 5, rim[2] + k // 8, a)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w - 1, h - 1), outline=(30, 18, 8, 255), width=2)
    # a few pin-holes and a crease
    for (x, y) in ((14, 12), (w - 16, 10), (12, h - 14), (w - 14, h - 12)):
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(28, 16, 6, 230))
        d.ellipse((x - 2, y - 2, x + 1, y + 1), fill=(120, 90, 50, 255))
    save(img, "MapEdge")


def compass():
    s = 256
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    d.ellipse((c - 118, c - 118, c + 118, c + 118), outline=WHITE, width=2)
    d.ellipse((c - 104, c - 104, c + 104, c + 104), outline=WHITE, width=1)
    for i in range(72):
        a = math.radians(i * 5)
        r0 = 108 if i % 6 else 100
        d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + 116 * math.cos(a), c + 116 * math.sin(a))], fill=WHITE, width=1)
    for k, (R, r) in enumerate(((96, 14), (62, 10))):
        for i in range(4):
            a = math.radians(i * 90 + (45 if k else 0))
            tip = (c + R * math.cos(a), c + R * math.sin(a))
            l = (c + r * math.cos(a - math.pi / 2), c + r * math.sin(a - math.pi / 2))
            rr = (c + r * math.cos(a + math.pi / 2), c + r * math.sin(a + math.pi / 2))
            d.polygon([tip, l, (c, c)], fill=WHITE)
            d.polygon([tip, rr, (c, c)], outline=WHITE)
    d.ellipse((c - 6, c - 6, c + 6, c + 6), fill=WHITE)
    save(img.filter(ImageFilter.GaussianBlur(0.4)), "Compass")


def bronze_disc(size, base, rim):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    c = size / 2
    tarn = noise((size, size), 4, 14)
    for y in range(size):
        for x in range(size):
            dx, dy = x + 0.5 - c, y + 0.5 - c
            r = (dx * dx + dy * dy) ** 0.5
            lim = c - 3
            if r <= lim + 1:
                t = max(0.0, 1 - ((dx + c * 0.3) ** 2 + (dy + c * 0.3) ** 2) ** 0.5 / (c * 1.3))
                k = 55 * t - (r / lim) ** 4 * 60 + tarn[y * size + x]
                col = (clamp(base[0] + k), clamp(base[1] + k * 0.9), clamp(base[2] + k * 0.6))
                a = 255 if r <= lim else int(255 * (lim + 1 - r))
                px[x, y] = (*col, a)
    d = ImageDraw.Draw(img)
    d.ellipse((3, 3, size - 3, size - 3), outline=(*rim, 255), width=2)
    d.ellipse((7, 7, size - 7, size - 7), outline=(*rim, 90), width=1)
    return img


def brass():
    save(bronze_disc(64, (168, 122, 58), (62, 40, 18)), "Brass")
    glyph = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    g = ImageDraw.Draw(glyph)
    g.line([(8, 8), (24, 24)], fill=WHITE, width=4)
    g.line([(24, 8), (8, 24)], fill=WHITE, width=4)
    save(glyph, "Cross")
    arrow = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    ImageDraw.Draw(arrow).polygon([(22, 6), (10, 16), (22, 26)], fill=WHITE)
    save(arrow, "Arrow")


def icons():
    # a cog for the settings ribbon
    s = 32
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = s / 2
    pts = []
    for i in range(80):
        a = i / 80 * 2 * math.pi
        r = 13 if (i % 10) < 5 else 9.5
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    d.polygon(pts, fill=WHITE)
    d.ellipse((c - 4, c - 4, c + 4, c + 4), fill=(0, 0, 0, 0))
    save(img, "Gear")
    # a magnifying glass for the search box
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((5, 5, 21, 21), outline=WHITE, width=3)
    d.line([(19, 19), (28, 28)], fill=WHITE, width=4)
    save(img, "Lens")


def corner():
    """A gilt corner guard with a curved inner edge, engraved scrollwork and rivets."""
    s = 64
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    gold = (176, 134, 66, 255)
    dark = (72, 48, 18, 255)
    light = (236, 204, 140, 255)
    # body: an L whose inner corner is scooped out in a quarter circle
    d.rectangle((0, 0, 62, 18), fill=gold)
    d.rectangle((0, 0, 18, 62), fill=gold)
    d.pieslice((18 - 14, 18 - 14, 18 + 14, 18 + 14), 0, 90, fill=gold)
    d.pieslice((18 - 12, 18 - 12, 18 + 12, 18 + 12), 0, 90, fill=(0, 0, 0, 0))
    d.pieslice((18 - 12, 18 - 12, 18 + 12, 18 + 12), 0, 90, fill=gold)
    # tapered ends
    d.polygon([(62, 0), (62, 18), (54, 18), (62, 10)], fill=(0, 0, 0, 0))
    d.polygon([(0, 62), (18, 62), (18, 54), (10, 62)], fill=(0, 0, 0, 0))
    # tarnish
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for _ in range(30):
        x, y = random.randrange(s), random.randrange(s)
        ld.line([(x, y), (x + random.randrange(-8, 9), y + random.randrange(-8, 9))], fill=(40, 24, 8, random.randrange(20, 55)))
    img = masked(img, layer)
    d = ImageDraw.Draw(img)
    # edges: dark outline with a light bevel on the outer side
    d.line([(0, 18), (30, 18)], fill=dark, width=1)
    d.line([(18, 30), (18, 62)], fill=dark, width=1)
    d.arc((6, 6, 30, 30), 0, 90, fill=dark, width=1)
    d.line([(0, 1), (62, 1)], fill=light, width=1)
    d.line([(1, 0), (1, 62)], fill=light, width=1)
    # engraved scrollwork along each arm
    for pts in (bezier((30, 9), (40, 3), (48, 15), (56, 9)), bezier((9, 30), (3, 40), (15, 48), (9, 56))):
        d.line(pts, fill=dark, width=1)
        d.line([(p[0] + 1, p[1] + 1) for p in pts], fill=(light[0], light[1], light[2], 120), width=1)
    d.line(spiral(40, 9, 4, 0.5, 0.8, math.pi), fill=dark, width=1)
    d.line(spiral(9, 40, 4, 0.5, 0.8, -math.pi / 2), fill=dark, width=1)
    for (x, y) in ((7, 7), (52, 9), (9, 52)):  # rivets
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=dark)
        d.ellipse((x - 3, y - 3, x + 2, y + 2), fill=gold)
        d.ellipse((x - 2, y - 2, x, y), fill=light)
    save(img, "Corner")


def strap():
    """A leather strap with stitched edges and a brass buckle, laid across the cover."""
    w, h = 128, 32
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    n = noise((w, h), 4, 10)
    px = img.load()
    for y in range(6, 26):
        for x in range(0, 104):
            k = n[y * w + x] - (abs(y - 16) / 10) ** 3 * 30
            px[x, y] = (clamp(66 + k), clamp(36 + k * 0.7), clamp(18 + k * 0.5), 255)
    d.rectangle((0, 6, 103, 25), outline=(20, 10, 4, 255), width=1)
    for x in range(4, 100, 6):  # stitching
        d.line([(x, 9), (x + 3, 9)], fill=(210, 176, 112, 220), width=1)
        d.line([(x, 22), (x + 3, 22)], fill=(210, 176, 112, 220), width=1)
    # buckle
    gold = (184, 140, 68, 255)
    dark = (72, 48, 18, 255)
    d.rounded_rectangle((100, 3, 124, 28), radius=4, fill=dark)
    d.rounded_rectangle((102, 5, 122, 26), radius=3, fill=gold)
    d.rounded_rectangle((106, 9, 118, 22), radius=2, fill=(0, 0, 0, 0))
    d.rounded_rectangle((106, 9, 118, 22), radius=2, outline=dark, width=1)
    d.line([(103, 16), (116, 16)], fill=dark, width=3)
    d.line([(103, 15), (115, 15)], fill=(236, 204, 140, 255), width=1)
    d.line([(104, 7), (120, 7)], fill=(236, 204, 140, 160), width=1)
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((2, 9, 124, 29), fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(2.5))
    save(Image.alpha_composite(sh, img), "Strap")


def lace():
    """Binding cord crossing the spine, tiled vertically."""
    w, h = 32, 32
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for (p0, p1) in (((4, 2), (28, 30)), ((28, 2), (4, 30))):
        d.line([p0, p1], fill=(30, 16, 6, 200), width=6)
        d.line([p0, p1], fill=(196, 160, 104, 255), width=4)
        d.line([p0, p1], fill=(236, 208, 150, 200), width=1)
    # eyelets at the edges
    for (x, y) in ((4, 2), (28, 2), (4, 30), (28, 30)):
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(60, 40, 16, 255))
        d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(20, 10, 4, 255))
    save(img, "Lace")


def stitch():
    w, h = 32, 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(2, 4), (14, 4)], fill=(215, 180, 115, 230), width=2)
    d.line([(18, 4), (30, 4)], fill=(215, 180, 115, 230), width=2)
    for x in (1, 15, 17, 31):
        d.point((x, 4), fill=(20, 10, 4, 150))
    save(img, "Stitch")
    save(img.rotate(90, expand=True), "StitchV")


def diamond():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    ImageDraw.Draw(img).polygon([(8, 2), (14, 8), (8, 14), (2, 8)], fill=WHITE)
    save(img, "Diamond")


if __name__ == "__main__":
    parchment()
    leather()
    ribbon()
    flourish()
    rule()
    vine()
    scroll()
    dropcap()
    map_edge()
    compass()
    brass()
    icons()
    corner()
    strap()
    lace()
    stitch()
    diamond()
