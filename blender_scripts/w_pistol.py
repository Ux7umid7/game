"""Pistol (top-middle in the reference) + additions: suppressor, under-rail light."""
import wb


def build(M, pack):
    p = "PST_"
    root = wb.begin("Pistol", pack)

    # slide (bore axis at z = 0)
    slide = [(-0.075, -0.012), (0.105, -0.012), (0.105, 0.012), (0.098, 0.02), (-0.06, 0.02),
             (-0.075, 0.014)]
    wb.prism(p + "Slide", slide, 0.03, M["metal"], bevel=0.003)
    ser = [((-0.064 + i * 0.0045, -0.0152, 0.004), (0.0018, 0.0012, 0.024)) for i in range(7)]
    ser += [((x, 0.0152, z), s) for (x, y, z), s in ser]
    wb.boxes(p + "Serrations", ser, M["black"], bevel=0)
    wb.box(p + "EjectionPort", (0.02, 0, 0.0155), (0.04, 0.02, 0.01), M["black"], bevel=0.001)
    wb.box(p + "ChamberBlock", (0.022, 0, 0.0158), (0.03, 0.014, 0.01), M["copper"], bevel=0.001)
    wb.box(p + "FrontSight", (0.096, 0, 0.0235), (0.006, 0.005, 0.008), M["dark"], bevel=0.001)
    wb.prism(p + "RearSight", [(-0.066, 0.019), (-0.05, 0.019), (-0.052, 0.028), (-0.064, 0.028)],
             0.022, M["dark"], bevel=0.0015)
    wb.box(p + "RearSightDot", (-0.0659, -0.004, 0.025), (0.001, 0.003, 0.003), M["glow_orange"], bevel=0)
    wb.box(p + "RearSightDot2", (-0.0659, 0.004, 0.025), (0.001, 0.003, 0.003), M["glow_orange"], bevel=0)
    wb.cyl(p + "BarrelTip", (0.1, 0, 0), (0.108, 0, 0), 0.0075, M["metal"], verts=20, bevel=0.001)
    wb.cyl(p + "Bore", (0.104, 0, 0), (0.1085, 0, 0), 0.0045, M["black"], verts=16, bevel=0)

    # frame + grip
    frame = [(-0.072, -0.012), (0.1, -0.012), (0.1, -0.026), (0.03, -0.026), (0.02, -0.03),
             (-0.035, -0.03), (-0.072, -0.02)]
    wb.prism(p + "Frame", frame, 0.028, M["dark"], bevel=0.0025)
    grip = [(-0.035, -0.028), (-0.04, -0.06), (-0.048, -0.105), (-0.05, -0.122), (-0.092, -0.122),
            (-0.088, -0.1), (-0.08, -0.04), (-0.076, -0.016), (-0.072, -0.016)]
    wb.prism(p + "Grip", grip, 0.03, M["dark"], bevel=0.005, segs=3)
    panel = [(-0.043, -0.04), (-0.05, -0.1), (-0.084, -0.1), (-0.077, -0.04)]
    wb.mirror_y(wb.prism(p + "GripPanel", panel, 0.004, M["wood"], bevel=0.002, y=-0.0155, segs=3))
    wb.mirror_y(wb.cyl(p + "GripScrew", (-0.06, -0.0175, -0.05), (-0.06, -0.0185, -0.05), 0.0025,
                       M["brass"], verts=12, bevel=0))
    wb.box(p + "MagBase", (-0.071, 0, -0.126), (0.046, 0.032, 0.01), M["metal"], bevel=0.003)
    wb.prism(p + "Hammer", [(-0.074, 0.006), (-0.083, 0.012), (-0.088, 0.008), (-0.08, -0.002),
                            (-0.074, -0.004)], 0.008, M["metal"], bevel=0.001)
    tg = wb.prism(p + "TriggerGuard", [(-0.036, -0.026), (0.034, -0.026), (0.03, -0.054), (-0.03, -0.056)],
                  0.012, M["dark"], bevel=0.002)
    tgc = wb.prism(p + "_cut", [(-0.03, -0.026), (0.026, -0.026), (0.023, -0.048), (-0.026, -0.05)],
                   0.04, None, bevel=0)
    wb.cut(tg, tgc)
    wb.prism(p + "Trigger", [(-0.004, -0.028), (0.003, -0.028), (0.001, -0.038), (-0.006, -0.046),
                             (-0.011, -0.046), (-0.006, -0.038)], 0.006, M["black"], bevel=0.001)
    wb.mirror_y(wb.box(p + "SlideStop", (-0.005, -0.0155, -0.006), (0.024, 0.003, 0.005), M["black"],
                       bevel=0.001))
    # camo patch on the slide (the reference has an olive smear on top)
    wb.prism(p + "SlidePatch", [(0.0, 0.0205), (0.06, 0.0205), (0.052, 0.012), (0.012, 0.014)], 0.031,
             M["olive"], bevel=0.0015)

    # ================= additions =================
    sup = [(0.108, 0.0), (0.108, 0.006), (0.116, 0.006), (0.116, 0.0145), (0.12, 0.0165),
           (0.255, 0.0165), (0.259, 0.0145), (0.259, 0.005), (0.25, 0.005), (0.25, 0.0)]
    wb.lathe(p + "Suppressor", sup, M["olive_dk"], segs=32)
    wb.cyl(p + "SuppressorTape", (0.16, 0, 0), (0.185, 0, 0), 0.0172, M["teal"], verts=32, bevel=0.002)
    wb.box(p + "AccessoryRail", (0.068, 0, -0.03), (0.05, 0.016, 0.006), M["dark"], bevel=0.001)
    wb.box(p + "TacLight", (0.07, 0, -0.04), (0.05, 0.022, 0.018), M["black"], bevel=0.004, segs=3)
    wb.box(p + "TacLightLens", (0.0955, 0, -0.04), (0.002, 0.016, 0.012), M["light_lens"], bevel=0.0008)
    return root
