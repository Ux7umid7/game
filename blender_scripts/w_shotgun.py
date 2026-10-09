"""Pump shotgun (bottom-left in the reference) + additions: buttstock shell carrier, shell in port."""
import wb


def _stock_top(x):
    return 0.022 + (x + 0.098) * (0.01 / 0.342)


def _stock_bot(x):
    return -0.072 + (x + 0.2) * (0.053 / 0.24)


def _wrap(name, x0, x1, thick, mat, M, pad=0.003):
    pts = [(x0, _stock_top(x0) + pad), (x1, _stock_top(x1) + pad), (x1, _stock_bot(x1) - pad),
           (x0, _stock_bot(x0) - pad)]
    return wb.prism(name, pts, thick, mat, bevel=0.006, segs=3)


def build(M, pack):
    p = "SG_"
    root = wb.begin("Shotgun", pack)

    # receiver
    rec = [(-0.1, -0.035), (0.1, -0.035), (0.1, 0.017), (0.09, 0.026), (-0.08, 0.026), (-0.1, 0.022)]
    wb.prism(p + "Receiver", rec, 0.044, M["metal"], bevel=0.004)
    wb.box(p + "EjectionPort", (0.035, -0.0222, 0.002), (0.065, 0.002, 0.024), M["black"], bevel=0.001)
    wb.cyl(p + "ShellInPort", (0.008, -0.0135, 0.002), (0.062, -0.0135, 0.002), 0.0105, M["shell_red"],
           verts=20, bevel=0.001)
    wb.cyl(p + "ShellInPortBase", (0.003, -0.0135, 0.002), (0.012, -0.0135, 0.002), 0.011, M["brass"],
           verts=20, bevel=0.001)
    wb.box(p + "LoadingPort", (0.03, 0, -0.0355), (0.07, 0.03, 0.002), M["black"], bevel=0)
    wb.cyl(p + "Safety", (-0.075, -0.024, -0.03), (-0.075, 0.024, -0.03), 0.0035, M["black"], verts=12, bevel=0)
    wb.mirror_y(wb.cyl(p + "Pin", (-0.04, -0.0222, -0.025), (-0.04, -0.0232, -0.025), 0.003, M["dark"],
                       verts=12, bevel=0))
    tg = wb.prism(p + "TriggerGuard", [(-0.065, -0.035), (0.035, -0.035), (0.028, -0.066), (-0.05, -0.068)],
                  0.012, M["dark"], bevel=0.002)
    wb.cut(tg, wb.prism(p + "_cut", [(-0.05, -0.035), (0.024, -0.035), (0.018, -0.059), (-0.04, -0.061)],
                        0.04, None, bevel=0))
    wb.prism(p + "Trigger", [(-0.016, -0.036), (-0.009, -0.036), (-0.011, -0.047), (-0.017, -0.056),
                             (-0.022, -0.056), (-0.018, -0.047)], 0.006, M["black"], bevel=0.001)

    # barrel + magazine tube + pump
    wb.cyl(p + "Barrel", (0.09, 0, 0.0), (0.64, 0, 0.0), 0.012, M["metal"], verts=28)
    wb.cyl(p + "Muzzle", (0.625, 0, 0.0), (0.645, 0, 0.0), 0.0138, M["metal"], verts=28, bevel=0.002)
    wb.cyl(p + "Bore", (0.64, 0, 0.0), (0.6455, 0, 0.0), 0.0095, M["black"], verts=20, bevel=0)
    wb.cyl(p + "BeadSight", (0.632, 0, 0.011), (0.632, 0, 0.017), 0.0025, M["brass"], verts=12, bevel=0.001)
    wb.cyl(p + "MagTube", (0.09, 0, -0.027), (0.55, 0, -0.027), 0.0115, M["metal"], verts=24)
    wb.cyl(p + "MagCap", (0.548, 0, -0.027), (0.572, 0, -0.027), 0.0135, M["metal"], verts=24, bevel=0.003)
    wb.mirror_y(wb.box(p + "ActionBar", (0.15, -0.0125, -0.027), (0.12, 0.003, 0.006), M["metal"],
                       bevel=0.001))
    wb.box(p + "PumpCore", (0.295, 0, -0.029), (0.18, 0.044, 0.034), M["wood"], bevel=0.01, segs=3)
    ribs = [((0.215 + i * 0.016, 0, -0.029), (0.009, 0.05, 0.042)) for i in range(11)]
    wb.boxes(p + "PumpRibs", ribs, M["wood"], bevel=0.004, segs=2)
    wb.box(p + "BarrelBand", (0.51, 0, -0.0135), (0.026, 0.034, 0.058), M["olive"], bevel=0.009, segs=3)

    # stock (wood) with butt pad, olive wrap and teal tape
    stock = [(-0.098, 0.022), (-0.44, 0.012), (-0.44, -0.125), (-0.2, -0.072), (-0.162, -0.082),
             (-0.13, -0.07), (-0.098, -0.035)]
    wb.prism(p + "Stock", stock, 0.046, M["wood"], bevel=0.008, segs=3)
    _wrap(p + "OliveWrap", -0.44, -0.408, 0.05, M["olive"], M)
    _wrap(p + "TapeWrap", -0.39, -0.362, 0.052, M["teal"], M)
    wb.prism(p + "ButtPad", [(-0.44, 0.016), (-0.458, 0.018), (-0.458, -0.13), (-0.44, -0.129)], 0.05,
             M["rubber"], bevel=0.006, segs=3)

    # ================= additions: shell carrier on the stock =================
    _wrap(p + "ShellCarrier", -0.33, -0.215, 0.058, M["canvas"], M, pad=0.004)
    shells, bases = [], []
    for i in range(5):
        x = -0.312 + i * 0.022
        zc = (_stock_top(x) + _stock_bot(x)) / 2
        shells.append(((x, -0.037, zc - 0.022), (x, -0.037, zc + 0.04), 0.0102))
        bases.append(((x, -0.037, zc - 0.034), (x, -0.037, zc - 0.022), 0.0108))
    wb.cyls(p + "CarrierShells", shells, M["shell_red"], verts=20, bevel=0.001)
    wb.cyls(p + "CarrierShellBases", bases, M["brass"], verts=20, bevel=0.001)
    for k, dz in enumerate((-0.012, 0.02)):
        x0, x1 = -0.326, -0.219
        z0 = (_stock_top(x0) + _stock_bot(x0)) / 2 + dz
        z1 = (_stock_top(x1) + _stock_bot(x1)) / 2 + dz
        wb.box(p + "CarrierLoop%d" % k, ((x0 + x1) / 2, -0.0395, (z0 + z1) / 2), (x1 - x0, 0.008, 0.009),
               M["canvas"], bevel=0.002, rot=(0, -6, 0))
    return root
