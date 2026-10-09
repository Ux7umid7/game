"""Island cottage (from the reference picture) in three variants, with an enterable interior.

The variants follow the game story — find the old house, repair it, upgrade it:
  ruined   "Eski uy"          holes in the roof, boarded windows, overgrown, broken furniture
  cottage  "Ta'mirlangan uy"  the reference: blue slate roof, glowing windows, fire, cosy room
  upgraded "Kengaytirilgan"   terracotta roof, greenhouse, flower boxes, fence, more furniture

Axes: front door faces -Y, +Z up, origin = centre of the footprint at ground level. Metres.
"""
import math
import random
import bpy
from mathutils import Matrix, Vector
import wb
import h_props as P

HX, HY, T = 2.6, 3.5, 0.25          # half outer width (x), half outer depth (y), wall thickness
FZ = 0.45                           # top of the floor slab
F0 = FZ + 0.03                      # walking surface (top of the floor planks)
EZ = 3.3                            # top of the side walls (eaves)
PITCH = math.radians(48)
TAN, C, S = math.tan(PITCH), math.cos(PITCH), math.sin(PITCH)
RZ = EZ + HX * TAN                  # ridge height (underside of the roof deck)
EAVE_OV, GABLE_OV = 0.5, 0.4

STONES = ("stone_a", "stone_b", "stone_c")
PLANKS = ("plank_a", "plank_b", "plank_c")
LEAVES = ("leaf_a", "leaf_b", "leaf_c")

