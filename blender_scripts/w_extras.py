"""New items that fit the island game ideas: crossbow, hatchet, flare gun, EMP grenade, ammo crate."""
import math
import wb


# ------------------------------------------------------------------ crossbow
def build_crossbow(M, pack):
    p = "XB_"
    root = wb.begin("Crossbow", pack)
    stock = [(0.40, 0.0), (0.40, -0.03), (0.05, -0.034), (0.0, -0.04), (-0.022, -0.05), (-0.038, -0.128),
             (-0.078, -0.128), (-0.074, -0.06), (-0.1, -0.042), (-0.3, -0.078), (-0.318, -0.078),
             (-0.318, 0.022), (-0.25, 0.022), (-0.1, 0.004), (-0.06, 0.0)]
    wb.prism(p + "Stock", stock, 0.04, M["wood_dk"], bevel=0.007, segs=3)
    wb.prism(p + "ButtPad", [(-0.318, 0.025), (-0.334, 0.025), (-0.334, -0.082), (-0.318, -0.081)], 0.044,
             M["rubber"], bevel=0.005, segs=3)
    wb.box(p + "StockTape", (-0.2, 0, -0.022), (0.03, 0.044, 0.07), M["teal"], bevel=0.008, segs=3, rot=(0, -10, 0))
    wb.box(p + "FlightRail", (0.17, 0, 0.007), (0.46, 0.022, 0.014), M["metal"], bevel=0.002)
    wb.box(p + "RailGroove", (0.18, 0, 0.0142), (0.42, 0.006, 0.001), M["black"], bevel=0)
    wb.box(p + "TriggerHousing", (0.0, 0, 0.012), (0.08, 0.036, 0.032), M["dark"], bevel=0.003)
    wb.box(p + "StringLatch", (0.03, 0, 0.03), (0.016, 0.024, 0.01), M["metal"], bevel=0.002)
    tg = wb.prism(p + "TriggerGuard", [(-0.026, -0.04), (0.03, -0.035), (0.026, -0.068), (-0.022, -0.07)],
                  0.012, M["metal"], bevel=0.002)
    wb.cut(tg, wb.prism(p + "_cut", [(-0.018, -0.04), (0.02, -0.035), (0.016, -0.061), (-0.016, -0.062)],
                        0.04, None, bevel=0))
    wb.prism(p + "Trigger", [(0.0, -0.037), (0.006, -0.037), (0.004, -0.047), (-0.002, -0.055),
                             (-0.007, -0.055), (-0.003, -0.047)], 0.006, M["black"], bevel=0.001)
    wb.box(p + "Riser", (0.408, 0, 0.0), (0.05, 0.06, 0.05), M["dark"], bevel=0.005, segs=3)
    # limbs: outline drawn in XZ then laid flat (rotated 90 deg about X)
    span, n = 0.34, 16
    front, back = [], []
    for i in range(n + 1):
        t = -1 + 2 * i / n
        xc = 0.408 - 0.085 * t * t
        w = 0.042 - 0.024 * abs(t)
        front.append((xc + w / 2, span * t))
        back.append((xc - w / 2, span * t))
    limbs = wb.prism(p + "Limbs", front + back[::-1], 0.012, M["olive"], bevel=0.003, segs=2)
    limbs.rotation_euler = (math.radians(90), 0, 0)
    limbs.location = (0, 0, 0.004)
    tip_x = 0.408 - 0.085
    wb.cyls(p + "Cams", [((tip_x, s * span, -0.012), (tip_x, s * span, 0.02), 0.015) for s in (-1, 1)],
            M["metal"], verts=24, bevel=0.002)
    for s in (-1, 1):
        wb.box(p + "LimbWrap%d" % (s + 1), (0.408 - 0.085 * 0.346, -s * 0.2, 0.004), (0.036, 0.022, 0.017),
               M["teal"], bevel=0.004, rot=(0, 0, -s * 16))
    wb.cyls(p + "String", [((tip_x - 0.008, s * span, 0.012), (0.03, 0, 0.022), 0.0018) for s in (-1, 1)],
            M["rope"], verts=8)
    # bolt (arrow) loaded on the rail
    wb.cyl(p + "BoltShaft", (0.035, 0, 0.02), (0.44, 0, 0.02), 0.004, M["rust"], verts=12, bevel=0)
    head = [(0.0, 0.0), (0.0, 0.0055), (0.01, 0.006), (0.04, 0.0)]
    wb.lathe(p + "BoltHead", head, M["steel"], origin=(0.438, 0, 0.02), segs=4, angle=30)
    wb.prism(p + "BoltFinTop", [(0.04, 0.023), (0.09, 0.023), (0.078, 0.036), (0.045, 0.036)], 0.0018,
             M["teal"], bevel=0)
    wb.boxes(p + "BoltFinsSide", [((0.064, s * 0.011, 0.02), (0.044, 0.014, 0.0018)) for s in (-1, 1)],
             M["rust"], bevel=0)
    # foot stirrup
    wb.cyls(p + "Stirrup", [((0.43, -0.03, -0.012), (0.49, -0.035, -0.03), 0.0045),
                            ((0.43, 0.03, -0.012), (0.49, 0.035, -0.03), 0.0045),
                            ((0.49, -0.036, -0.03), (0.49, 0.036, -0.03), 0.0045)], M["metal"], verts=12)
    return root


