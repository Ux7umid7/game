"""SMG with folding stock (top-right in the reference) + additions: holo sight, stock tape."""
import wb


def build(M, pack):
    p = "SMG_"
    root = wb.begin("SMG", pack)
    bz = -0.008  # bore height

    wb.box(p + "Receiver", (0.005, 0, 0.01), (0.19, 0.05, 0.05), M["metal"], bevel=0.004)
    wb.box(p + "RailBase", (0.005, 0, 0.039), (0.17, 0.022, 0.008), M["metal"], bevel=0.0015)
    wb.boxes(p + "RailTeeth", [((-0.075 + i * 0.01, 0, 0.0455), (0.005, 0.024, 0.005)) for i in range(17)],
             M["metal"], bevel=0.0008)
    wb.box(p + "EjectionPort", (0.035, -0.0252, 0.012), (0.045, 0.003, 0.015), M["black"], bevel=0.001)
    wb.box(p + "SidePanel", (-0.045, -0.0254, 0.008), (0.06, 0.002, 0.03), M["olive"], bevel=0.0008)

    # lower housing, grip, trigger, magazine
    lower = [(-0.085, -0.015), (0.1, -0.015), (0.1, -0.025), (0.066, -0.03), (0.063, -0.054),
             (0.018, -0.054), (0.015, -0.034), (-0.06, -0.034), (-0.085, -0.026)]
    wb.prism(p + "LowerHousing", lower, 0.046, M["dark"], bevel=0.003)
    grip = [(-0.012, -0.033), (-0.016, -0.05), (-0.035, -0.138), (-0.041, -0.15), (-0.076, -0.148),
            (-0.078, -0.138), (-0.056, -0.033)]
    wb.prism(p + "Grip", grip, 0.033, M["wood"], bevel=0.007, segs=3)
    wb.boxes(p + "TriggerGuard", [((0.002, 0, -0.06), (0.036, 0.011, 0.005)),
                                  ((0.017, 0, -0.048), (0.005, 0.011, 0.024))], M["metal"], bevel=0.0012)
    wb.prism(p + "Trigger", [(-0.002, -0.034), (0.004, -0.034), (0.002, -0.043), (-0.003, -0.051),
                             (-0.008, -0.051), (-0.004, -0.043)], 0.006, M["black"], bevel=0.001)
    wb.prism(p + "Magazine", [(0.022, -0.045), (0.059, -0.045), (0.069, -0.198), (0.034, -0.2)], 0.022,
             M["metal"], bevel=0.003)
    wb.box(p + "MagBase", (0.052, 0, -0.203), (0.044, 0.028, 0.01), M["dark"], bevel=0.003)
    wb.boxes(p + "MagWindow", [((0.042 + 0.01 * t, -0.0115, -0.065 - 0.12 * t), (0.012, 0.002, 0.006))
                               for t in (0.0, 0.25, 0.5, 0.75)], M["brass"], bevel=0)

    # handguard with real holes, barrel, compensator, cocking tube, front sight
    hg = wb.box(p + "Handguard", (0.143, 0, bz), (0.086, 0.056, 0.042), M["rust"], bevel=0.008, segs=3)
    cutters = [wb.cyl(p + "_cut", (0.118 + i * 0.025, -0.05, bz), (0.118 + i * 0.025, 0.05, bz), 0.0075,
                      None, verts=20, bevel=0) for i in range(3)]
    wb.cut(hg, *cutters)
    wb.cyl(p + "Barrel", (0.09, 0, bz), (0.215, 0, bz), 0.0085, M["metal"], verts=20)
    comp = [(0.212, 0.0), (0.212, 0.0125), (0.222, 0.0125), (0.222, 0.0105), (0.227, 0.0105),
            (0.227, 0.0135), (0.237, 0.0135), (0.237, 0.0105), (0.242, 0.0105), (0.242, 0.0135),
            (0.252, 0.0135), (0.254, 0.0115), (0.254, 0.0055), (0.244, 0.0055), (0.244, 0.0)]
    wb.lathe(p + "Compensator", comp, M["metal"], segs=24)
    wb.cyl(p + "CockingTube", (0.1, 0, 0.022), (0.2, 0, 0.022), 0.0105, M["metal"], verts=24)
    wb.cyl(p + "CockingLever", (0.172, -0.008, 0.022), (0.168, -0.034, 0.03), 0.0035, M["dark"], verts=12)
    wb.cyl(p + "CockingKnob", (0.168, -0.032, 0.03), (0.167, -0.04, 0.032), 0.0065, M["dark"], verts=16)
    wb.prism(p + "FrontSightPost", [(0.186, 0.03), (0.2, 0.03), (0.197, 0.044), (0.189, 0.044)], 0.012,
             M["metal"], bevel=0.0015)
    hood = wb.cyl(p + "FrontSightHood", (0.188, 0, 0.049), (0.198, 0, 0.049), 0.011, M["metal"], verts=24,
                  bevel=0.001)
    wb.cut(hood, wb.cyl(p + "_cut", (0.18, 0, 0.049), (0.21, 0, 0.049), 0.0075, None, verts=24, bevel=0))
    wb.box(p + "FrontSightPin", (0.193, 0, 0.046), (0.0025, 0.0025, 0.012), M["black"], bevel=0)
    wb.prism(p + "HandStop", [(0.152, -0.028), (0.178, -0.028), (0.172, -0.064), (0.16, -0.068),
                              (0.152, -0.058)], 0.03, M["olive_dk"], bevel=0.004, segs=3)

    # folding stock
    wb.cyl(p + "StockHinge", (-0.094, -0.028, -0.004), (-0.094, 0.028, -0.004), 0.012, M["metal"], verts=24)
    stock = [(-0.09, 0.03), (-0.27, 0.026), (-0.284, 0.03), (-0.29, 0.02), (-0.29, -0.08), (-0.28, -0.088),
             (-0.262, -0.088), (-0.1, -0.025), (-0.09, -0.02)]
    st = wb.prism(p + "Stock", stock, 0.03, M["olive"], bevel=0.005, segs=3)
    wb.cut(st, wb.prism(p + "_cut", [(-0.112, 0.012), (-0.255, 0.01), (-0.255, -0.062)], 0.08, None, bevel=0))
    wb.box(p + "ButtPlate", (-0.297, 0, -0.03), (0.016, 0.044, 0.124), M["rubber"], bevel=0.005, segs=3)

    # ================= additions =================
    wb.box(p + "StockTape", (-0.19, 0, 0.0195), (0.02, 0.034, 0.022), M["teal"], bevel=0.005, segs=3)
    wb.box(p + "HoloBase", (-0.005, 0, 0.0535), (0.052, 0.028, 0.01), M["dark"], bevel=0.002)
    holo = wb.prism(p + "HoloSight", [(-0.03, 0.056), (0.022, 0.056), (0.022, 0.09), (0.014, 0.097),
                                      (-0.022, 0.097), (-0.03, 0.089)], 0.034, M["olive_dk"], bevel=0.002)
    wb.cut(holo, wb.box(p + "_cut", (0.0, 0, 0.077), (0.1, 0.026, 0.028), None, bevel=0))
    wb.box(p + "HoloGlass", (0.016, 0, 0.077), (0.002, 0.026, 0.028), M["lens"], bevel=0)
    wb.cyl(p + "HoloButton", (-0.012, -0.017, 0.064), (-0.012, -0.021, 0.064), 0.004, M["glow_orange"],
           verts=12, bevel=0)
    return root
