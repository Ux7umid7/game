"""Furniture and small props for the house interiors (all drawn into a wb.Builder).

Every function places its prop at pos=(x, y, floor_z) rotated `rot` degrees about Z.
Local axes: -Y is the prop's front, +Z up, z=0 is the floor.
"""
import math
from mathutils import Matrix
import wb

LEAF = [(0, -0.5), (0.35, -0.2), (0.5, 0.15), (0.25, 0.35), (0, 0.55), (-0.25, 0.35), (-0.5, 0.15),
        (-0.35, -0.2)]


def at(B, pos, rot=0.0, tilt=None):
    M = Matrix.Translation(pos) @ Matrix.Rotation(math.radians(rot), 4, "Z")
    if tilt:
        M = M @ wb.rotm(tilt)
    B.push(M)


def leaf(B, mat, pos, size, spin, tilt, yaw=0.0):
    pts = [(x * size, z * size) for x, z in LEAF]
    L = Matrix.Translation(pos) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @ \
        Matrix.Rotation(math.radians(tilt), 4, "X") @ Matrix.Rotation(math.radians(spin), 4, "Y")
    B.poly(pts, mat, "XZ", 0.0, L)


# ------------------------------------------------------------------ furniture
def table(B, M, pos, rot=0, w=1.3, d=0.8, h=0.76):
    at(B, pos, rot)
    B.box((0, 0, h - 0.03), (w, d, 0.06), M["plank_a"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box((sx * (w / 2 - 0.09), sy * (d / 2 - 0.09), (h - 0.06) / 2), (0.08, 0.08, h - 0.06), M["timber"])
        B.box((sx * (w / 2 - 0.09), 0, h - 0.13), (0.04, d - 0.24, 0.09), M["timber"])
    for sy in (-1, 1):
        B.box((0, sy * (d / 2 - 0.09), h - 0.13), (w - 0.24, 0.04, 0.09), M["timber"])
    B.pop()


def bench(B, M, pos, rot=0, L=1.1):
    at(B, pos, rot)
    B.box((0, 0, 0.44), (L, 0.32, 0.05), M["plank_b"])
    for sx in (-1, 1):
        B.box((sx * (L / 2 - 0.12), 0, 0.21), (0.05, 0.28, 0.42), M["timber"])
    B.box((0, 0, 0.16), (L - 0.3, 0.04, 0.06), M["timber"])
    B.pop()


def chair(B, M, pos, rot=0, tilt=None):
    at(B, pos, rot, tilt)
    B.box((0, 0, 0.45), (0.44, 0.42, 0.05), M["plank_a"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box((sx * 0.18, sy * 0.17, 0.215), (0.045, 0.045, 0.43), M["timber"])
        B.box((sx * 0.18, 0.17, 0.72), (0.045, 0.045, 0.5), M["timber"])
    for z in (0.75, 0.9):
        B.box((0, 0.17, z), (0.36, 0.03, 0.08), M["plank_a"])
    B.pop()


def bed(B, M, pos, rot=0, mattress=True):
    at(B, pos, rot)
    W, Lb, tm = 1.4, 2.05, M["timber"]
    for sx in (-1, 1):
        B.box((sx * (W / 2 - 0.05), 0.05, 0.55), (0.1, 0.1, 1.1), tm)
        B.box((sx * (W / 2 - 0.05), Lb - 0.05, 0.38), (0.1, 0.1, 0.76), tm)
        B.box((sx * (W / 2 - 0.04), Lb / 2, 0.32), (0.06, Lb - 0.1, 0.18), tm)
    head = [(-W / 2 + 0.1, 0.36), (W / 2 - 0.1, 0.36)] + \
           [(math.cos(math.radians(a)) * (W / 2 - 0.1), 0.86 + 0.14 * math.sin(math.radians(a)))
            for a in range(0, 181, 15)]
    B.prism(head, 0.05, M["plank_a"], "XZ", 0.05)
    B.box((0, Lb - 0.05, 0.5), (W - 0.2, 0.05, 0.3), M["plank_a"])
    B.box((0, Lb / 2, 0.42), (W - 0.16, Lb - 0.14, 0.05), M["plank_b"])
    if mattress:
        B.box((0, Lb / 2 + 0.02, 0.54), (W - 0.18, Lb - 0.2, 0.18), M["fab_cream"])
        bl = Lb * 0.62
        yb = Lb - 0.1 - bl / 2
        B.box((0, yb, 0.645), (W - 0.12, bl, 0.05), M["fab_teal"])
        for sx in (-1, 1):
            B.box((sx * (W / 2 - 0.075), yb, 0.53), (0.03, bl, 0.24), M["fab_teal"])
        B.box((0, yb - bl / 2, 0.66), (W - 0.1, 0.12, 0.07), M["fab_mustard"])
        for sx in (-1, 1):
            B.box((sx * 0.3, 0.33, 0.69), (0.5, 0.3, 0.12), M["fab_cream"], rot=(10, 0, 0))
    B.pop()


def counter(B, M, pos, rot=0, L=2.3, rng=None):
    at(B, pos, rot)
    B.box((0, 0, 0.43), (L, 0.6, 0.86), M["timber"])
    B.box((0, -0.02, 0.885), (L + 0.04, 0.66, 0.05), M["plank_a"])
    n = int(L / 0.56)
    for i in range(n):
        x = -L / 2 + 0.28 + i * (L - 0.56) / max(n - 1, 1)
        B.box((x, -0.305, 0.46), (0.48, 0.02, 0.62), M["plank_c"])
        B.cyl((x + 0.17, -0.31, 0.62), (x + 0.17, -0.34, 0.62), 0.018, M["iron"], 8)
    B.box((L / 2 - 0.45, -0.02, 0.86), (0.5, 0.42, 0.12), M["ceramic"])
    B.box((L / 2 - 0.45, -0.02, 0.905), (0.42, 0.34, 0.04), M["ash"])
    B.cyl((L / 2 - 0.45, 0.2, 0.9), (L / 2 - 0.45, 0.2, 1.15), 0.02, M["iron"], 8)
    B.cyl((L / 2 - 0.45, 0.2, 1.15), (L / 2 - 0.45, 0.06, 1.12), 0.018, M["iron"], 8)
    B.cyl((-L / 2 + 0.35, 0.0, 0.91), (-L / 2 + 0.35, 0.0, 1.05), 0.13, M["copper"], 16)
    B.cyl((-L / 2 + 0.35, 0.0, 1.05), (-L / 2 + 0.35, 0.0, 1.07), 0.14, M["iron"], 16)
    B.box((-0.2, -0.05, 0.92), (0.4, 0.28, 0.025), M["plank_c"])
    B.lathe([(0, 0.0), (0, 0.07), (0.05, 0.085), (0.12, 0.06), (0.15, 0.0)], M["end_grain"],
            origin=(-0.2, -0.05, 0.935), axis=(1, 0, 0), segs=12)
    B.pop()


def wall_shelf(B, M, pos, rot=0, L=1.6, rng=None, items="jars"):
    at(B, pos, rot)
    B.box((0, 0, 0), (L, 0.24, 0.04), M["plank_a"])
    for sx in (-1, 1):
        B.prism([(0.0, 0.0), (0.0, -0.2), (-0.18, 0.0)], 0.04, M["timber"], "YZ", sx * (L / 2 - 0.1),
                L=Matrix.Translation((0, 0.12, -0.02)))
    x = -L / 2 + 0.12
    while x < L / 2 - 0.1:
        h = rng.uniform(0.1, 0.22) if rng else 0.15
        r = rng.uniform(0.04, 0.07) if rng else 0.05
        mat = M[rng.choice(["clay", "ceramic", "copper", "clay"])] if rng else M["clay"]
        B.cyl((x, 0, 0.02), (x, 0, 0.02 + h), r, mat, 12)
        B.cyl((x, 0, 0.02 + h), (x, 0, 0.04 + h), r * 0.7, M["plank_b"], 10)
        x += 2 * r + rng.uniform(0.03, 0.08) if rng else 0.15
    B.pop()


def bookcase(B, M, pos, rot=0, w=0.85, h=1.9, d=0.3, rng=None, broken=False):
    at(B, pos, rot, (0, 8, 0) if broken else None)
    tm = M["timber_dk"]
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.02), 0, h / 2), (0.04, d, h), tm)
    B.box((0, d / 2 - 0.01, h / 2), (w, 0.02, h), M["plank_b"])
    B.box((0, 0, h - 0.02), (w + 0.04, d + 0.02, 0.04), tm)
    shelves = [0.06, 0.48, 0.9, 1.32]
    for z in shelves:
        B.box((0, 0, z), (w - 0.04, d - 0.02, 0.03), tm)
    for k, z in enumerate(shelves):
        if broken and k > 1:
            continue
        x = -w / 2 + 0.06
        while x < w / 2 - 0.08:
            bw = rng.uniform(0.03, 0.06)
            bh = rng.uniform(0.2, 0.33)
            lean = rng.uniform(-8, 8) if rng.random() < 0.2 else 0
            B.box((x + bw / 2, 0.0, z + 0.015 + bh / 2), (bw, d - 0.08, bh),
                  M[rng.choice(["book_a", "book_b", "book_c", "fab_mustard", "fab_cream"])], rot=(0, lean, 0))
            x += bw + 0.004
            if rng.random() < 0.08:
                x += 0.12
    B.pop()


def armchair(B, M, pos, rot=0):
    at(B, pos, rot)
    B.box((0, 0, 0.3), (0.78, 0.72, 0.22), M["fab_red"])
    B.box((0, 0.3, 0.68), (0.78, 0.18, 0.6), M["fab_red"], rot=(-8, 0, 0))
    for sx in (-1, 1):
        B.box((sx * 0.4, 0, 0.5), (0.14, 0.72, 0.26), M["fab_red"])
        for sy in (-1, 1):
            B.box((sx * 0.33, sy * 0.28, 0.1), (0.06, 0.06, 0.2), M["timber_dk"])
    B.box((0, -0.04, 0.44), (0.62, 0.6, 0.08), M["fab_mustard"])
    B.box((0, 0.2, 0.62), (0.45, 0.14, 0.3), M["fab_cream"], rot=(-15, 0, 0))
    B.pop()


def chest(B, M, pos, rot=0):
    at(B, pos, rot)
    B.box((0, 0, 0.22), (0.82, 0.46, 0.44), M["plank_b"])
    B.box((0, 0, 0.5), (0.84, 0.48, 0.12), M["plank_c"])
    for x in (-0.3, 0.3):
        B.box((x, 0, 0.3), (0.05, 0.49, 0.58), M["iron"])
    B.box((0, -0.245, 0.42), (0.08, 0.02, 0.1), M["copper"])
    B.pop()


def barrel(B, M, pos, rot=0, lying=False):
    x, y, z = pos
    at(B, (x, y, z + (0.31 if lying else 0.0)), rot, (90, 0, 0) if lying else None)
    prof = [(0.0, 0.0), (0.0, 0.25), (0.15, 0.29), (0.31, 0.31), (0.47, 0.29), (0.62, 0.25), (0.62, 0.0)]
    B.lathe(prof, M["plank_b"], axis=(0, 0, 1), segs=16)
    for zz, rr in ((0.06, 0.262), (0.2, 0.3), (0.42, 0.3), (0.56, 0.262)):
        B.cyl((0, 0, zz - 0.02), (0, 0, zz + 0.02), rr, M["iron"], 16)
    B.pop()


def crate(B, M, pos, rot=0, s=0.5, tilt=None):
    at(B, pos, rot, tilt)
    B.box((0, 0, s / 2), (s, s, s), M["plank_c"])
    t = 0.05
    for a in (-1, 1):
        for b in (-1, 1):
            B.box((a * (s / 2 - t / 2 + 0.005), b * (s / 2 - t / 2 + 0.005), s / 2), (t, t, s + 0.01), M["timber_dk"])
            B.box((0, a * (s / 2 - t / 2 + 0.005), s / 2 + b * (s / 2 - t / 2)), (s + 0.01, t, t), M["timber_dk"])
            B.box((a * (s / 2 - t / 2 + 0.005), 0, s / 2 + b * (s / 2 - t / 2)), (t, s + 0.01, t), M["timber_dk"])
    B.pop()


def rug(B, M, pos, rot=0, w=1.7, d=1.2):
    at(B, pos, rot)
    B.box((0, 0, 0.006), (w, d, 0.012), M["fab_red"])
    B.box((0, 0, 0.008), (w - 0.2, d - 0.2, 0.012), M["fab_mustard"])
    B.box((0, 0, 0.01), (w - 0.34, d - 0.34, 0.012), M["fab_red"])
    B.box((0, 0, 0.012), (w - 0.8, d - 0.7, 0.012), M["fab_teal"])
    B.pop()


def hanging_lamp(B, M, pos, top_z, lit=True):
    x, y, z = pos
    B.cyl((x, y, top_z), (x, y, z + 0.32), 0.008, M["iron"], 6)
    B.box((x, y, z), (0.2, 0.2, 0.03), M["iron"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box((x + sx * 0.09, y + sy * 0.09, z + 0.14), (0.02, 0.02, 0.26), M["iron"])
    B.box((x, y, z + 0.14), (0.16, 0.16, 0.24), M["lamp_glow" if lit else "lamp_off"])
    B.cyl((x, y, z + 0.27), (x, y, z + 0.36), 0.15, M["iron"], 4, r2=0.02)


def candle(B, M, pos, h=0.12, lit=True):
    x, y, z = pos
    B.cyl((x, y, z), (x, y, z + 0.012), 0.045, M["copper"], 12)
    B.cyl((x, y, z + 0.012), (x, y, z + h), 0.022, M["fab_cream"], 10)
    if lit:
        B.cyl((x, y, z + h + 0.005), (x, y, z + h + 0.05), 0.011, M["fire_core"], 8, r2=0.0)


def mug(B, M, pos):
    x, y, z = pos
    B.cyl((x, y, z), (x, y, z + 0.1), 0.04, M["ceramic"], 12)
    B.box((x + 0.05, y, z + 0.05), (0.025, 0.012, 0.06), M["ceramic"])


def plant(B, M, rng, pos, s=1.0):
    x, y, z = pos
    B.cyl((x, y, z), (x, y, z + 0.18 * s), 0.1 * s, M["clay"], 12, r2=0.125 * s)
    B.cyl((x, y, z + 0.17 * s), (x, y, z + 0.18 * s), 0.115 * s, M["dirt"], 12)
    for i in range(9):
        a = i * 40 + rng.uniform(-10, 10)
        r = 0.06 * s
        leaf(B, M[rng.choice(["leaf_a", "leaf_b", "leaf_c"])],
             (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)), z + (0.27 + 0.05 * (i % 3)) * s),
             0.17 * s, rng.uniform(-20, 20), -35, yaw=a - 90)


def fire(B, M, pos, lit=True):
    x, y, z = pos
    for a, dy in ((25, -0.05), (-25, 0.05), (0, 0.0)):
        B.cyl((x - 0.22, y + dy, z + 0.06), (x + 0.22, y + dy, z + 0.06 + (0.06 if a == 0 else 0)), 0.05,
              M["bark"], 10)
    if lit:
        for (dx, dy, h, r, m) in ((0, 0, 0.42, 0.13, "fire"), (-0.1, 0.03, 0.3, 0.08, "fire"),
                                  (0.11, -0.02, 0.33, 0.09, "fire"), (0, 0, 0.3, 0.07, "fire_core"),
                                  (0.05, 0.02, 0.22, 0.05, "fire_core")):
            B.cyl((x + dx, y + dy, z + 0.06), (x + dx, y + dy, z + 0.06 + h), r, M[m], 8, r2=0.0)
        B.box((x, y, z + 0.02), (0.5, 0.3, 0.03), M["fire"])
    else:
        B.box((x, y, z + 0.02), (0.6, 0.4, 0.05), M["ash"])


def painting(B, M, pos, rot=0):
    at(B, pos, rot)
    B.box((0, 0, 0), (0.7, 0.04, 0.5), M["timber_dk"])
    B.box((0, -0.022, 0.0), (0.6, 0.01, 0.4), M["grass"])
    B.box((0, -0.025, 0.1), (0.6, 0.01, 0.2), M["glass_clear"])
    B.prism([(-0.25, -0.1), (-0.05, 0.12), (0.12, -0.1)], 0.012, M["slate_a"], "XZ", -0.028)
    B.box((0.15, -0.028, 0.1), (0.08, 0.01, 0.08), M["flower_yel"])
    B.pop()


def debris(B, M, rng, x0, x1, y0, y1, z, n=10):
    for _ in range(n):
        B.box((rng.uniform(x0, x1), rng.uniform(y0, y1), z + 0.02),
              (rng.uniform(0.4, 1.2), rng.uniform(0.08, 0.18), 0.03),
              M[rng.choice(["plank_a", "plank_b", "timber_old"])], rot=(0, rng.uniform(-6, 6), rng.uniform(0, 180)))


def fallen_tiles(B, M, rng, x0, x1, y0, y1, z, mats, n=12):
    for _ in range(n):
        B.box((rng.uniform(x0, x1), rng.uniform(y0, y1), z + 0.015), (0.32, 0.36, 0.024),
              M[rng.choice(mats)], rot=(rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(0, 180)))


def scattered_leaves(B, M, rng, x0, x1, y0, y1, z, n=40):
    for _ in range(n):
        leaf(B, M[rng.choice(["leaf_a", "leaf_c", "moss"])], (rng.uniform(x0, x1), rng.uniform(y0, y1), z + 0.005),
             rng.uniform(0.08, 0.14), rng.uniform(0, 360), -90)
