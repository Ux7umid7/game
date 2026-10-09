"""Bolt-action sniper rifle (bottom-right in the reference) + additions: bipod, cheek riser, sling studs."""
import wb


def build(M, pack):
    p = "SNP_"
    root = wb.begin("Sniper", pack)

    # receiver + bolt
    wb.cyl(p + "Receiver", (-0.12, 0, 0), (0.1, 0, 0), 0.0165, M["metal"], verts=28, bevel=0.002)
    wb.cyl(p + "BoltShroud", (-0.15, 0, 0), (-0.118, 0, 0), 0.013, M["metal"], verts=24, bevel=0.002)
    wb.box(p + "EjectionPort", (-0.015, -0.012, 0.007), (0.055, 0.012, 0.012), M["black"], bevel=0.001)
    wb.cyl(p + "BoltHandle", (-0.085, -0.012, 0.004), (-0.096, -0.05, -0.022), 0.0042, M["metal"], verts=12,
           bevel=0)
    knob = [(-0.012, 0.0), (-0.011, 0.005), (-0.006, 0.009), (0.0, 0.0102), (0.006, 0.009), (0.011, 0.005),
            (0.012, 0.0)]
    wb.lathe(p + "BoltKnob", knob, M["metal"], origin=(-0.097, -0.054, -0.025), axis=(0, 0, 1), segs=20,
             angle=60)

    # barrel + muzzle brake
    wb.cyl(p + "Barrel", (0.09, 0, 0), (0.74, 0, 0), 0.0125, M["metal"], verts=28, r2=0.0095)
    brake = [(0.735, 0.0), (0.735, 0.0155), (0.748, 0.0155), (0.748, 0.012), (0.756, 0.012), (0.756, 0.0165),
             (0.768, 0.0165), (0.768, 0.012), (0.776, 0.012), (0.776, 0.0165), (0.792, 0.0165),
             (0.795, 0.013), (0.795, 0.007), (0.782, 0.007), (0.782, 0.0)]
    wb.lathe(p + "MuzzleBrake", brake, M["metal"], segs=28)

    # stock
    stock = [(0.43, -0.006), (0.442, -0.02), (0.428, -0.036), (0.1, -0.046), (-0.06, -0.046),
             (-0.085, -0.062), (-0.108, -0.128), (-0.152, -0.13), (-0.165, -0.08), (-0.42, -0.112),
             (-0.432, -0.112), (-0.432, 0.024), (-0.36, 0.03), (-0.21, 0.028), (-0.16, 0.004),
             (-0.12, -0.005)]
    wb.prism(p + "Stock", stock, 0.05, M["wood"], bevel=0.008, segs=3)
    wb.prism(p + "ButtPad", [(-0.432, 0.027), (-0.452, 0.028), (-0.452, -0.116), (-0.432, -0.115)], 0.054,
             M["rubber"], bevel=0.006, segs=3)
    wb.prism(p + "ButtWrap", [(-0.432, 0.029), (-0.405, 0.028), (-0.405, -0.111), (-0.432, -0.115)], 0.055,
             M["olive"], bevel=0.006, segs=3)
    wb.prism(p + "GripPanel", [(-0.092, -0.066), (-0.11, -0.118), (-0.142, -0.12), (-0.138, -0.08)], 0.054,
             M["olive_dk"], bevel=0.004, segs=3)
    wb.box(p + "ForendTape", (0.3, 0, -0.022), (0.034, 0.056, 0.042), M["teal"], bevel=0.012, segs=3)
    wb.box(p + "ForendTape2", (0.245, 0, -0.023), (0.012, 0.055, 0.04), M["olive"], bevel=0.01, segs=3)
    wb.box(p + "Magazine", (0.03, 0, -0.058), (0.064, 0.032, 0.03), M["metal"], bevel=0.003)
    tg = wb.prism(p + "TriggerGuard", [(-0.092, -0.044), (-0.008, -0.044), (-0.014, -0.074), (-0.082, -0.075)],
                  0.012, M["metal"], bevel=0.002)
    wb.cut(tg, wb.prism(p + "_cut", [(-0.08, -0.044), (-0.019, -0.044), (-0.024, -0.067), (-0.073, -0.068)],
                        0.04, None, bevel=0))
    wb.prism(p + "Trigger", [(-0.05, -0.045), (-0.044, -0.045), (-0.046, -0.055), (-0.052, -0.063),
                             (-0.057, -0.063), (-0.053, -0.055)], 0.006, M["black"], bevel=0.001)

    # scope
    sz = 0.056
    body = [(-0.175, 0.0), (-0.175, 0.019), (-0.17, 0.0215), (-0.125, 0.0215), (-0.11, 0.0162),
            (-0.1, 0.0152), (0.085, 0.0152), (0.125, 0.0245), (0.205, 0.0245), (0.21, 0.022), (0.21, 0.0)]
    wb.lathe(p + "ScopeBody", body, M["dark"], origin=(0, 0, sz), segs=36)
    wb.cyl(p + "ScopeObjectiveSleeve", (0.135, 0, sz), (0.2, 0, sz), 0.0252, M["olive"], verts=36, bevel=0.002)
    wb.cyl(p + "ScopeEyeSleeve", (-0.165, 0, sz), (-0.13, 0, sz), 0.0222, M["olive"], verts=36, bevel=0.002)
    wb.cyl(p + "ScopeLensFront", (0.2095, 0, sz), (0.2105, 0, sz), 0.021, M["lens"], verts=36, bevel=0)
    wb.cyl(p + "ScopeLensRear", (-0.1755, 0, sz), (-0.1745, 0, sz), 0.016, M["lens"], verts=36, bevel=0)
    wb.cyl(p + "ScopeTurretTop", (0.0, 0, sz + 0.012), (0.0, 0, sz + 0.034), 0.012, M["dark"], verts=24,
           bevel=0.002)
    wb.cyl(p + "ScopeTurretTopCap", (0.0, 0, sz + 0.033), (0.0, 0, sz + 0.038), 0.0125, M["olive"], verts=24,
           bevel=0.0015)
    wb.cyl(p + "ScopeTurretSide", (0.0, -0.012, sz), (0.0, -0.034, sz), 0.012, M["dark"], verts=24,
           bevel=0.002)
    wb.cyl(p + "ScopeTurretSideCap", (0.0, -0.033, sz), (0.0, -0.038, sz), 0.0125, M["olive"], verts=24,
           bevel=0.0015)
    wb.cyl(p + "ScopeSaddle", (-0.022, 0, sz), (0.022, 0, sz), 0.019, M["dark"], verts=32, bevel=0.003)
    for i, x in enumerate((-0.07, 0.06)):
        wb.cyl(p + "ScopeRing%d" % i, (x - 0.009, 0, sz), (x + 0.009, 0, sz), 0.0195, M["metal"], verts=32,
               bevel=0.002)
        wb.box(p + "ScopeRingBase%d" % i, (x, 0, 0.025), (0.018, 0.024, 0.028), M["metal"], bevel=0.002)
    wb.box(p + "ScopeRail", (0.0, 0, 0.0165), (0.17, 0.02, 0.006), M["metal"], bevel=0.0015)

    # ================= additions =================
    wb.prism(p + "CheekRiser", [(-0.372, 0.028), (-0.215, 0.026), (-0.222, 0.046), (-0.36, 0.049)], 0.04,
             M["olive_dk"], bevel=0.004, segs=3)
    wb.cyls(p + "CheekRiserPosts", [((-0.33, 0, 0.02), (-0.33, 0, 0.03), 0.004),
                                     ((-0.26, 0, 0.02), (-0.26, 0, 0.03), 0.004)], M["metal"], verts=12)
    # bipod (deployed)
    wb.box(p + "BipodMount", (0.38, 0, -0.042), (0.03, 0.026, 0.014), M["dark"], bevel=0.002)
    legs, feet = [], []
    for s in (-1, 1):
        legs.append(((0.385, s * 0.012, -0.048), (0.42, s * 0.05, -0.19), 0.0055))
        feet.append(((0.42, s * 0.05, -0.186), (0.4215, s * 0.054, -0.2), 0.009))
    wb.cyls(p + "BipodLegs", legs, M["metal"], verts=14)
    wb.cyls(p + "BipodLegsInner", [((a[0] + 0.6 * (b[0] - a[0]), a[1] + 0.6 * (b[1] - a[1]),
                                     a[2] + 0.6 * (b[2] - a[2])), b, 0.0068) for a, b, r in legs],
            M["dark"], verts=14)
    wb.cyls(p + "BipodFeet", feet, M["rubber"], verts=14, bevel=0.002)
    wb.cyls(p + "SlingStuds", [((-0.36, 0, -0.106), (-0.36, 0, -0.118), 0.004),
                               ((0.335, 0, -0.036), (0.335, 0, -0.048), 0.004)], M["metal"], verts=12)
    return root