WALLS = {  # local frame per wall: u along the wall, local -Y = outside, 0..T = wall thickness
    "F": Matrix.Translation((0, -HY, 0)),
    "B": Matrix.Translation((0, HY, 0)) @ Matrix.Rotation(math.pi, 4, "Z"),
    "L": Matrix.Translation((-HX, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"),
    "R": Matrix.Translation((HX, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"),
}
WALL_HALF = {"F": HX, "B": HX, "L": HY, "R": HY}

# wall, kind, u, z0, width, height, arched, shutters      (L: u = -y, R: u = y, B: u = -x)
OPENINGS = [
    ("F", "door", 0.7, F0, 1.05, 2.15, True, False),
    ("F", "win", -1.45, 1.35, 0.8, 1.05, True, False),
    ("F", "win", 0.0, 4.05, 0.72, 0.95, True, True),
    ("B", "win", -1.6, 1.42, 0.8, 0.9, False, False),
    ("B", "win", 0.0, 4.35, 0.5, 0.55, True, False),
    ("L", "win", 2.0, 1.3, 0.85, 1.15, True, True),
    ("L", "win", -0.3, 1.3, 0.85, 1.15, True, False),
    ("R", "win", -0.8, 1.3, 0.85, 1.15, True, True),
]

DORMER = dict(yc=-0.9, xf=-1.85, hw=0.5, ov=0.15)
CHIMNEY = (-1.72, -0.88, 2.55, 3.45)  # x0, x1, y0, y1

VARIANTS = {
    "ruined": dict(prefix="HR_", seed=11, plaster="plaster_old", timber="timber_old",
                   tiles=("slate_old", "slate_a", "slate_c"), moss=0.16, missing=0.12, hole=True,
                   glow=False, ivy=1.8, porch="broken", shed="collapsed", interior="ruined", dormer=False,
                   chimney_top=5.9, shutter_mat="timber_old", door_mat="timber_old", door_open=(62, 6),
                   extras=("weeds",)),
    "cottage": dict(prefix="HC_", seed=7, plaster="plaster", timber="timber",
                    tiles=("slate_a", "slate_b", "slate_c"), moss=0.03, missing=0.0, hole=False,
                    glow=True, ivy=1.0, porch="full", shed="full", interior="cozy", dormer=True,
                    chimney_top=7.15, shutter_mat="timber", door_mat="plank_a", door_open=(28, 0),
                    extras=("pots",)),
    "upgraded": dict(prefix="HU_", seed=5, plaster="plaster_new", timber="timber",
                     tiles=("terra_a", "terra_b", "terra_c"), moss=0.0, missing=0.0, hole=False,
                     glow=True, ivy=0.45, porch="full", shed="full", interior="full", dormer=True,
                     chimney_top=7.15, shutter_mat="paint_teal", door_mat="paint_teal", door_open=(30, 0),
                     extras=("greenhouse", "fence", "flowers", "vane", "bench", "mailbox", "basket", "pots")),
}

BEVEL = {  # builder: (width, segments, smooth)
    "Floor": (0.006, 1, True), "Stone": (0.03, 1, True), "Timber": (0.015, 2, True),
    "Roof_Deck": (0.008, 1, True), "Dormer": (0.015, 2, True), "Roof_Tiles": (0.01, 1, True), "Ridge": (0.02, 2, True),
    "Windows": (0.008, 1, True), "Glass": (0.0, 1, True), "Ivy": (0.0, 1, False), "Chimney": (0.025, 1, True),
    "Fireplace": (0.025, 1, True), "Porch": (0.015, 2, True), "Shed": (0.012, 1, True),
    "Firewood": (0.0, 1, True), "Lantern": (0.004, 1, True), "Interior": (0.01, 1, True),
    "Fire": (0.0, 1, False), "Yard": (0.008, 1, True), "Greenhouse": (0.008, 1, True),
}


def roof_z(x):
    """Height of the main roof plane (underside of the deck) above world x."""
    return RZ - abs(x) * TAN


def opening(x0, x1, z0, z1, arch, n=12):
    if not arch:
        return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    r = (x1 - x0) / 2
    zs = z1 - r
    return [(x0, z0), (x1, z0), (x1, zs)] + wb.arc((x0 + x1) / 2, zs, r, 0, 180, n)[1:-1] + [(x0, zs)]


class Ctx:
    def __init__(self, prefix, M, cfg):
        self.p, self.M, self.cfg = prefix, M, cfg
        self.rng = random.Random(cfg["seed"])
        self.B = {}

    def __getitem__(self, name):
        if name not in self.B:
            self.B[name] = wb.Builder(self.p + name)
        return self.B[name]


def stone_rows(B, M, rng, u0, u1, z0, z1, y=-0.035, depth=0.12, rowh=(0.2, 0.3), lens=(0.28, 0.6), gap=0.025,
               skip=None, mats=STONES):
    z = z0
    while z < z1 - 0.04:
        hh = min(rng.uniform(*rowh), z1 - z)
        u = u0 - rng.uniform(0, 0.3)
        while u < u1:
            L = rng.uniform(*lens)
            a, b = max(u, u0), min(u + L, u1)
            if b - a > 0.08 and not (skip and skip(a, b, z, z + hh)):
                B.box(((a + b) / 2, y + rng.uniform(-0.01, 0.01), z + hh / 2), (b - a - gap, depth, hh - gap),
                      M[rng.choice(mats)])
            u += L
        z += hh


# ====================================================================== shell
def build_floor(k):
    M, rng, Fl = k.M, k.rng, k["Floor"]
    Fl.box2((-HX, -HY, 0), (HX, HY, FZ), M["stone_b"])
    x = -HX + T
    while x < HX - T - 0.01:
        w = min(0.2, HX - T - x)
        y = -HY + T - rng.uniform(0, 1.5)
        while y < HY - T:
            L = rng.uniform(1.4, 2.4)
            a, b = max(y, -HY + T), min(y + L, HY - T)
            if b - a > 0.05:
                Fl.box2((x + 0.004, a + 0.004, FZ), (x + w - 0.004, b - 0.004, F0), M[rng.choice(PLANKS)])
            y += L
        x += w
    # wainscot on the long left wall and the front wall
    I = Fl
    I.box2((-HX + T, -HY + T, F0), (-HX + T + 0.03, HY - T, F0 + 0.85), M["plank_b"])
    I.box2((-HX + T, -HY + T, F0 + 0.85), (-HX + T + 0.06, HY - T, F0 + 0.9), M["timber_dk"])
    for x0, x1 in ((-HX + T, 0.0), (1.4, HX - T)):
        I.box2((x0, -HY + T, F0), (x1, -HY + T + 0.03, F0 + 0.85), M["plank_b"])
        I.box2((x0, -HY + T, F0 + 0.85), (x1, -HY + T + 0.06, F0 + 0.9), M["timber_dk"])


def build_walls(k):
    W, pm = k["Walls"], k.M[k.cfg["plaster"]]
    for key in ("F", "B"):
        W.push(WALLS[key])
        W.prism([(-HX, 0), (HX, 0), (HX, EZ), (0, RZ), (-HX, EZ)], T, pm, "XZ", T / 2)
        W.pop()
    for key in ("L", "R"):
        W.push(WALLS[key])
        W.box((0, T / 2, EZ / 2), (2 * (HY - T), T, EZ), pm)
        W.pop()


def build_openings(k):
    names = ("Cut", "Windows", "Glass", "Stone")
    for (wall, kind, u, z0, w, h, arch, shut) in OPENINGS:
        for n in names:
            k[n].push(WALLS[wall])
        k["Cut"].prism(opening(u - w / 2, u + w / 2, z0, z0 + h, arch), 1.2, None, "XZ", T / 2)
        if kind == "door":
            door(k, wall, u, z0, w, h)
        else:
            window(k, u, z0, w, h, arch, shut)
        for n in names:
            k[n].pop()


def window(k, u, z0, w, h, arch, shut, cutless=False):
    M, cfg, rng = k.M, k.cfg, k.rng
    Wn, G, St = k["Windows"], k["Glass"], k["Stone"]
    fm = M[cfg["timber"]]
    fw = 0.08
    x0, x1, z1 = u - w / 2, u + w / 2, z0 + h
    zs = z1 - w / 2 if arch else z1
    fy, fd = (0.06, 0.2) if not cutless else (-0.03, 0.06)
    Wn.box((x0 + fw / 2, fy, (z0 + zs) / 2), (fw, fd, zs - z0), fm)
    Wn.box((x1 - fw / 2, fy, (z0 + zs) / 2), (fw, fd, zs - z0), fm)
    Wn.box((u, fy, z0 + fw / 2), (w, fd, fw), fm)
    if arch:
        Wn.prism(wb.arc(u, zs, w / 2, 0, 180, 12) + wb.arc(u, zs, w / 2 - fw, 180, 0, 12), fd, fm, "XZ", fy)
        top_in = zs + w / 2 - fw
    else:
        Wn.box((u, fy, z1 - fw / 2), (w, fd, fw), fm)
        top_in = z1 - fw
    ruined = cfg["interior"] == "ruined"
    gy = 0.08 if not cutless else -0.035
    if not ruined or rng.random() < 0.45:
        G.prism(opening(x0 + fw, x1 - fw, z0 + fw, top_in, arch), 0.012,
                M["glass_warm"] if cfg["glow"] else M["glass_dark"], "XZ", gy)
    Wn.box((u, gy, (z0 + fw + top_in) / 2), (0.035, 0.05, top_in - z0 - fw), fm)
    Wn.box((u, gy, z0 + fw + (zs - z0 - fw) * 0.55), (w - 2 * fw, 0.05, 0.035), fm)
    St.box((u, -0.07, z0 - 0.04), (w + 0.24, 0.22, 0.1), M["stone_c"])
    if not cutless:
        Wn.box((u, T + 0.03, z0 + 0.01), (w + 0.1, 0.1, 0.04), M["plank_a"])
    if shut:
        shutters(k, u, z0, w, h, arch, ruined)
    if ruined and not cutless:
        for i in range(rng.randint(2, 3)):
            Wn.box((u + rng.uniform(-0.05, 0.05), -0.085, z0 + h * (0.22 + 0.27 * i)), (w + 0.28, 0.035, 0.13),
                   M[rng.choice(("plank_b", "timber_old"))], rot=(0, rng.uniform(-25, 25), 0))


def shutters(k, u, z0, w, h, arch, ruined):
    M = k.M
    Wn, sm = k["Windows"], M[k.cfg["shutter_mat"]]
    sw = w / 2 + 0.05
    sh = h - (w * 0.18 if arch else 0)
    for side in (-1, 1):
        if ruined and side == 1:
            continue
        xc = u + side * (w / 2 + 0.06 + sw / 2)
        L = Matrix.Translation((xc, -0.05, z0 + sh / 2))
        if ruined:
            L = L @ wb.rotm((0, -side * 14, 0))
        for i in range(3):
            Wn.box((-sw / 2 + sw / 6 + i * sw / 3, 0, 0), (sw / 3 - 0.012, 0.04, sh), sm, L=L)
        for zz in (-sh * 0.33, sh * 0.33):
            Wn.box((0, -0.03, zz), (sw - 0.04, 0.025, 0.08), sm, L=L)
            Wn.box((-side * sw * 0.2, -0.046, zz), (sw * 0.6, 0.012, 0.03), M["iron"], L=L)


def door(k, wall, u, z0, w, h):
    M, cfg, rng = k.M, k.cfg, k.rng
    St, Wn = k["Stone"], k["Windows"]
    r = w / 2
    zs = z0 + h - r
    # stone surround: jamb blocks + arched voussoirs
    z, i = z0 - 0.03, 0
    while z < zs - 0.05:
        hh = min(0.3, zs - z)
        for side in (-1, 1):
            bw = 0.3 if (i + (side > 0)) % 2 == 0 else 0.2
            St.box((u + side * (r + bw / 2 + 0.01), -0.03, z + hh / 2), (bw, 0.13, hh - 0.025), M[rng.choice(STONES)])
        z += hh
        i += 1
    n = 9
    for j in range(n):
        a0, a1 = math.radians(180 * j / n + 1.2), math.radians(180 * (j + 1) / n - 1.2)
        ro = r + (0.32 if j == n // 2 else 0.25)
        pts = [(u + r * math.cos(a0), zs + r * math.sin(a0)), (u + ro * math.cos(a0), zs + ro * math.sin(a0)),
               (u + ro * math.cos(a1), zs + ro * math.sin(a1)), (u + r * math.cos(a1), zs + r * math.sin(a1))]
        St.prism(pts, 0.13, M[rng.choice(STONES)], "XZ", -0.03)
    St.box((u, 0.05, z0 - 0.02), (w + 0.1, 0.4, 0.06), M["stone_b"])
    # timber lining inside the opening
    fw = 0.07
    tm = M[cfg["timber"]]
    Wn.box((u - r + fw / 2, T / 2 + 0.01, (z0 + zs) / 2), (fw, T, zs - z0), tm)
    Wn.box((u + r - fw / 2, T / 2 + 0.01, (z0 + zs) / 2), (fw, T, zs - z0), tm)
    Wn.prism(wb.arc(u, zs, r, 0, 180, 12) + wb.arc(u, zs, r - fw, 180, 0, 12), T, tm, "XZ", T / 2 + 0.01)
    # door leaf: separate object, origin on the hinge so it can be animated in the game
    dw, dh = w - 2 * fw - 0.01, h - fw - 0.005
    rd = dw / 2
    zsd = dh - rd
    D = wb.Builder(k.p + "Door")
    dm = M[cfg["door_mat"]]
    D.prism(opening(0, dw, 0, dh, True), 0.06, dm, "XZ", 0.0)
    for i in range(1, 5):
        x = dw * i / 5
        top = zsd + math.sqrt(max(rd * rd - (x - rd) ** 2, 0)) - 0.03
        for yy in (-0.031, 0.031):
            D.box((x, yy, top / 2 + 0.01), (0.012, 0.004, top - 0.03), M["timber_dk"])
    for zz in (0.35, dh * 0.62):
        D.box((dw * 0.42, -0.036, zz), (dw * 0.82, 0.01, 0.05), M["iron"])
        D.cyl((0.02, -0.03, zz - 0.06), (0.02, -0.03, zz + 0.06), 0.022, M["iron"], 10)
    ring = [(0.005 * math.cos(math.radians(a)), 0.045 + 0.005 * math.sin(math.radians(a))) for a in range(0, 361, 30)]
    D.lathe(ring, M["iron"], origin=(dw * 0.8, -0.05, 1.0), axis=(0, 1, 0), segs=16)
    D.box((dw * 0.8, -0.034, 1.05), (0.05, 0.01, 0.07), M["iron"])
    ang, sag = cfg["door_open"]
    MW = WALLS[wall] @ Matrix.Translation((u - r + fw + 0.005, 0.11, z0)) @ \
        Matrix.Rotation(math.radians(ang), 4, "Z") @ Matrix.Rotation(math.radians(sag), 4, "Y")
    D.finish(bevel=0.006, segs=1, matrix=MW)


def build_timber(k):
    M, tm = k.M, k.M[k.cfg["timber"]]
    Tb = k["Timber"]
    for key in "FBLR":
        half = WALL_HALF[key]
        Tb.push(WALLS[key])
        for s in (-1, 1):
            Tb.box((s * (half - 0.11), -0.035, (0.95 + EZ) / 2), (0.22, 0.09, EZ - 0.95), tm)
        if key == "F":
            for a, b in ((-half, 0.15 - 0.32), (1.25 + 0.32, half)):
                Tb.box(((a + b) / 2, -0.035, 1.0), (b - a, 0.09, 0.12), tm)
        else:
            Tb.box((0, -0.035, 1.0), (2 * half, 0.09, 0.12), tm)
        if key in "LR":
            Tb.box((0, -0.035, EZ - 0.1), (2 * half, 0.09, 0.2), tm)
        else:
            Tb.box((0, -0.04, EZ - 0.08), (2 * half + 0.12, 0.1, 0.2), tm)
            ztop = EZ + (HX - 1.35) * TAN - 0.06
            for s in (-1, 1):
                Tb.box((s * 1.35, -0.035, (EZ + ztop) / 2), (0.16, 0.08, ztop - EZ), tm)
        mids = {"L": (0.85,), "R": (-2.0, 0.5), "B": (0.5,), "F": ()}[key]
        for u in mids:
            Tb.box((u, -0.035, (1.06 + EZ - 0.2) / 2), (0.18, 0.08, EZ - 1.26), tm)
        Tb.pop()


def build_stone_band(k):
    M, rng, St = k.M, k.rng, k["Stone"]
    for key in "FBLR":
        half = WALL_HALF[key]
        St.push(WALLS[key])
        St.box((0, -0.03, 0.475), (2 * half + 0.24, 0.06, 0.95), M["mortar"])
        skip = (lambda a, b, za, zb: b > 0.05 and a < 1.35 and zb > 0.47) if key == "F" else None
        stone_rows(St, M, rng, -half - 0.12, half + 0.12, 0.0, 0.95, skip=skip)
        # stones peeking through the plaster (many more on the ruined house)
        rects = [(u - w / 2 - 0.35, u + w / 2 + 0.35, z0 - 0.3, z0 + h + 0.4)
                 for (wl, kd, u, z0, w, h, a, s) in OPENINGS if wl == key]
        n = 26 if k.cfg["interior"] == "ruined" else 7
        for _ in range(n):
            u, z = rng.uniform(-half + 0.35, half - 0.35), rng.uniform(1.25, EZ - 0.45)
            if any(a < u < b and c < z < d for a, b, c, d in rects):
                continue
            if k.cfg["interior"] == "ruined" and rng.random() < 0.5:
                stone_rows(St, M, rng, u - 0.3, u + 0.3, z - 0.25, z + 0.25, y=-0.01, depth=0.06,
                           rowh=(0.14, 0.2), lens=(0.18, 0.3))
            else:
                St.box((u, -0.012, z), (rng.uniform(0.16, 0.3), 0.05, rng.uniform(0.12, 0.2)), M[rng.choice(STONES)])
        St.pop()


# ====================================================================== roof
def tiles_and_deck(k, F, u0, u1, v0, v1, holes_t=(), holes_d=(), clip=None, rafters=True, deck=True,
                   tiles=True):
    M, rng, cfg = k.M, k.rng, k.cfg
    D, Tl = k["Roof_Deck"], k["Roof_Tiles"]
    D.push(F[0])
    Tl.push(F[0])

    def inside(hs, u, v):
        return any(a <= u <= b and c <= v <= d for a, b, c, d in hs)

    if deck:
        v = v0
        while v < v1 - 1e-3:
            vh = min(0.2, v1 - v)
            vc = v + vh / 2
            u = u0 - rng.uniform(0, 1.2)
            while u < u1:
                L = rng.uniform(1.3, 2.2)
                a, b = max(u, u0), min(u + L, u1)
                if b - a > 0.05 and not inside(holes_d, (a + b) / 2, vc) and (clip is None or clip(b, vc)):
                    D.box(((a + b) / 2, vc, 0.02), (b - a - 0.008, vh - 0.01, 0.04), M[rng.choice(PLANKS)])
                u += L
            v += 0.2
    if rafters:
        u = u0 + 0.12
        while u < u1 - 0.05:
            D.box((u, (v0 + v1) / 2 - 0.02, -0.065), (0.1, v1 - v0 - 0.04, 0.11), M[cfg["timber"]])
            u += 0.75
    if tiles:
        tl, tw, rs = 0.38, 0.34, 0.27
        v, row = v0 - 0.02, 0
        while v < v1 - 0.12:
            u = u0 - (tw / 2 if row % 2 else 0.0)
            while u < u1:
                uc, vc = u + tw / 2, v + tl / 2
                u += tw
                if uc - tw / 2 < u0 - 0.06 or uc + tw / 2 > u1 + 0.06:
                    continue
                if inside(holes_t, uc, vc) or rng.random() < cfg["missing"]:
                    continue
                if clip is not None and not (clip(uc - tw / 2, vc) and clip(uc + tw / 2, vc)):
                    continue
                mat = M["moss"] if rng.random() < cfg["moss"] else M[rng.choice(cfg["tiles"])]
                Tl.box((uc + rng.uniform(-0.01, 0.01), vc, 0.066), (tw * 0.93, tl, 0.026), mat,
                       rot=(-7 + rng.uniform(-1.5, 1.5), rng.uniform(-1.2, 1.2), rng.uniform(-3, 3)))
            v += rs
            row += 1
    D.pop()
    Tl.pop()


def barge(k, F, u0, u1, v0, v1, fascia=True):
    R, tm = k["Ridge"], k.M[k.cfg["timber"]]
    R.push(F[0])
    for u in (u0 + 0.04, u1 - 0.04):
        R.box((u, (v0 + v1) / 2, 0.02), (0.08, v1 - v0 + 0.06, 0.32), tm)
    if fascia:
        R.box(((u0 + u1) / 2, v0 + 0.03, -0.01), (u1 - u0, 0.06, 0.26), tm)
    R.pop()


def dormer_geom():
    d = DORMER
    zf = roof_z(d["xf"])
    ze = zf + 0.95
    zr = ze + d["hw"]
    zfe = zr - (d["hw"] + d["ov"])
    return zf, ze, zr, zfe, (zr + 0.02 - RZ) / TAN, (zfe - RZ) / TAN


def build_roof(k):
    M, cfg = k.M, k.cfg
    v0, v1 = -EAVE_OV / C, HX / C
    u0, u1 = -(HY + GABLE_OV), HY + GABLE_OV
    Lf = wb.frame((-HX, 0, EZ), (0, 1, 0), (C, 0, S))
    Rf = wb.frame((HX, 0, EZ), (0, 1, 0), (-C, 0, S))
    vL = lambda x: (x + HX) / C
    cx0, cx1, cy0, cy1 = CHIMNEY
    holes_t = [(cy0 - 0.1, cy1 + 0.15, vL(cx0) - 0.08, vL(cx1) + 0.08)]
    holes_d = list(holes_t)
    if cfg["dormer"]:
        d = DORMER
        zf, ze, zr, zfe, xr, xe = dormer_geom()
        holes_t.append((d["yc"] - d["hw"] + 0.05, d["yc"] + d["hw"] - 0.05, vL(d["xf"] + 0.05), vL(xr + 0.06)))
    if cfg["hole"]:
        holes_t.append((-1.9, 0.5, 0.6, 2.7))
        holes_d.append((-1.55, 0.15, 0.95, 2.35))
    tiles_and_deck(k, Lf, u0, u1, v0, v1, holes_t, holes_d)
    tiles_and_deck(k, Rf, u0, u1, v0, v1)
    for F in (Lf, Rf):
        barge(k, F, u0, u1, v0, v1)
        k["Ridge"].push(F[0])
        k["Ridge"].box((0, v1 - 0.12, 0.09), (u1 - u0, 0.3, 0.04), M["timber_dk"])
        k["Ridge"].pop()
    R = k["Ridge"]
    yl = HY + GABLE_OV + 0.12
    R.cyl((0, -yl, RZ + 0.14), (0, yl, RZ + 0.14), 0.17, M[cfg["timber"]], 16)
    for s in (-1, 1):
        R.cyl((0, s * yl, RZ + 0.14), (0, s * (yl + 0.012), RZ + 0.14), 0.15, M["end_grain"], 16)
    y = -HY
    while y < HY:
        if not (cfg["hole"] and k.rng.random() < 0.4):
            R.cyl((0, y - 0.035, RZ + 0.14), (0, y + 0.035, RZ + 0.14), 0.183, M["timber_dk"], 16)
        y += 0.9
    # interior roof structure: tie beams, king posts, struts
    D, tdk = k["Roof_Deck"], M["timber_dk"]
    kp_top = RZ - 0.15
    for yb in (-2.0, -0.2, 1.6):
        D.box((0, yb, EZ - 0.1), (2 * (HX - T), 0.16, 0.2), tdk)
        D.box((0, yb, (EZ + kp_top) / 2), (0.14, 0.14, kp_top - EZ), tdk)
        for s in (-1, 1):
            D.box((s * 0.635, yb, 3.95), (0.1, 0.1, 1.72), tdk, rot=(0, -s * 41, 0))


def build_dormer(k):
    M, cfg, d = k.M, k.cfg, DORMER
    yc, xf, hw, ov = d["yc"], d["xf"], d["hw"], d["ov"]
    zf, ze, zr, zfe, xr, xe = dormer_geom()
    W, pm = k["Dormer"], M[cfg["plaster"]]  # own object: keeps it out of the wall boolean
    W.prism([(yc - hw, zf - 0.15), (yc + hw, zf - 0.15), (yc + hw, ze), (yc, zr), (yc - hw, ze)], 0.14, pm, "YZ",
            xf + 0.07)
    x_e = (ze - RZ) / TAN
    for s in (-1, 1):
        W.prism([(xf, zf - 0.15), (xf, ze), (x_e, ze)], 0.1, pm, "XZ", yc + s * (hw - 0.05))
    DF = Matrix.Translation((xf, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z")
    for n in ("Windows", "Glass", "Stone"):
        k[n].push(DF)
    window(k, -yc, zf + 0.14, 0.5, 0.66, True, False, cutless=True)
    for n in ("Windows", "Glass", "Stone"):
        k[n].pop()
    for s in (-1, 1):
        pts = [(xf - ov, yc + s * (hw + ov), zfe), (xf - ov, yc, zr + 0.02), (xr, yc, zr + 0.02),
               (xe, yc + s * (hw + ov), zfe)]
        n = (Vector(pts[1]) - Vector(pts[0])).cross(Vector(pts[2]) - Vector(pts[0]))
        if n.z < 0:
            pts.reverse()
        k["Roof_Deck"].slab(pts, 0.05, M["plank_b"])
        O = Vector((xf - ov, yc + s * (hw + ov), zfe))
        F = wb.frame(O, (1, 0, 0), (0, -s, 1))
        Mf, r, dd, nn = F
        span = (hw + ov) * math.sqrt(2)

        def clip(u, v, O=O, r=r, dd=dd):
            p = O + r * u + dd * v
            return p.z + 0.03 > roof_z(p.x) + 0.08

        ub = (xr - O.x) * r.x
        tiles_and_deck(k, F, min(0.0, ub), max(0.0, ub), 0.0, span, clip=clip, rafters=False, deck=False)
    k["Ridge"].cyl((xf - ov - 0.05, yc, zr + 0.11), (xr, yc, zr + 0.11), 0.075, M[cfg["timber"]], 12)


# ====================================================================== chimney + fireplace
def build_chimney(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    ch = k["Chimney"]
    x0, x1, y0, y1 = CHIMNEY
    top = cfg["chimney_top"]
    ch.box2((x0, y0, 2.0), (x1, y1, top), M["mortar"])
    ruined = cfg["interior"] == "ruined"
    skip = (lambda a, b, za, zb: zb > top - 0.55 and rng.random() < 0.45) if ruined else None
    faces = [
        (Matrix.Translation((0, y0, 0)), x0, x1, 2.0),
        (Matrix.Translation((x0, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"), -y1, -y0, 2.0),
        (Matrix.Translation((x1, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"), y0, y1, 2.0),
        (Matrix.Translation((0, y1, 0)) @ Matrix.Rotation(math.pi, 4, "Z"), -x1, -x0, roof_z(x0) - 0.1),
    ]
    for Mf, u0, u1, zs in faces:
        ch.push(Mf)
        stone_rows(ch, M, rng, u0 - 0.03, u1 + 0.03, zs, top, y=-0.02, depth=0.07, rowh=(0.18, 0.26),
                   lens=(0.2, 0.42), skip=skip)
        ch.pop()
    if not ruined:
        ch.box2((x0 - 0.08, y0 - 0.08, top), (x1 + 0.08, y1 + 0.08, top + 0.12), M["stone_b"])
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ch.cyl((cx, cy, top + 0.12), (cx, cy, top + 0.5), 0.13, M["copper"], 16, r2=0.12)
        ch.cyl((cx, cy, top + 0.46), (cx, cy, top + 0.54), 0.16, M["copper"], 16)


def build_fireplace(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    B = k["Fireplace"]
    md = M["mortar"]
    B.box2((-1.98, 2.3, F0), (-1.6, 3.25, 1.32), md)
    B.box2((-1.0, 2.3, F0), (-0.62, 3.25, 1.32), md)
    B.box2((-1.6, 2.95, F0), (-1.0, 3.25, 1.32), M["ash"])
    B.box2((-1.98, 2.3, 1.32), (-0.62, 3.25, 1.58), M["stone_b"])
    B.box2((-1.88, 2.42, 1.58), (-0.72, 3.25, 2.05), md)
    for Mf, u0, u1, z0, z1 in [
        (Matrix.Translation((0, 2.3, 0)), -1.98, -1.6, F0, 1.32),
        (Matrix.Translation((0, 2.3, 0)), -1.0, -0.62, F0, 1.32),
        (Matrix.Translation((0, 2.42, 0)), -1.88, -0.72, 1.58, 2.05),
        (Matrix.Translation((-1.98, 0, 0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z"), -3.25, -2.3, F0, 1.32),
        (Matrix.Translation((-0.62, 0, 0)) @ Matrix.Rotation(math.pi / 2, 4, "Z"), 2.3, 3.25, F0, 1.32),
    ]:
        B.push(Mf)
        stone_rows(B, M, rng, u0, u1, z0, z1, y=-0.02, depth=0.06, rowh=(0.16, 0.24), lens=(0.18, 0.36))
        B.pop()
    B.box2((-2.08, 2.22, 1.42), (-0.52, 2.62, 1.56), M["timber_dk"])
    B.box2((-2.1, 1.92, F0 - 0.02), (-0.5, 2.3, F0 + 0.06), M["stone_b"])
    B.box2((-1.6, 2.3, F0), (-1.0, 2.95, F0 + 0.04), M["ash"])
    P.fire(k["Fire"], M, (-1.3, 2.62, F0 + 0.04), lit=cfg["glow"])
    if cfg["glow"]:
        P.candle(k["Fire"], M, (-1.9, 2.42, 1.56))
        P.candle(k["Fire"], M, (-0.72, 2.42, 1.56), h=0.16)
        k["Interior"].cyl((-1.45, 2.45, 1.56), (-1.45, 2.45, 1.72), 0.05, M["clay"], 12)
        k["Interior"].cyl((-1.1, 2.48, 1.56), (-1.1, 2.48, 1.585), 0.11, M["ceramic"], 16)


# ====================================================================== porch, lantern, shed
def build_porch(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    St, Pb = k["Stone"], k["Porch"]
    tm = M[cfg["timber"]]
    x0, x1, yw, yf = -0.45, 2.25, -HY, -5.3
    broken = cfg["porch"] == "broken"
    St.box2((x0, yf, 0), (x1, yw, FZ - 0.04), M["mortar"])
    y = yf + 0.02
    while y < yw - 0.05:
        hh = min(rng.uniform(0.35, 0.55), yw - y)
        x = x0 + 0.02 - rng.uniform(0, 0.25)
        while x < x1 - 0.02:
            L = rng.uniform(0.35, 0.6)
            a, b = max(x, x0 + 0.02), min(x + L, x1 - 0.02)
            if b - a > 0.1 and not (broken and rng.random() < 0.15):
                St.box2((a + 0.012, y + 0.012, FZ - 0.05), (b - 0.012, y + hh - 0.012, FZ), M[rng.choice(STONES)])
            x += L
        y += hh
    for i in range(3):
        a = x0 + 0.1 + i * (x1 - x0 - 0.2) / 3
        St.box2((a + 0.01, yf - 0.36, 0), (a + (x1 - x0 - 0.2) / 3 - 0.01, yf, 0.22), M[rng.choice(STONES)])
    posts = [(x0 + 0.2, yf + 0.2), (x1 - 0.2, yf + 0.2)]
    for px, py in posts:
        St.box((px, py, FZ + 0.14), (0.46, 0.46, 0.27), M[rng.choice(STONES)])
        St.box((px, py, FZ + 0.42), (0.42, 0.42, 0.27), M[rng.choice(STONES)])
    Pb.box2((x0 - 0.1, yw - 0.1, 3.55), (x1 + 0.1, yw, 3.75), tm)
    py = yf + 0.2
    if broken:
        Pb.box((posts[0][0], py, 1.87), (0.2, 0.2, 1.74), tm, rot=(4, -3, 0))
        Pb.box((1.2, py + 0.25, FZ + 0.12), (0.2, 1.74, 0.2), tm, rot=(0, 0, 20))
        Pb.box((0.5, py + 0.15, 2.3), (1.5, 0.18, 0.2), tm, rot=(0, 28, 6))
        P.debris(Pb, M, rng, x0 + 0.3, x1 - 0.3, yf + 0.3, yw - 0.3, FZ, n=5)
        return
    for px, _ in posts:
        Pb.box((px, py, (1.0 + 2.74) / 2), (0.2, 0.2, 1.74), tm)
        for s in (-1, 1):
            if (px < 1 and s < 0) or (px > 1 and s > 0):
                continue
            Pb.box((px + s * 0.24, py, 2.52), (0.6, 0.12, 0.12), tm, rot=(0, s * 45, 0))
    Pb.box(((x0 + x1) / 2, py, 2.84), (x1 - x0 + 0.1, 0.18, 0.2), tm)
    F = wb.frame((0, -5.6, 2.85), (1, 0, 0), (0, 2.1, 0.9))
    Lp = math.hypot(2.1, 0.9)
    ua, ub = sorted(((x0 - 0.15) * F[1].x, (x1 + 0.15) * F[1].x))
    tiles_and_deck(k, F, ua, ub, 0.0, Lp)
    barge(k, F, ua, ub, 0.0, Lp)


def build_lantern(k):
    M, lit = k.M, k.cfg["glow"]
    L = k["Lantern"]
    x, y, z = -0.62, -HY, 2.4
    L.box((x, y - 0.012, z + 0.2), (0.1, 0.025, 0.24), M["iron"])
    L.box((x, y - 0.2, z + 0.28), (0.03, 0.38, 0.03), M["iron"])
    L.box((x, y - 0.12, z + 0.17), (0.025, 0.25, 0.025), M["iron"], rot=(-38, 0, 0))
    tilt = (12, 0, 0) if not lit else None
    P.at(L, (x, y - 0.36, z - 0.12), 0, tilt)
    P.hanging_lamp(L, M, (0, 0, 0), 0.4, lit=lit)
    L.pop()


def build_shed(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    Sh, FW = k["Shed"], k["Firewood"]
    tm = M[cfg["timber"]]
    xo, xi, y0, y1 = -4.25, -HX, 1.0, 3.5
    zo, zi = 2.0, 2.72
    O = (xo - 0.2, 0, zo)
    dvec = (xi - O[0], 0, zi - zo)
    zr = lambda x: zo + (x - O[0]) / dvec[0] * dvec[2]
    if cfg["shed"] == "collapsed":
        Sh.box((xo + 0.1, y0 + 0.05, 0.85), (0.15, 0.15, 1.7), tm, rot=(0, 14, 0))
        Sh.box((xo + 0.5, y1 - 0.4, 0.08), (0.15, 1.7, 0.15), tm, rot=(0, 0, 25))
        for i in range(9):
            Sh.box((xo + 0.9 + rng.uniform(-0.3, 0.3), y0 + 0.3 + i * 0.26, 0.45 + rng.uniform(-0.1, 0.1)),
                   (1.95, 0.2, 0.04), M[rng.choice(PLANKS)], rot=(rng.uniform(-4, 4), -24 + rng.uniform(-5, 5), 0))
        for _ in range(14):
            yy, xx = rng.uniform(y0, y1), rng.uniform(xo - 0.4, xi - 0.2)
            FW.cyl((xx - 0.22, yy, 0.07), (xx + 0.22, yy, 0.07), 0.065, M["bark"], 8)
        return
    F = wb.frame(O, (0, 1, 0), dvec)
    Lw = math.hypot(dvec[0], dvec[2])
    tiles_and_deck(k, F, y0 - 0.15, y1 + 0.15, 0.0, Lw)
    barge(k, F, y0 - 0.15, y1 + 0.15, 0.0, Lw)
    for yy in (y0 + 0.08, y1 - 0.08):
        Sh.box((xo + 0.1, yy, 0.89), (0.15, 0.15, 1.78), tm)
    Sh.box((xo + 0.1, (y0 + y1) / 2, 1.88), (0.16, y1 - y0 + 0.2, 0.2), tm)
    Sh.box2((xi - 0.1, y0 - 0.15, 2.5), (xi, y1 + 0.15, 2.66), tm)
    x = xo + 0.02
    while x < xi - 0.02:
        w = min(0.2, xi - x)
        top = zr(x + w / 2) - 0.12
        Sh.box((x + w / 2, y1 - 0.03, top / 2), (w - 0.012, 0.04, top), M[rng.choice(PLANKS)])
        x += w
    for cx in (-3.92, -3.42):
        z, row = 0.08, 0
        while z < 1.35:
            yy = y0 + 0.22 + (0.07 if row % 2 else 0.0)
            while yy < y1 - 0.2:
                r = rng.uniform(0.055, 0.075)
                L = 0.44 + rng.uniform(-0.03, 0.03)
                xs = cx + rng.uniform(-0.02, 0.02)
                FW.cyl((xs - L / 2, yy, z), (xs + L / 2, yy, z), r, M["bark"], 8)
                FW.cyl((xs - L / 2 - 0.005, yy, z), (xs - L / 2 + 0.003, yy, z), r * 0.88, M["end_grain"], 8)
                yy += 0.145
            z += 0.125
            row += 1
    bx, by = -3.55, 0.35
    FW.cyl((bx, by, 0), (bx, by, 0.5), 0.27, M["bark"], 14)
    FW.cyl((bx, by, 0.5), (bx, by, 0.507), 0.255, M["end_grain"], 14)
    FW.cyl((bx + 0.04, by, 0.5), (bx + 0.4, by - 0.06, 0.88), 0.022, M["plank_c"], 8)
    FW.box((bx + 0.03, by, 0.53), (0.2, 0.03, 0.12), M["iron"], rot=(0, -45, 0))
    for i in range(4):
        a = i * 85 + 20
        FW.cyl((bx + 0.5 * math.cos(math.radians(a)), by + 0.5 * math.sin(math.radians(a)), 0.07),
               (bx + 0.5 * math.cos(math.radians(a)) + 0.3, by + 0.5 * math.sin(math.radians(a)) + 0.1, 0.07),
               0.06, M["bark"], 8)


# ====================================================================== ivy
def ivy_wall(k, wall, starts):
    M, rng, amount = k.M, k.rng, k.cfg["ivy"]
    B = k["Ivy"]
    half = WALL_HALF[wall]
    rects = [(u - w / 2 - 0.02, u + w / 2 + 0.02, z0 - 0.12, z0 + h + 0.03)
             for (wl, kd, u, z0, w, h, a, s) in OPENINGS if wl == wall]

    def top_at(x):
        if wall in "FB":
            return EZ + max(0.0, (HX - abs(x))) * TAN - 0.25
        return EZ + 0.05

    def blocked(x, z):
        return abs(x) > half - 0.02 or z > top_at(x) or any(a < x < b and c < z < d for a, b, c, d in rects)

    B.push(WALLS[wall])
    for sx, sz, length in starts:
        stack = [(sx, sz, 90.0, length * (0.6 + 0.4 * amount), 0.02)]
        while stack:
            x, z, ang, L, r = stack.pop()
            for _ in range(int(L / 0.11)):
                ang = max(25.0, min(155.0, ang + rng.uniform(-22, 22)))
                nx, nz = x + 0.11 * math.cos(math.radians(ang)), z + 0.11 * math.sin(math.radians(ang))
                if abs(nx) > half - 0.02 or nz > top_at(nx):
                    break
                if not blocked(nx, nz) and not blocked(x, z):
                    B.cyl((x, -0.105, z), (nx, -0.105, nz), r, M["vine"], 5)
                for _ in range(int(rng.uniform(1.6, 3.6) * amount + 0.5)):
                    lx, lz = nx + rng.gauss(0, 0.085), nz + rng.gauss(0, 0.075)
                    if blocked(lx, lz):
                        continue
                    P.leaf(B, M[rng.choice(LEAVES)], (lx, -0.12 - rng.uniform(0, 0.05), lz),
                           rng.uniform(0.09, 0.16), rng.uniform(0, 360), rng.uniform(-35, 15))
                x, z = nx, nz
                r = max(0.008, r * 0.985)
                if rng.random() < 0.12 and L > 0.6:
                    stack.append((x, z, ang + rng.choice((-1, 1)) * rng.uniform(40, 75), L * 0.45, r * 0.8))
    B.pop()


def build_ivy(k):
    ivy_wall(k, "L", [(3.3, 0.2, 4.2), (0.85, 0.3, 3.6), (-0.75, 0.3, 3.0)])
    ivy_wall(k, "F", [(-2.42, 0.2, 4.6), (-0.15, 0.5, 3.0), (2.42, 0.3, 3.8)])
    if k.cfg["ivy"] > 1.5:
        ivy_wall(k, "R", [(-3.3, 0.2, 4.0), (1.2, 0.2, 3.4), (3.3, 0.2, 3.6)])
        ivy_wall(k, "B", [(2.3, 0.2, 4.4), (0.0, 0.2, 3.6), (-2.3, 0.2, 4.0)])
        ivy_wall(k, "L", [(2.0, 0.2, 3.6), (-2.6, 0.2, 3.0)])


# ====================================================================== interior
def build_interior(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    I = k["Interior"]
    mode = cfg["interior"]
    if mode == "ruined":
        P.bed(I, M, (-1.65, -3.22, F0), 0, mattress=False)
        P.at(I, (0.45, -0.2, F0 + 0.3), 20, (0, 27, 0))
        P.table(I, M, (0, 0, 0), 0)
        I.pop()
        P.chair(I, M, (1.35, 0.7, F0 + 0.22), 70, tilt=(90, 0, 0))
        P.crate(I, M, (2.0, -1.3, F0), 8)
        P.crate(I, M, (2.0, -1.9, F0), -12)
        P.crate(I, M, (2.0, -1.6, F0 + 0.5), 25, s=0.42)
        P.barrel(I, M, (1.4, 1.5, F0), 30, lying=True)
        P.counter(I, M, (2.05, 1.75, F0), -90, L=2.3, rng=rng)
        P.bookcase(I, M, (1.875, -3.08, F0), 180, rng=rng, broken=True)
        P.debris(I, M, rng, -1.8, 1.6, -2.4, 2.0, F0, 14)
        P.fallen_tiles(I, M, rng, -1.9, -0.5, -1.6, 0.2, F0, cfg["tiles"], n=16)
        P.scattered_leaves(I, M, rng, -2.2, 0.2, -2.4, 1.0, F0, 70)
        P.hanging_lamp(I, M, (0.55, -0.2, 2.35), EZ - 0.2, lit=False)
        return
    P.bed(I, M, (-1.65, -3.22, F0), 0)
    P.chest(I, M, (-1.65, -0.86, F0), 0)
    P.table(I, M, (0.55, -0.2, F0), 0)
    P.bench(I, M, (0.55, -0.85, F0), 0)
    P.chair(I, M, (0.55, 0.45, F0), 0)
    P.counter(I, M, (2.05, 1.75, F0), -90, L=2.3, rng=rng)
    P.wall_shelf(I, M, (2.23, 1.75, 1.95), -90, L=1.8, rng=rng)
    P.bookcase(I, M, (1.875, -3.08, F0), 180, rng=rng)
    P.armchair(I, M, (-0.25, 1.45, F0), -128)
    P.rug(I, M, (-1.25, 1.35, F0), 0)
    P.barrel(I, M, (2.0, -1.95, F0))
    P.crate(I, M, (2.02, -1.25, F0), 10)
    P.hanging_lamp(I, M, (0.55, -0.2, 2.45), EZ - 0.2, lit=True)
    P.candle(I, M, (0.3, -0.1, F0 + 0.76))
    P.mug(I, M, (0.75, -0.35, F0 + 0.76))
    P.mug(I, M, (0.9, -0.05, F0 + 0.76))
    I.cyl((0.55, -0.15, F0 + 0.76), (0.55, -0.15, F0 + 0.79), 0.16, M["ceramic"], 16)
    I.lathe([(0, 0.0), (0, 0.08), (0.06, 0.095), (0.14, 0.07), (0.17, 0.0)], M["end_grain"],
            origin=(0.47, -0.15, F0 + 0.8), axis=(1, 0, 0), segs=12)
    P.plant(I, M, rng, (-2.12, 0.9, F0), 1.5)
    P.plant(I, M, rng, (2.12, 1.45, F0 + 0.91), 0.7)
    if mode == "full":
        P.painting(I, M, (-HX + T + 0.03, -0.85, 2.15), 90)
        P.plant(I, M, rng, (1.1, -3.0, F0), 1.3)
        P.plant(I, M, rng, (2.12, 2.82, F0 + 0.91), 0.55)
        for i in range(4):
            x = 1.2 + i * 0.25
            I.cyl((x, 1.6, EZ - 0.2), (x, 1.6, EZ - 0.45), 0.004, M["vine"], 4)
            for j in range(5):
                P.leaf(I, M[rng.choice(LEAVES)], (x + rng.uniform(-0.04, 0.04), 1.6, EZ - 0.5 - j * 0.03), 0.1,
                       rng.uniform(150, 210), 0, yaw=rng.uniform(0, 180))


def add_lights(k):
    if not k.cfg["glow"]:
        return
    for name, loc, energy, col in (("LampLight", (0.55, -0.2, 2.5), 160, (1.0, 0.78, 0.5)),
                                   ("FireLight", (-1.3, 2.3, F0 + 0.45), 130, (1.0, 0.55, 0.25)),
                                   ("FillLight", (0.0, 0.0, EZ - 0.3), 90, (1.0, 0.85, 0.65)),
                                   ("PorchLight", (-0.62, -HY - 0.36, 2.35), 25, (1.0, 0.78, 0.5))):
        ld = bpy.data.lights.new(k.p + name, "POINT")
        ld.energy, ld.color, ld.shadow_soft_size = energy, col, 0.12
        ob = bpy.data.objects.new(k.p + name, ld)
        wb.CUR["coll"].objects.link(ob)
        ob.parent = wb.CUR["root"]
        ob.location = loc


# ====================================================================== yard + extras
def path_stones(k, Y):
    M, rng = k.M, k.rng
    y = -5.68
    n = 0
    while y > -8.6:
        for x in (0.62, 1.18):
            if k.cfg["interior"] == "ruined" and rng.random() < 0.35:
                continue
            s = rng.uniform(0.38, 0.52)
            Y.box((x + rng.uniform(-0.08, 0.08), y - s / 2, 0.02 + rng.uniform(0, 0.01)), (s, s * rng.uniform(0.8, 1.0), 0.05),
                  M[rng.choice(STONES)], rot=(0, 0, rng.uniform(-15, 15)))
        y -= 0.56
        n += 1


def flowers(k, B, cx, cy, cz, w, d, n):
    M, rng = k.M, k.rng
    for _ in range(n):
        x, y = cx + rng.uniform(-w / 2, w / 2), cy + rng.uniform(-d / 2, d / 2)
        h = rng.uniform(0.12, 0.26)
        B.cyl((x, y, cz), (x, y, cz + h), 0.006, M["leaf_c"], 4)
        B.box((x, y, cz + h), (0.055, 0.055, 0.055), M[rng.choice(("flower_red", "flower_yel", "flower_pur"))],
              rot=(45, 35, rng.uniform(0, 90)))
        P.leaf(B, M[rng.choice(LEAVES)], (x + 0.03, y, cz + h * 0.4), 0.08, rng.uniform(0, 360), -60,
               yaw=rng.uniform(0, 360))


def build_yard(k):
    M, rng, cfg = k.M, k.rng, k.cfg
    Y = k["Yard"]
    ex = cfg["extras"]
    path_stones(k, Y)
    if "pots" in ex:
        for x in (-0.25, 2.05):
            P.plant(Y, M, rng, (x, -5.8, 0.0), 1.8)
    if "weeds" in ex:
        for _ in range(55):
            side = rng.choice("FBLR")
            half = WALL_HALF[side]
            Y.push(WALLS[side])
            u = rng.uniform(-half - 0.3, half + 0.3)
            for _b in range(7):
                h = rng.uniform(0.25, 0.6)
                Y.poly([(-0.015, 0), (0.015, 0), (0.0, h)], M[rng.choice(("grass", "grass_dk"))], "XZ",
                        -0.25 - rng.uniform(0, 0.25),
                        L=Matrix.Translation((u + rng.uniform(-0.12, 0.12), 0, 0)) @
                        wb.rotm((rng.uniform(-20, 20), rng.uniform(-25, 25), rng.uniform(0, 180))))
            Y.pop()
        P.fallen_tiles(Y, M, rng, -3.2, -2.8, -3.5, 1.0, 0.0, cfg["tiles"], n=10)
        P.fallen_tiles(Y, M, rng, -1.0, 2.5, -4.6, -3.7, 0.45, cfg["tiles"], n=6)
        for i in range(3):
            Y.box((-1.9 + i * 0.35, -HY - 0.25, 1.05), (0.2, 0.04, 2.1), M[rng.choice(("plank_b", "timber_old"))],
                  rot=(-12, rng.uniform(-6, 6), 0))
    if "flowers" in ex:
        for wall, u, z0, w in (("L", 2.0, 1.3, 0.85), ("L", -0.3, 1.3, 0.85), ("F", -1.45, 1.35, 0.8)):
            Y.push(WALLS[wall])
            Y.box((u, -0.25, z0 - 0.2), (w + 0.18, 0.22, 0.18), M["paint_teal"])
            Y.box((u, -0.25, z0 - 0.105), (w + 0.1, 0.16, 0.02), M["dirt"])
            flowers(k, Y, u, -0.25, z0 - 0.1, w, 0.12, 14)
            Y.pop()
    if "fence" in ex:
        yf, pw = -8.4, M["paint_white"]
        for x0, x1 in ((-4.8, 0.3), (1.5, 4.8)):
            n = int((x1 - x0) / 0.16)
            for i in range(n + 1):
                x = x0 + i * (x1 - x0) / n
                Y.prism([(-0.04, 0), (0.04, 0), (0.04, 0.82), (0.0, 0.9), (-0.04, 0.82)], 0.025, pw, "XZ", yf,
                        L=Matrix.Translation((x, 0, 0)))
            for z in (0.25, 0.65):
                Y.box(((x0 + x1) / 2, yf + 0.03, z), (x1 - x0, 0.04, 0.07), pw)
            for x in (x0, x1):
                Y.box((x, yf, 0.5), (0.1, 0.1, 1.0), pw)
        for sx in (-4.8, 4.8):
            n = int(3.6 / 0.16)
            for i in range(n + 1):
                y = yf + i * 3.6 / n
                Y.prism([(-0.04, 0), (0.04, 0), (0.04, 0.82), (0.0, 0.9), (-0.04, 0.82)], 0.025, pw, "YZ", sx,
                        L=Matrix.Translation((0, y, 0)))
            for z in (0.25, 0.65):
                Y.box((sx + 0.03, yf + 1.8, z), (0.04, 3.6, 0.07), pw)
    if "mailbox" in ex:
        Y.box((1.85, -8.65, 0.55), (0.08, 0.08, 1.1), M["timber"])
        Y.box((1.85, -8.65, 1.17), (0.22, 0.42, 0.16), M["paint_teal"])
        Y.cyl((1.85, -8.86, 1.25), (1.85, -8.44, 1.25), 0.11, M["paint_teal"], 16)
        Y.box((1.97, -8.55, 1.32), (0.015, 0.04, 0.22), M["flower_red"])
    if "bench" in ex:
        P.bench(Y, M, (-2.2, -6.4, 0.0), 0, L=1.3)
        Y.box((-2.2, -6.25, 0.75), (1.3, 0.05, 0.3), M["plank_b"])
        for sx in (-0.5, 0.5):
            Y.box((-2.2 + sx, -6.25, 0.55), (0.05, 0.05, 0.6), M["timber"])
    if "vane" in ex:
        z0 = RZ + 0.3
        Y.cyl((0, -HY - 0.2, z0), (0, -HY - 0.2, z0 + 0.9), 0.015, M["iron"], 8)
        Y.cyl((0, -HY - 0.2, z0 + 0.5), (0, -HY - 0.2, z0 + 0.58), 0.04, M["copper"], 12)
        Y.prism([(-0.35, -0.02), (0.18, -0.02), (0.18, -0.07), (0.32, 0.0), (0.18, 0.07), (0.18, 0.02),
                 (-0.35, 0.02), (-0.42, 0.08), (-0.42, -0.08)], 0.01, M["copper"], "XZ", -HY - 0.2,
                L=Matrix.Translation((0, 0, z0 + 0.82)))
        for a in (0, 90):
            Y.box((0, -HY - 0.2, z0 + 0.66), (0.3, 0.012, 0.012), M["iron"], rot=(0, 0, a))
    if "basket" in ex:
        bx, by = 0.15, -5.1
        Y.cyl((bx, by, 2.74), (bx, by, 2.35), 0.006, M["iron"], 4)
        Y.cyl((bx, by, 2.2), (bx, by, 2.35), 0.17, M["clay"], 14, r2=0.2)
        flowers(k, Y, bx, by, 2.35, 0.28, 0.28, 10)
        for i in range(8):
            a = i * 45
            P.leaf(Y, M[rng.choice(LEAVES)], (bx + 0.2 * math.cos(math.radians(a)), by + 0.2 * math.sin(math.radians(a)),
                                             2.22), 0.12, 180, -70, yaw=a - 90)


def build_greenhouse(k):
    M, rng = k.M, k.rng
    G, Gl, St = k["Greenhouse"], k["Glass"], k["Stone"]
    xi, xo, y0, y1 = HX, 4.45, -2.1, 1.5
    zi, zo = 2.55, 1.95
    zr = lambda x: zi + (x - xi) / (xo - xi) * (zo - zi)
    wm, gm = M["paint_white"], M["glass_clear"]
    for p0, p1 in (((xo - 0.25, y0, 0), (xo, y1, 0.4)), ((xi, y0, 0), (xo, y0 + 0.25, 0.4)),
                   ((xi, y1 - 0.25, 0), (xo, y1, 0.4))):
        St.box2(p0, p1, M["stone_c"])
    for i in range(5):
        y = y0 + 0.06 + i * (y1 - y0 - 0.12) / 4
        G.box((xo - 0.06, y, (0.4 + zo) / 2), (0.08, 0.08, zo - 0.4), wm)
        ang = math.degrees(math.atan2(zi - zo, xo - xi))
        G.box(((xi + xo) / 2, y, (zi + zo) / 2 + 0.04), (math.hypot(xo - xi, zi - zo) + 0.1, 0.06, 0.08), wm,
              rot=(0, ang, 0))
    for x in (xi + 0.62, xi + 1.24):
        for y in (y0 + 0.06, y1 - 0.06):
            G.box((x, y, (0.4 + zr(x)) / 2), (0.07, 0.07, zr(x) - 0.4), wm)
    G.box(((xi + xo) / 2 + 0.06, y0 + 0.06, 0.45), (xo - xi, 0.07, 0.07), wm)
    G.box(((xi + xo) / 2 + 0.06, y1 - 0.06, 0.45), (xo - xi, 0.07, 0.07), wm)
    G.box((xo - 0.06, (y0 + y1) / 2, zo), (0.1, y1 - y0, 0.1), wm)
    Gl.box2((xo - 0.05, y0 + 0.05, 0.4), (xo - 0.03, y1 - 0.05, zo), gm)
    for y in (y0 + 0.07, y1 - 0.07):
        Gl.prism([(xi, 0.4), (xo - 0.05, 0.4), (xo - 0.05, zo), (xi, zi)], 0.015, gm, "XZ", y)
    pts = [(xi, y0, zi + 0.09), (xi, y1, zi + 0.09), (xo + 0.1, y1, zr(xo + 0.1) + 0.09),
           (xo + 0.1, y0, zr(xo + 0.1) + 0.09)]
    n = (Vector(pts[1]) - Vector(pts[0])).cross(Vector(pts[2]) - Vector(pts[0]))
    if n.z < 0:
        pts.reverse()
    Gl.slab(pts, 0.015, gm)
    G.box2((xo - 0.75, y0 + 0.35, 0.72), (xo - 0.3, y1 - 0.35, 0.77), M["plank_a"])
    for y in (y0 + 0.45, y1 - 0.45):
        for x in (xo - 0.7, xo - 0.35):
            G.box((x, y, 0.36), (0.05, 0.05, 0.72), M["timber"])
    y = y0 + 0.5
    while y < y1 - 0.45:
        P.plant(G, M, rng, (xo - 0.52, y, 0.77), 0.9)
        y += 0.42
    for y in (y0 + 0.6, y1 - 0.6):
        G.cyl((xi + 0.5, y, 0), (xi + 0.5, y, 0.25), 0.16, M["clay"], 12)
        G.cyl((xi + 0.5, y, 0.25), (xi + 0.5, y, 1.5), 0.012, M["timber"], 6)
        for j in range(14):
            P.leaf(G, M[rng.choice(LEAVES)], (xi + 0.5 + rng.uniform(-0.12, 0.12), y + rng.uniform(-0.12, 0.12),
                                             0.35 + j * 0.08), 0.14, rng.uniform(0, 360), rng.uniform(-50, 50),
                   yaw=rng.uniform(0, 360))
            if j % 4 == 2:
                G.cyl((xi + 0.5 + 0.08, y, 0.4 + j * 0.08), (xi + 0.5 + 0.08, y, 0.43 + j * 0.08), 0.03,
                      M["flower_red"], 10)


# ====================================================================== main
def build_house(name, variant, M, pack):
    cfg = VARIANTS[variant]
    root = wb.begin(name, pack)
    k = Ctx(cfg["prefix"], M, cfg)
    build_floor(k)
    build_walls(k)
    build_openings(k)
    build_timber(k)
    build_stone_band(k)
    build_roof(k)
    if cfg["dormer"]:
        build_dormer(k)
    build_chimney(k)
    build_fireplace(k)
    build_porch(k)
    build_lantern(k)
    build_shed(k)
    build_ivy(k)
    build_interior(k)
    build_yard(k)
    if "greenhouse" in cfg["extras"]:
        build_greenhouse(k)
    walls = k.B.pop("Walls").finish()
    cutter = k.B.pop("Cut").finish(smooth=False)
    wb.cut(walls, cutter, keep_bevel=(0.02, 2))
    for name_, B in k.B.items():
        bw, segs, sm = BEVEL.get(name_, (0.01, 1, True))
        B.finish(bevel=bw, segs=segs, smooth=sm)
    add_lights(k)
    return root
