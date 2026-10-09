"""Rebuild the houses (3 variants) + jeep. In Blender: Scripting tab -> open this file -> Run Script."""
import sys
import importlib
import os


def _here():
    f = globals().get("__file__")
    if f and os.path.isfile(f):
        return os.path.dirname(os.path.abspath(f))
    import bpy  # run from Blender's Text Editor: use the text block's file path
    for t in bpy.data.texts:
        if t.filepath and os.path.basename(t.filepath) == "build_env.py":
            return os.path.dirname(os.path.abspath(bpy.path.abspath(t.filepath)))
    raise RuntimeError("Open blender_scripts/build_env.py from disk in the Text Editor, then run it.")


HERE = _here()
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import wb, env_mats, h_props, h_house, v_jeep, stage_env, export_glb  # noqa: E402

for m in (wb, env_mats, h_props, h_house, v_jeep, stage_env, export_glb):
    importlib.reload(m)

ASSETS = ("House_Ruined", "House_Cottage", "House_Upgraded", "Jeep")


def main():
    M = env_mats.make()
    pack = wb.get_coll("Env_Pack")
    h_house.build_house("House_Ruined", "ruined", M, pack)
    h_house.build_house("House_Cottage", "cottage", M, pack)
    h_house.build_house("House_Upgraded", "upgraded", M, pack)
    v_jeep.build_jeep(M, pack)
    stage_env.build(M)


main()