# ------------------------------------------------------------------ hatchet
def build_hatchet(M, pack):
    p = "AXE_"
    root = wb.begin("Hatchet", pack)
    right, left = [], []
    n = 20
    for i in range(n + 1):
        z = -0.01 + 0.44 * i / n
        xc = 0.008 * math.sin(math.pi * (z + 0.01) / 0.44)
        hw = 0.015 + (0.007 * (1 - z / 0.04) if z < 0.04 else 0.0)
        right.append((xc + hw, z))
        left.append((xc - hw, z))
    wb.prism(p + "Handle", right + left[::-1], 0.024, M["wood"], bevel=0.006, segs=3)
    head = [(-0.034, 0.37), (-0.034, 0.425), (0.03, 0.425), (0.06, 0.442), (0.105, 0.468), (0.126, 0.445),
            (0.126, 0.345), (0.105, 0.322), (0.06, 0.352), (0.03, 0.37)]
    hd = wb.prism(p + "Head", head, 0.03, M["axe_head"], bevel=0.0, segs=2)
    for v in hd.data.vertices:
        if v.co.x > 0.035:
            k = max(0.12, 1 - (v.co.x - 0.035) / 0.095)
            v.co.y *= k
    hd.data.set_sharp_from_angle(angle=math.radians(35))
    wb.add_bevel(hd, 0.0025, 2)
    wb.box(p + "HeadPoll", (-0.004, 0, 0.3975), (0.066, 0.034, 0.059), M["metal"], bevel=0.004, segs=2)
    wb.box(p + "Wedge", (0.002, 0, 0.428), (0.024, 0.012, 0.006), M["wood_dk"], bevel=0.001)
    wraps = []
    for i in range(9):
        z = 0.035 + i * 0.012
        wraps.append(((0.008 * math.sin(math.pi * (z + 0.01) / 0.44), 0, z), (0.034, 0.028, 0.011),
                      (0, 8 if i % 2 else -8, 0)))
    wb.boxes(p + "GripWrap", wraps, M["rope"], bevel=0.003, segs=2)
    wb.cyl(p + "LanyardHole", (0.0, -0.013, 0.012), (0.0, 0.013, 0.012), 0.0045, M["black"], verts=12, bevel=0)
    wb.box(p + "TapeBand", (0.008 * math.sin(math.pi * 0.2 / 0.44), 0, 0.19), (0.034, 0.028, 0.018), M["teal"],
           bevel=0.004, segs=2)
    return root


