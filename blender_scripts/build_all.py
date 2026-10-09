"""Rebuild the whole weapon pack. In Blender: Scripting tab -> open this file -> Run Script."""
import sys
import importlib
import os

def _here():
    f = globals().get("__file__")
    if f and os.path.isfile(f):
        return os.path.dirname(os.path.abspath(f))
    import bpy  # run from Blender's Text Editor: use the text block's file path
    for t in bpy.data.texts:
        if t.filepath and os.path.basename(t.filepath) == "build_all.py":
            return os.path.dirname(os.path.abspath(bpy.path.abspath(t.filepath)))
    raise RuntimeError("Open blender_scripts/build_all.py from disk in the Text Editor, then run it.")


HERE = _here()
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import wb, w_ar, w_pistol, w_smg, w_shotgun, w_sniper, w_extras, stage  # noqa: E402

for m in (wb, w_ar, w_pistol, w_smg, w_shotgun, w_sniper, w_extras, stage):
    importlib.reload(m)


def main():
    M = wb.make_materials()
    pack = wb.get_coll("Weapon_Pack")
    w_ar.build(M, pack)
    w_pistol.build(M, pack)
    w_smg.build(M, pack)
    w_shotgun.build(M, pack)
    w_sniper.build(M, pack)
    w_extras.build_crossbow(M, pack)
    w_extras.build_hatchet(M, pack)
    w_extras.build_flaregun(M, pack)
    w_extras.build_grenade(M, pack)
    w_extras.build_ammo(M, pack)
    stage.build(pack)


main()
