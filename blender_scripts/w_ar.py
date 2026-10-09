"""AR carbine (top-left in the reference) + additions: red-dot sight, vertical grip, flashlight."""
import wb


def build(M, pack):
    p = "AR_"
    root = wb.begin("AR_Carbine", pack)

    # --- upper receiver + rail
    wb.box(p + "UpperReceiver", (0.01, 0, 0.012), (0.22, 0.05, 0.05), M["metal"], bevel=0.004)
    wb.box(p + "EjectionPort", (0.045, -0.0252, 0.014), (0.055, 0.003, 0.016), M["black"], bevel=0.001)
    wb.cyl(p + "ForwardAssist", (-0.075, -0.018, 0.024), (-0.06, -0.034, 0.024), 0.008, M["metal"], verts=16)
    wb.box(p + "ChargingHandle", (-0.108, 0, 0.032), (0.018, 0.054, 0.008), M["metal"], bevel=0.002)
    wb.box(p + "RailBase", (0.01, 0, 0.041), (0.22, 0.024, 0.008), M["metal"], bevel=0.0015)
    teeth = [((-0.095 + i * 0.01, 0, 0.0475), (0.005, 0.026, 0.006)) for i in range(22)]
    wb.boxes(p + "RailTeeth", teeth, M["metal"], bevel=0.001)

    # --- lower receiver, grip, trigger
    lower = [(-0.10, -0.013), (0.12, -0.013), (0.12, -0.03), (0.096, -0.036), (0.092, -0.072),
             (0.026, -0.072), (0.02, -0.046), (-0.07, -0.046), (-0.10, -0.034)]
    wb.prism(p + "LowerReceiver", lower, 0.046, M["metal"], bevel=0.004)
    grip = [(-0.014, -0.045), (-0.018, -0.062), (-0.04, -0.15), (-0.048, -0.166), (-0.084, -0.162),
            (-0.088, -0.15), (-0.062, -0.045)]
    wb.prism(p + "PistolGrip", grip, 0.034, M["dark"], bevel=0.008, segs=3)
    ins = [(-0.03, -0.072), (-0.048, -0.142), (-0.072, -0.14), (-0.054, -0.072)]
    wb.mirror_y(wb.prism(p + "GripInsert", ins, 0.004, M["olive"], bevel=0.0015, y=-0.0175))
    wb.boxes(p + "TriggerGuard", [((0.002, 0, -0.071), (0.05, 0.012, 0.006)),
                                  ((0.023, 0, -0.058), (0.006, 0.012, 0.026))], M["metal"], bevel=0.0015)
    trig = [(-0.004, -0.044), (0.003, -0.044), (0.001, -0.056), (-0.004, -0.064), (-0.01, -0.065),
            (-0.006, -0.056)]
    wb.prism(p + "Trigger", trig, 0.006, M["black"], bevel=0.001)

    # --- magazine (curved)
    mag = [(0.086, -0.05), (0.088, -0.10), (0.095, -0.15), (0.108, -0.20), (0.118, -0.224),
           (0.067, -0.232), (0.055, -0.205), (0.043, -0.155), (0.034, -0.105), (0.03, -0.05)]
    wb.prism(p + "Magazine", mag, 0.024, M["metal"], bevel=0.003)
    wb.prism(p + "MagBasePlate", [(0.063, -0.226), (0.122, -0.218), (0.126, -0.232), (0.064, -0.242)],
             0.03, M["dark"], bevel=0.003)
    ribs = []
    for zz in (-0.09, -0.12, -0.15, -0.18):
        t = (zz + 0.05) / -0.18
        x0 = 0.03 + 0.03 * t * t + 0.004
        x1 = 0.086 + 0.03 * t * t - 0.004
        ribs.append((((x0 + x1) / 2, 0, zz), (x1 - x0, 0.026, 0.003), (0, -12 * t, 0)))
    wb.boxes(p + "MagRibs", ribs, M["dark"], bevel=0.0008)

    # --- buffer tube + stock
    wb.cyl(p + "BufferTube", (-0.10, 0, 0.006), (-0.33, 0, 0.006), 0.015, M["metal"], verts=24)
    stock = [(-0.215, 0.026), (-0.38, 0.031), (-0.386, 0.02), (-0.386, -0.085), (-0.372, -0.096),
             (-0.35, -0.096), (-0.30, -0.04), (-0.24, -0.019), (-0.215, -0.017)]
    st = wb.prism(p + "Stock", stock, 0.042, M["olive"], bevel=0.006, segs=3)
    hole = wb.prism(p + "_cut", [(-0.368, -0.018), (-0.305, -0.016), (-0.366, -0.074)], 0.08, None, bevel=0)
    wb.cut(st, hole)
    wb.box(p + "StockLever", (-0.27, 0, -0.03), (0.04, 0.03, 0.01), M["dark"], bevel=0.002)
    wb.box(p + "ButtPad", (-0.393, 0, -0.032), (0.016, 0.046, 0.136), M["rubber"], bevel=0.005, segs=3)

    # --- handguard, barrel, sights, muzzle
    wb.cyl(p + "DeltaRing", (0.112, 0, 0), (0.126, 0, 0), 0.035, M["metal"], verts=32)
    wb.box(p + "Handguard", (0.226, 0, 0), (0.2, 0.058, 0.06), M["camo"], bevel=0.016, segs=3)
    slots = []
    for i in range(4):
        x = 0.145 + i * 0.022
        for y in (-0.0292, 0.0292):
            slots.append(((x, y, 0.004), (0.008, 0.0016, 0.03)))
    wb.boxes(p + "HandguardSlots", slots, M["black"], bevel=0.0006)
    wb.box(p + "TapeWrap", (0.292, 0, 0), (0.03, 0.062, 0.064), M["teal"], bevel=0.016, segs=3)
    wb.box(p + "TapeWrapBack", (0.142, 0, 0), (0.016, 0.061, 0.063), M["olive_dk"], bevel=0.016, segs=3)
    wb.cyl(p + "HandguardCap", (0.326, 0, 0), (0.334, 0, 0), 0.03, M["metal"], verts=32)
    wb.cyl(p + "Barrel", (0.12, 0, 0), (0.472, 0, 0), 0.0095, M["metal"], verts=24)
    wb.box(p + "FrontSightBase", (0.35, 0, -0.004), (0.024, 0.026, 0.03), M["metal"], bevel=0.003)
    fs = wb.prism(p + "FrontSight", [(0.332, 0.008), (0.368, 0.008), (0.355, 0.064), (0.345, 0.064)],
                  0.016, M["metal"], bevel=0.002)
    fcut = wb.prism(p + "_cut", [(0.341, 0.017), (0.359, 0.017), (0.3505, 0.049)], 0.04, None, bevel=0)
    wb.cut(fs, fcut)
    wb.box(p + "FrontSightPost", (0.35, 0, 0.026), (0.003, 0.003, 0.02), M["black"], bevel=0)
    muz = [(0.47, 0.0), (0.47, 0.0125), (0.484, 0.0125), (0.484, 0.011), (0.489, 0.011), (0.489, 0.0138),
           (0.503, 0.0138), (0.503, 0.011), (0.508, 0.011), (0.508, 0.0138), (0.524, 0.0138),
           (0.526, 0.012), (0.526, 0.006), (0.514, 0.006), (0.514, 0.0)]
    wb.lathe(p + "MuzzleBrake", muz, M["metal"], segs=24)

    # --- rear flip sight
    rs = wb.prism(p + "RearSight", [(-0.096, 0.05), (-0.07, 0.05), (-0.073, 0.074), (-0.078, 0.083),
                                    (-0.088, 0.083), (-0.093, 0.074)], 0.03, M["dark"], bevel=0.002)
    rcut = wb.cyl(p + "_cut", (-0.11, 0, 0.073), (-0.06, 0, 0.073), 0.0035, None, verts=12, bevel=0)
    wb.cut(rs, rcut)

    # ================= additions =================
    # red-dot sight
    wb.box(p + "RedDotMount", (0.005, 0, 0.056), (0.05, 0.03, 0.012), M["dark"], bevel=0.002)
    rd = wb.cyl(p + "RedDotBody", (-0.022, 0, 0.081), (0.032, 0, 0.081), 0.021, M["olive_dk"], verts=32,
                bevel=0.003)
    rdc = wb.cyl(p + "_cut", (-0.04, 0, 0.081), (0.05, 0, 0.081), 0.0165, None, verts=32, bevel=0)
    wb.cut(rd, rdc)
    wb.box(p + "RedDotNeck", (0.005, 0, 0.063), (0.036, 0.02, 0.012), M["dark"], bevel=0.002)
    wb.cyl(p + "RedDotGlass", (0.012, 0, 0.081), (0.014, 0, 0.081), 0.0166, M["reddot"], verts=32, bevel=0)
    wb.cyl(p + "RedDotKnobTop", (0.005, 0, 0.1), (0.005, 0, 0.108), 0.007, M["dark"], verts=16)
    wb.cyl(p + "RedDotKnobSide", (0.005, -0.02, 0.081), (0.005, -0.03, 0.081), 0.007, M["dark"], verts=16)
    # vertical fore-grip
    wb.box(p + "LowerRail", (0.245, 0, -0.033), (0.06, 0.022, 0.008), M["metal"], bevel=0.0015)
    wb.cyl(p + "ForeGrip", (0.245, 0, -0.035), (0.252, 0, -0.112), 0.0145, M["olive_dk"], verts=24,
           r2=0.0135, bevel=0.003)
    wb.cyl(p + "ForeGripCap", (0.252, 0, -0.112), (0.2525, 0, -0.118), 0.0135, M["rubber"], verts=24,
           bevel=0.002)
    # flashlight on the right side
    wb.box(p + "LightMount", (0.2, -0.031, -0.004), (0.022, 0.01, 0.012), M["dark"], bevel=0.0015)
    wb.cyl(p + "Flashlight", (0.168, -0.044, -0.004), (0.226, -0.044, -0.004), 0.011, M["black"], verts=24,
           bevel=0.002)
    wb.cyl(p + "FlashlightHead", (0.222, -0.044, -0.004), (0.24, -0.044, -0.004), 0.0145, M["black"],
           verts=24, bevel=0.002)
    wb.cyl(p + "FlashlightLens", (0.2395, -0.044, -0.004), (0.2405, -0.044, -0.004), 0.012,
           M["light_lens"], verts=24, bevel=0)
    return root
