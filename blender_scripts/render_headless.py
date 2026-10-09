"""Headless build + save (+ glTF export) + render.

Weapons:
  blender --background --factory-startup --python render_headless.py -- --samples 64 --shot=SheetCam --shot=CloseCam
Houses + jeep:
  blender --background --factory-startup --python render_headless.py -- --build build_env.py --blend env_pack.blend
          --export --shot=Cam_Overview --shot=Cam_House_Cottage ...
Options: --no-render, --samples N, --export (writes exports/<Asset>.glb for every root in Env_Pack)
"""
import os
import sys
import runpy
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def opt(name, default):
    return argv[argv.index(name) + 1] if name in argv else default


samples = int(opt("--samples", 64))
build = opt("--build", "build_all.py")
blend = opt("--blend", "weapon_pack.blend")

c = bpy.data.objects.get("Cube")  # start from an empty scene (drop the factory cube)
if c is not None:
    bpy.data.objects.remove(c, do_unlink=True)

runpy.run_path(os.path.join(HERE, build), run_name="__main__")

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = samples
sc.cycles.use_denoising = True
sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "AgX - Punchy"
except TypeError:
    pass

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(GAME, blend))
print("SAVED", blend)

if "--export" in argv:
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import export_glb
    pack = bpy.data.collections.get("Env_Pack")
    names = [o.name for o in pack.all_objects if o.parent is None and o.type == "EMPTY"] if pack else []
    for path in export_glb.export_roots(names, os.path.join(GAME, "exports")):
        print("EXPORTED", path)

if "--no-render" not in argv:
    out = os.path.join(GAME, "renders")
    os.makedirs(out, exist_ok=True)
    shots = [a.split("=", 1)[1] for a in argv if a.startswith("--shot=")] or ["SheetCam"]
    first = sc.camera
    for cam_name in shots:
        sc.camera = bpy.data.objects[cam_name]
        sc.render.resolution_x, sc.render.resolution_y = (1920, 1080) if cam_name == "SheetCam" else (1600, 900)
        sc.render.filepath = os.path.join(out, cam_name + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)
    sc.camera = first
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    bpy.ops.wm.save_mainfile()