# ------------------------------------------------------------------ flare gun
def build_flaregun(M, pack):
    p = "FLR_"
    root = wb.begin("FlareGun", pack)
    br = wb.cyl(p + "Barrel", (0.0, 0, 0.0), (0.175, 0, 0.0), 0.022, M["flare_red"], verts=32, bevel=0.003)
    wb.cut(br, wb.cyl(p + "_cut", (0.15, 0, 0.0), (0.2, 0, 0.0), 0.016, None, verts=32, bevel=0))
    wb.cyl(p + "BoreBack", (0.148, 0, 0), (0.152, 0, 0), 0.0162, M["black"], verts=32, bevel=0)
    wb.cyl(p + "MuzzleRing", (0.16, 0, 0), (0.176, 0, 0), 0.0238, M["dark"], verts=32, bevel=0.002)
    wb.cyl(p + "StripeBand", (0.06, 0, 0), (0.075, 0, 0), 0.0228, M["yellow"], verts=32, bevel=0.001)
    wb.box(p + "Breech", (-0.008, 0, -0.002), (0.05, 0.04, 0.046), M["flare_red"], bevel=0.006, segs=3)
    wb.cyl(p + "HingePin", (0.012, -0.022, -0.02), (0.012, 0.022, -0.02), 0.005, M["dark"], verts=16)
    frame = [(-0.03, -0.022), (0.02, -0.022), (0.016, -0.03), (-0.012, -0.034), (-0.03, -0.11),
             (-0.034, -0.122), (-0.072, -0.122), (-0.072, -0.108), (-0.058, -0.03), (-0.062, 0.006),
             (-0.048, 0.02), (-0.032, 0.02)]
    wb.prism(p + "Frame", frame, 0.034, M["flare_red"], bevel=0.007, segs=3)
    wb.mirror_y(wb.prism(p + "GripPanel", [(-0.02, -0.04), (-0.034, -0.105), (-0.064, -0.105),
                                           (-0.052, -0.04)], 0.004, M["dark"], bevel=0.0015, y=-0.0175))
    wb.prism(p + "Hammer", [(-0.05, 0.012), (-0.062, 0.032), (-0.072, 0.03), (-0.064, 0.008)], 0.01,
             M["dark"], bevel=0.0015)
    tg = wb.prism(p + "TriggerGuard", [(-0.015, -0.03), (0.04, -0.022), (0.036, -0.06), (-0.01, -0.062)],
                  0.012, M["dark"], bevel=0.002)
    wb.cut(tg, wb.prism(p + "_cut", [(-0.008, -0.03), (0.03, -0.022), (0.027, -0.054), (-0.004, -0.055)],
                        0.04, None, bevel=0))
    wb.prism(p + "Trigger", [(0.004, -0.028), (0.011, -0.028), (0.009, -0.038), (0.003, -0.047),
                             (-0.002, -0.047), (0.002, -0.038)], 0.006, M["black"], bevel=0.001)
    # spare flare cartridge next to the gun
    cart = [(0.0, 0.0), (0.0, 0.0175), (0.006, 0.0175), (0.006, 0.0158), (0.075, 0.0158), (0.078, 0.013),
            (0.078, 0.0)]
    wb.lathe(p + "FlareShell", cart, M["glow_orange"], origin=(0.03, 0, -0.105), segs=28, angle=40)
    wb.cyl(p + "FlareShellBase", (0.03, 0, -0.105), (0.045, 0, -0.105), 0.0178, M["brass"], verts=28, bevel=0.001)
    return root


# ------------------------------------------------------------------ EMP grenade
def build_grenade(M, pack):
    p = "EMP_"
    root = wb.begin("EMP_Grenade", pack)
    body = [(-0.04, 0.0), (-0.04, 0.02), (-0.037, 0.027), (-0.03, 0.031), (0.025, 0.031), (0.032, 0.027),
            (0.036, 0.02), (0.036, 0.0)]
    wb.lathe(p + "Body", body, M["dark"], axis=(0, 0, 1), segs=36)
    wb.cyls(p + "GlowBands", [((0, 0, -0.018), (0, 0, -0.012), 0.0318), ((0, 0, 0.008), (0, 0, 0.014), 0.0318)],
            M["glow_cyan"], verts=36)
    ribs = []
    for i in range(8):
        a = i * 45 + 22.5
        ribs.append(((0.0318 * math.cos(math.radians(a)), 0.0318 * math.sin(math.radians(a)), -0.002),
                     (0.006, 0.006, 0.05), (0, 0, a)))
    wb.boxes(p + "Ribs", ribs, M["metal"], bevel=0.0015, segs=2)
    wb.cyl(p + "Fuze", (0, 0, 0.034), (0, 0, 0.05), 0.012, M["metal"], verts=24, bevel=0.002)
    wb.prism(p + "Spoon", [(0.004, 0.05), (0.02, 0.05), (0.037, 0.031), (0.037, -0.016), (0.031, -0.018),
                           (0.031, 0.029), (0.016, 0.044), (0.004, 0.044)], 0.012, M["yellow"], bevel=0.0015)
    ring = [(0.0018 * math.cos(math.radians(a)), 0.011 + 0.0018 * math.sin(math.radians(a)))
            for a in range(0, 361, 30)]
    wb.lathe(p + "PinRing", ring, M["steel"], origin=(-0.022, 0, 0.044), axis=(0, 1, 0), segs=24, angle=60)
    wb.cyl(p + "Pin", (-0.012, 0, 0.044), (0.0, 0, 0.044), 0.0015, M["steel"], verts=8, bevel=0)
    wb.cyl(p + "Antenna", (0, 0, 0.05), (0, 0, 0.074), 0.0015, M["metal"], verts=8, bevel=0)
    ball = [(-0.005, 0.0), (-0.0035, 0.0035), (0.0, 0.005), (0.0035, 0.0035), (0.005, 0.0)]
    wb.lathe(p + "AntennaBall", ball, M["glow_cyan"], origin=(0, 0, 0.077), axis=(0, 0, 1), segs=16, angle=60)
    return root


