"""Headless build + save + render.

blender.exe --background --factory-startup --python render_headless.py -- [--no-render] [--samples N]
"""
import os
import sys
import runpy
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
samples = int(argv[argv.index("--samples") + 1]) if "--samples" in argv else 64

# start from an empty scene (drop the factory cube)
c = bpy.data.objects.get("Cube")
if c is not None:
    bpy.data.objects.remove(c, do_unlink=True)

runpy.run_path(os.path.join(HERE, "build_all.py"), run_name="__main__")

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

blend = os.path.join(GAME, "weapon_pack.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
print("SAVED", blend)

if "--no-render" not in argv:
    out = os.path.join(GAME, "renders")
    os.makedirs(out, exist_ok=True)
    shots = [a.split("=", 1)[1] for a in argv if a.startswith("--shot=")] or ["SheetCam"]
    for cam_name in shots:
        sc.camera = bpy.data.objects[cam_name]
        if cam_name == "CloseCam":
            sc.render.resolution_x, sc.render.resolution_y = 1600, 900
        else:
            sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
        sc.render.filepath = os.path.join(out, cam_name + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)
    sc.camera = bpy.data.objects["SheetCam"]
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    bpy.ops.wm.save_mainfile()
