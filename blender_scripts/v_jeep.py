"""Teal 3-door off-roader (from the reference picture), game-ready.

Axes: front = -Y (becomes +Z in Godot, matching VehicleBody3D), +Z up, left side = +X, ground at z=0.
Wheels are separate objects with their origin on the axle, so they can spin / steer in the game.
Left-hand drive (steering wheel on the +X side). Metres.
"""
import math
import random
from mathutils import Matrix, Vector
import wb

WB2 = 1.12          # half wheelbase
TRACK = 0.66        # wheel centre x
WR = 0.36           # tyre radius
ARCH_R, ARCH_Z = 0.47, 0.38
SILL, BELT, ROOF = 0.52, 1.05, 1.74
X_SKIN = 0.78
Y_FRONT, Y_REAR = -1.62, 1.70
WHEELS = {"FL": (TRACK, -WB2), "FR": (-TRACK, -WB2), "RL": (TRACK, WB2), "RR": (-TRACK, WB2)}


def beam(B, p0, p1, sx, sy, mat):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    B.box((0, 0, 0), (sx, sy, d.length), mat, L=Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4())


def arch_pts(cy, r, z0, n=14, reverse=False):
    a0 = math.degrees(math.asin((z0 - ARCH_Z) / r))
    angs = [a0 + (180 - 2 * a0) * i / n for i in range(n + 1)]
    if reverse:
        angs = angs[::-1]
    return [(cy + r * math.cos(math.radians(a)), ARCH_Z + r * math.sin(math.radians(a))) for a in angs]


def side_profile():
    ch = 0.06
    pts = [(Y_FRONT, BELT - ch), (Y_FRONT + ch, BELT), (Y_REAR - 0.03, BELT), (Y_REAR, BELT - 0.03), (Y_REAR, SILL)]
    for cy in (WB2, -WB2):
        pts += arch_pts(cy, ARCH_R, SILL)
    pts.append((Y_FRONT, SILL + 0.05))
    return pts


def build_wheel(name, M, rng, loc, rot_z):
    W = wb.Builder(name)
    W.lathe([(-0.13, 0.215), (-0.13, 0.30), (-0.12, 0.335), (-0.1, 0.355), (0.1, 0.355), (0.12, 0.335),
             (0.13, 0.30), (0.13, 0.215)], M["car_rubber"], segs=32)
    n = 26
    for i in range(n):
        for k, xo in enumerate((0.055, -0.055)):
            a = 360 * (i + 0.5 * k) / n
            R = Matrix.Rotation(math.radians(a), 4, "X")
            W.box((xo, 0, 0.367), (0.085, 0.07, 0.03), M["car_rubber"], L=R)
            W.box((0.118 * (1 if k == 0 else -1), 0, 0.325), (0.03, 0.055, 0.045), M["car_rubber"], L=R)
    W.lathe([(-0.125, 0.232), (-0.115, 0.215), (0.115, 0.215), (0.125, 0.232)], M["car_rim"], segs=32)
    W.cyl((0.02, 0, 0), (0.06, 0, 0), 0.212, M["car_rim"], 32)
    W.cyl((0.06, 0, 0), (0.085, 0, 0), 0.075, M["car_rim"], 20, r2=0.06)
    for i in range(5):
        a = math.radians(72 * i)
        W.cyl((0.06, 0.1 * math.cos(a), 0.1 * math.sin(a)), (0.078, 0.1 * math.cos(a), 0.1 * math.sin(a)), 0.014,
              M["car_chrome"], 6)
    for i in range(6):
        a = math.radians(60 * i + 30)
        W.cyl((0.059, 0.155 * math.cos(a), 0.155 * math.sin(a)), (0.0615, 0.155 * math.cos(a), 0.155 * math.sin(a)),
              0.026, M["car_grille"], 12)
    return W.finish(bevel=0.005, segs=1, matrix=Matrix.Translation(loc) @ Matrix.Rotation(math.radians(rot_z), 4, "Z"))