# ------------------------------------------------------------------ ammo crate + loose rounds
def build_ammo(M, pack):
    p = "AMMO_"
    root = wb.begin("Ammo_Crate", pack)
    L, W, H = 0.26, 0.12, 0.16
    wb.box(p + "Body", (0, 0, H / 2), (L, W, H), M["olive"], bevel=0.006, segs=3)
    wb.box(p + "Lid", (0, 0, H + 0.012), (L + 0.008, W + 0.008, 0.026), M["olive_dk"], bevel=0.005, segs=3)
    wb.boxes(p + "SidePanels", [((0, s * (W / 2 + 0.001), 0.072), (L - 0.05, 0.004, 0.08)) for s in (-1, 1)],
             M["olive"], bevel=0.002)
    wb.box(p + "Stripe", (0, -(W / 2 + 0.0032), 0.125), (L - 0.05, 0.002, 0.016), M["yellow"], bevel=0)
    stencil = [((-0.075 + i * 0.022, -(W / 2 + 0.0032), 0.072), (0.014, 0.002, 0.028)) for i in range(4)]
    stencil += [((0.04, -(W / 2 + 0.0032), 0.072), (0.06, 0.002, 0.008))]
    wb.boxes(p + "Stencil", stencil, M["yellow"], bevel=0)
    wb.cyls(p + "HandlePosts", [((s * 0.06, 0, H + 0.024), (s * 0.06, 0, H + 0.036), 0.006) for s in (-1, 1)],
            M["metal"], verts=12)
    wb.cyl(p + "Handle", (-0.07, 0, H + 0.04), (0.07, 0, H + 0.04), 0.008, M["metal"], verts=16, bevel=0.002)
    wb.cyl(p + "HandleGrip", (-0.045, 0, H + 0.04), (0.045, 0, H + 0.04), 0.0105, M["rubber"], verts=16,
           bevel=0.003)
    wb.box(p + "Latch", (L / 2 + 0.006, 0, H - 0.01), (0.008, 0.05, 0.05), M["metal"], bevel=0.002)
    wb.cyl(p + "Hinge", (-L / 2 - 0.004, -0.05, H + 0.002), (-L / 2 - 0.004, 0.05, H + 0.002), 0.006, M["metal"],
           verts=16)
    # loose rifle rounds and shotgun shells lying in front
    case = [(0.0, 0.0), (0.0, 0.0058), (0.002, 0.0058), (0.002, 0.0052), (0.004, 0.006), (0.036, 0.0058),
            (0.041, 0.0042), (0.046, 0.0042), (0.046, 0.0)]
    tip = [(0.0, 0.0), (0.0, 0.0041), (0.008, 0.0039), (0.018, 0.0022), (0.023, 0.0)]
    for i, (x, y, a) in enumerate([(-0.07, -0.12, 10), (-0.02, -0.13, -15), (0.03, -0.115, 25)]):
        d = (math.cos(math.radians(a)), math.sin(math.radians(a)), 0)
        wb.lathe(p + "RoundCase%d" % i, case, M["brass"], origin=(x, y, 0.006), axis=d, segs=16, angle=40)
        wb.lathe(p + "RoundTip%d" % i, tip, M["copper"],
                 origin=(x + 0.046 * d[0], y + 0.046 * d[1], 0.006), axis=d, segs=16, angle=40)
    for i, (x, y, a) in enumerate([(0.08, -0.13, 70), (0.11, -0.12, 100)]):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        wb.cyl(p + "ShellBase%d" % i, (x, y, 0.0108), (x + 0.012 * c, y + 0.012 * s, 0.0108), 0.0112, M["brass"],
               verts=20, bevel=0.001)
        wb.cyl(p + "Shell%d" % i, (x + 0.012 * c, y + 0.012 * s, 0.0108), (x + 0.07 * c, y + 0.07 * s, 0.0108),
               0.0105, M["shell_red"], verts=20, bevel=0.0015)
    return root
