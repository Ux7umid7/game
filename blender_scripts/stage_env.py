"""Display stage for the houses + jeep: grass, dirt road, trees, rocks, sun, cameras (not exported)."""
import math
import random
import bpy
from mathutils import Matrix, Vector
import wb

LAYOUT = {  # root: (location, rotation about Z in degrees)
    "House_Ruined": ((-15.0, 0.0, 0.0), 0),
    "House_Cottage": ((0.0, 0.0, 0.0), 0),
    "House_Upgraded": ((15.0, 0.0, 0.0), 0),
    "Jeep": ((6.8, -11.8, 0.0), 32),
}


def _aim(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def _camera(coll, name, loc, target, lens):
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cd.lens, cd.clip_start, cd.clip_end = lens, 0.05, 400
    ob = bpy.data.objects.new(name, cd)
    coll.objects.link(ob)
    ob.location = loc
    _aim(ob, target)
    return ob


def _ball(B, mat, c, r, segs=8):
    prof = [(-r, 0.0), (-0.7 * r, 0.72 * r), (0.0, r), (0.7 * r, 0.72 * r), (r, 0.0)]
    B.lathe(prof, mat, origin=c, axis=(0, 0, 1), segs=segs)


def _tree(B, M, rng, x, y, s):
    B.cyl((x, y, 0), (x, y, 2.4 * s), 0.2 * s, M["bark"], 8, r2=0.12 * s)
    for _ in range(rng.randint(4, 6)):
        _ball(B, M[rng.choice(("leaf_a", "leaf_b", "leaf_c"))],
              (x + rng.uniform(-0.9, 0.9) * s, y + rng.uniform(-0.9, 0.9) * s, rng.uniform(2.6, 3.9) * s),
              rng.uniform(0.9, 1.4) * s)


def build(M):
    for name, (loc, rot) in LAYOUT.items():
        o = bpy.data.objects.get(name)
        if o:
            wb.place(o, loc, (0, 0, rot))
    coll = wb.get_coll("Env_Stage")
    for o in list(coll.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    wb.CUR["coll"], wb.CUR["root"] = coll, None
    rng = random.Random(21)

    G = wb.Builder("Ground")
    G.box2((-250, -250, -0.3), (250, 250, 0.0), M["grass"])
    G.box2((-40, -13.2, -0.25), (40, -10.4, 0.012), M["dirt"])
    for hx in (-15.0, 0.0, 15.0):
        G.box2((hx + 0.45, -10.45, -0.25), (hx + 1.35, -8.5, 0.01), M["dirt"])
    for i in range(60):  # each patch at its own height: coplanar overlaps shade black in Cycles
        cx, cy = rng.uniform(-35, 35), rng.uniform(-30, 25)
        r = rng.uniform(1.5, 4.0)
        G.poly([(cx + r * math.cos(a) * rng.uniform(0.7, 1.0), cy + r * 0.6 * math.sin(a) * rng.uniform(0.7, 1.0))
                for a in [j * math.pi / 5 for j in range(10)]], M["grass_dk"], "XY", 0.002 + 0.0008 * i)
    G.finish(smooth=False)

    Nat = wb.Builder("Nature")
    for x, y, s in ((-24, 9, 1.3), (-8, 10, 1.1), (7, 11, 1.4), (24, 9, 1.2), (-30, -2, 1.0), (30, -1, 1.15),
                    (-21, 15, 1.5), (-1, 16, 1.6), (20, 16, 1.3), (-7.5, 6.5, 0.8), (8.5, 6.0, 0.9),
                    (-27, -16, 1.1), (27, -17, 1.2)):
        _tree(Nat, M, rng, x, y, s)
    for _ in range(26):
        x, y = rng.uniform(-30, 30), rng.uniform(-20, 12)
        if abs(y + 11.8) < 2.0 or any(abs(x - hx) < 5.5 and -9 < y < 6 for hx in (-15, 0, 15)):
            continue
        _ball(Nat, M[rng.choice(("leaf_a", "leaf_c"))], (x, y, 0.1), rng.uniform(0.4, 0.8), segs=7)
    for _ in range(30):
        x, y = rng.uniform(-32, 32), rng.uniform(-22, 14)
        if abs(y + 11.8) < 1.8:
            continue
        r = rng.uniform(0.15, 0.55)
        Nat.lathe([(-r * 0.4, 0.0), (-r * 0.3, r * 0.8), (r * 0.1, r), (r * 0.35, r * 0.6), (r * 0.4, 0.0)],
                  M[rng.choice(("stone_a", "stone_b", "stone_c"))], origin=(x, y, 0), axis=(0, 0, 1), segs=6)
    for _ in range(420):
        x, y = rng.uniform(-30, 30), rng.uniform(-20, 10)
        if -13.4 < y < -10.2 or any(abs(x - hx) < 3.0 and -5.8 < y < 3.8 for hx in (-15, 0, 15)):
            continue
        for _b in range(5):
            h = rng.uniform(0.12, 0.3)
            ang = rng.uniform(0, 180)
            Nat.poly([(-0.012, 0.0), (0.012, 0.0), (0.0, h)], M[rng.choice(("grass", "grass_dk", "leaf_b"))], "XZ",
                     0.0, L=Matrix.Translation((x + rng.uniform(-0.1, 0.1), y + rng.uniform(-0.1, 0.1), 0)) @
                     wb.rotm((rng.uniform(-15, 15), 0, ang)))
    Nat.finish(bevel=0.0, smooth=False)

    # sun + sky
    sun_d = bpy.data.lights.get("Sun") or bpy.data.lights.new("Sun", "SUN")
    sun_d.energy, sun_d.angle, sun_d.color = 3.6, math.radians(1.5), (1.0, 0.91, 0.78)
    sun = bpy.data.objects.new("Sun", sun_d)
    coll.objects.link(sun)
    sun.rotation_euler = Vector((0.45, 0.78, -0.62)).to_track_quat("-Z", "Y").to_euler()
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = wb.srgb("#A8C6E2")
    bg.inputs["Strength"].default_value = 0.75

    cams = [_camera(coll, "Cam_Overview", (-6.0, -40.0, 15.0), (0.5, -1.5, 1.8), 32)]
    for name, (loc, _r) in list(LAYOUT.items())[:3]:
        x = loc[0]
        cams.append(_camera(coll, "Cam_" + name, (x - 10.5, -12.5, 6.3), (x - 0.4, 0.0, 2.6), 38))
    cams.append(_camera(coll, "Cam_Interior", (1.95, -2.85, 1.7), (-1.3, 2.3, 1.25), 18))
    cams.append(_camera(coll, "Cam_House_Upgraded_Side", (26.5, -11.5, 5.2), (16.6, 0.0, 1.9), 36))
    cams.append(_camera(coll, "Cam_Jeep", (13.4, -14.4, 2.5), (6.6, -11.5, 0.85), 36))
    bpy.context.scene.camera = cams[0]
    for n in ("Light", "Camera"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = o.hide_viewport = True
    return cams