def build_jeep(M, pack, name="Jeep"):
    root = wb.begin(name, pack)
    rng = random.Random(3)
    p = "JEEP_"
    Bd, Tr, Gl, Lt, In, Ch, Md = (wb.Builder(p + n) for n in
                                  ("Body", "Trim", "Glass", "Lights", "Interior", "Chassis", "Mud"))
    body, trim, dark = M["car_body"], M["car_plastic"], M["car_grille"]

    # ---------------- lower body: side skins with wheel arches, hood, front panel
    prof = side_profile()
    for s in (-1, 1):
        Bd.prism(prof, 0.045, body, "YZ", s * (X_SKIN - 0.0225))
    Bd.box2((-0.5, -1.6, 0.6), (0.5, -0.55, 1.02), body)
    Bd.box2((-X_SKIN, Y_FRONT, 1.0), (X_SKIN, -0.52, 1.08), body)
    Bd.box2((-0.46, -1.58, 1.06), (0.46, -0.6, 1.105), body)
    Bd.box2((-X_SKIN, Y_FRONT - 0.04, 0.58), (X_SKIN, Y_FRONT + 0.04, 1.03), body)
    Bd.box2((-0.76, -0.6, 1.03), (0.76, -0.48, 1.1), body)                       # cowl
    Bd.box2((-X_SKIN, Y_REAR - 0.045, SILL), (X_SKIN, Y_REAR, BELT + 0.03), body)  # tailgate
    # ---------------- cabin: pillars, roof
    for s in (-1, 1):
        beam(Bd, (s * 0.745, -0.53, 1.07), (s * 0.735, -0.33, 1.67), 0.06, 0.07, body)
        Bd.box((s * 0.745, 0.63, 1.36), (0.05, 0.1, 0.62), body)
        Bd.box((s * 0.745, Y_REAR - 0.045, 1.36), (0.06, 0.09, 0.62), body)
        Tr.box((s * 0.757, 0.67, 1.665), (0.02, 2.05, 0.03), trim)                 # rain gutter
    Bd.box((0, -0.335, 1.665), (1.5, 0.06, 0.05), body)
    Bd.box2((-0.75, -0.36, 1.655), (0.75, Y_REAR, ROOF), body)
    Bd.box((0, Y_REAR - 0.03, 1.08), (1.5, 0.05, 0.06), body)
    Bd.box((0, Y_REAR - 0.03, 1.64), (1.5, 0.05, 0.05), body)
    # ---------------- glass
    Gl.slab([(-0.68, -0.53, 1.08), (0.68, -0.53, 1.08), (0.68, -0.335, 1.645), (-0.68, -0.335, 1.645)], 0.01,
            M["car_glass"])
    for s in (-1, 1):
        Gl.prism([(-0.5, 1.08), (0.58, 1.08), (0.58, 1.64), (-0.33, 1.64)], 0.01, M["car_glass"], "YZ", s * 0.745)
        Gl.prism([(0.68, 1.08), (1.62, 1.08), (1.62, 1.63), (0.68, 1.63)], 0.01, M["car_glass"], "YZ", s * 0.745)
    Gl.prism([(-0.68, 1.1), (0.68, 1.1), (0.68, 1.61), (-0.68, 1.61)], 0.01, M["car_glass"], "XZ", Y_REAR - 0.02)
    # ---------------- trim: grille, bumpers, flares, mirrors, handles, seams, rack
    yf = Y_FRONT - 0.04
    Tr.box((0, yf - 0.012, 0.845), (0.76, 0.03, 0.27), dark)
    for z in (0.765, 0.845, 0.925):
        Tr.box((0, yf - 0.03, z), (0.72, 0.012, 0.012), trim)
    for i in range(9):
        Tr.box((-0.34 + i * 0.085, yf - 0.03, 0.845), (0.012, 0.012, 0.24), trim)
    for z in (0.705, 0.985):
        Tr.box((0, yf - 0.03, z), (0.8, 0.02, 0.025), trim)
    for x in (-0.395, 0.395):
        Tr.box((x, yf - 0.03, 0.845), (0.025, 0.02, 0.3), trim)
    Tr.box((0, yf - 0.012, 0.65), (0.7, 0.03, 0.06), dark)
    Tr.box((0, -1.765, 0.54), (1.68, 0.2, 0.2), trim)
    for s in (-1, 1):
        Tr.box((s * 0.79, -1.62, 0.54), (0.14, 0.32, 0.2), trim)
        Lt.box((s * 0.62, -1.866, 0.575), (0.16, 0.012, 0.05), M["car_ind"])
        Tr.box((s * 0.25, -1.866, 0.5), (0.1, 0.012, 0.04), dark)
    Tr.box((0, -1.866, 0.54), (0.42, 0.01, 0.12), dark)
    Tr.box((0, Y_REAR + 0.075, 0.54), (1.62, 0.16, 0.18), trim)
    for s in (-1, 1):
        Tr.box((s * 0.78, Y_REAR - 0.05, 0.54), (0.14, 0.26, 0.18), trim)
    for cy in (-WB2, WB2):
        band = arch_pts(cy, 0.56, SILL) + arch_pts(cy, ARCH_R - 0.005, SILL, reverse=True)
        for s in (-1, 1):
            Tr.prism(band, 0.07, trim, "YZ", s * (X_SKIN + 0.02))
            Tr.prism(arch_pts(cy, 0.5, SILL - 0.02) + arch_pts(cy, ARCH_R - 0.01, SILL - 0.02, reverse=True), 0.26,
                     dark, "YZ", s * 0.645)
            Tr.prism(arch_pts(cy, 0.5, SILL - 0.02), 0.02, dark, "YZ", s * 0.52)
    for s in (-1, 1):
        Tr.box((s * 0.79, 0.0, 0.54), (0.06, 1.32, 0.08), trim)
        beam(Tr, (s * 0.78, -0.47, 1.1), (s * 0.9, -0.5, 1.17), 0.03, 0.04, trim)
        Tr.box((s * 0.935, -0.5, 1.2), (0.05, 0.11, 0.16), trim)
        Tr.box((s * 0.935, -0.443, 1.2), (0.04, 0.005, 0.13), M["car_chrome"])
        Tr.box((s * (X_SKIN + 0.008), 0.48, 0.98), (0.02, 0.12, 0.03), dark)
        for y0, y1, z0, z1 in ((-0.52, -0.51, 0.56, BELT), (0.595, 0.605, 0.62, BELT), (-0.52, 0.6, 0.565, 0.575)):
            Tr.box2((s * (X_SKIN - 0.002), y0, z0), (s * (X_SKIN + 0.003), y1, z1), dark)
    Tr.cyl((0.78, 1.35, 0.97), (0.79, 1.35, 0.97), 0.045, trim, 16)                   # fuel cap
    for s in (-1, 1):                                                                 # wipers
        beam(Tr, (s * 0.06, -0.515, 1.1), (s * 0.58, -0.47, 1.18), 0.015, 0.02, dark)
    rz0, rz1 = 1.83, 1.97
    for z in (rz0, rz1):
        for s in (-1, 1):
            Tr.cyl((s * 0.62, -0.22, z), (s * 0.62, 1.6, z), 0.018, dark, 8)
        for y in (-0.22, 1.6):
            Tr.cyl((-0.62, y, z), (0.62, y, z), 0.018, dark, 8)
    for y in (0.15, 0.5, 0.85, 1.2):
        Tr.cyl((-0.62, y, rz0), (0.62, y, rz0), 0.014, dark, 8)
    for s in (-1, 1):
        for i in range(5):
            y = -0.22 + i * (1.82 / 4)
            Tr.cyl((s * 0.62, y, rz0), (s * 0.62, y, rz1), 0.015, dark, 8)
        for y in (-0.22, 0.69, 1.6):
            Tr.box((s * 0.6, y, (ROOF + rz0) / 2), (0.06, 0.08, rz0 - ROOF), dark)
    for x in (-0.3, 0.3):
        Tr.cyl((x, -0.22, rz0), (x, -0.22, rz1), 0.015, dark, 8)
        Tr.cyl((x, 1.6, rz0), (x, 1.6, rz1), 0.015, dark, 8)
    # ---------------- lights
    for s in (-1, 1):
        x = s * 0.56
        Bd.cyl((x, Y_FRONT - 0.03, 0.86), (x, Y_FRONT - 0.06, 0.86), 0.13, body, 28)
        Lt.cyl((x, Y_FRONT - 0.06, 0.86), (x, Y_FRONT - 0.085, 0.86), 0.105, M["car_chrome"], 28)
        Lt.cyl((x, Y_FRONT - 0.085, 0.86), (x, Y_FRONT - 0.095, 0.86), 0.085, M["car_head"], 28)
        Lt.box((x, Y_FRONT - 0.05, 0.68), (0.13, 0.02, 0.045), M["car_ind"])
        Lt.box((s * (X_SKIN + 0.004), -1.45, 0.88), (0.012, 0.09, 0.04), M["car_ind"])
        Lt.box((s * 0.66, Y_REAR + 0.006, 0.86), (0.11, 0.012, 0.24), M["car_tail"])
        Lt.box((s * 0.66, Y_REAR + 0.006, 0.7), (0.11, 0.012, 0.06), M["car_ind"])
    Tr.box((0, Y_REAR + 0.008, 0.78), (0.34, 0.012, 0.12), M["paint_white"])
    # ---------------- spare wheel on the tailgate
    Tr.box((0, Y_REAR + 0.03, 1.0), (0.2, 0.07, 0.2), trim)
    build_wheel(p + "SpareWheel", M, rng, (0, Y_REAR + 0.19, 1.0), 90)
    # ---------------- interior
    dash = M["car_dash"]
    In.box2((-0.74, -0.52, 0.55), (0.74, Y_REAR - 0.045, 0.62), dash)
    In.box2((-0.72, -0.56, 0.95), (0.72, -0.34, 1.16), dash)
    In.box2((-0.72, -0.56, 1.16), (0.72, -0.42, 1.2), dash)
    In.box((0.35, -0.41, 1.2), (0.3, 0.05, 0.08), dark)
    for dx in (-0.07, 0.07):
        In.cyl((0.35 + dx, -0.44, 1.2), (0.35 + dx, -0.445, 1.2), 0.03, M["car_chrome"], 16)
    In.cyl((0.35, -0.45, 1.0), (0.35, -0.27, 1.1), 0.03, dark, 10)
    axis = Vector((0, 0.18, 0.1)).normalized()
    ring = [(0.017 * math.cos(math.radians(a)), 0.17 + 0.017 * math.sin(math.radians(a))) for a in range(0, 361, 30)]
    In.lathe(ring, dark, origin=(0.35, -0.27, 1.1), axis=axis, segs=24)
    In.cyl((0.35, -0.28, 1.095), (0.35, -0.25, 1.11), 0.05, dark, 12)
    seat = M["car_seat"]
    for x in (-0.36, 0.36):
        In.box((x, 0.15, 0.74), (0.46, 0.5, 0.24), seat)
        In.box((x, 0.44, 1.17), (0.46, 0.13, 0.66), seat, rot=(-12, 0, 0))
        In.box((x, 0.5, 1.52), (0.26, 0.1, 0.16), seat, rot=(-12, 0, 0))
    In.box((0, 1.2, 0.74), (1.24, 0.46, 0.24), seat)
    In.box((0, 1.5, 1.1), (1.24, 0.12, 0.52), seat, rot=(-8, 0, 0))
    In.cyl((0, -0.22, 0.62), (0, -0.15, 0.93), 0.012, dark, 8)
    In.cyl((0, -0.15, 0.93), (0, -0.14, 0.97), 0.03, dark, 10)
    In.box((0, -0.35, 1.6), (0.22, 0.03, 0.06), dark)
    for s in (-1, 1):
        In.box2((s * 0.70, -0.5, 0.66), (s * 0.735, 0.58, 1.03), dash)
    # ---------------- chassis
    Ch.box2((-0.45, -1.5, 0.32), (0.45, 1.5, SILL), dark)
    for y in (-WB2, WB2):
        Ch.cyl((-0.56, y, WR), (0.56, y, WR), 0.05, dark, 12)
        Ch.cyl((0, y - 0.1, WR), (0, y + 0.1, WR), 0.12, dark, 16)
    Ch.cyl((-0.4, 1.4, 0.4), (-0.4, 1.9, 0.4), 0.035, M["car_chrome"], 12)
    # ---------------- mud splashes
    for s in (-1, 1):
        for _ in range(11):
            cy = rng.uniform(1.6, 1.66) if rng.random() < 0.2 else rng.uniform(-0.6, 0.6)
            cz = rng.uniform(0.58, 0.7)
            rr = rng.uniform(0.04, 0.11)
            n = 8
            blob = [(cy + rr * math.cos(2 * math.pi * i / n) * rng.uniform(0.6, 1.3),
                     cz + rr * 0.6 * math.sin(2 * math.pi * i / n) * rng.uniform(0.6, 1.3)) for i in range(n)]
            Md.poly(blob if s > 0 else blob[::-1], M["car_mud"], "YZ", s * (X_SKIN + 0.006))
    # ---------------- finish
    Bd.finish(bevel=0.02, segs=2)
    Tr.finish(bevel=0.01, segs=2)
    Gl.finish()
    Lt.finish(bevel=0.003, segs=1)
    In.finish(bevel=0.012, segs=2)
    Ch.finish(bevel=0.01, segs=1)
    Md.finish(smooth=False)
    for key, (x, y) in WHEELS.items():
        build_wheel(p + "Wheel_" + key, M, rng, (x, y, WR), 0 if x > 0 else 180)
    return root
