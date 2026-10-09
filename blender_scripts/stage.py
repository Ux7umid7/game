"""Display stage: lays the pack out like the reference sheet (beige backdrop, soft shadows, ortho camera)."""
import math
import bpy
import wb

LAYOUT = {
    # name: (location, rotation_deg)
    "AR_Carbine": ((-0.95, 0, 0.62), (0, 0, -15)),
    "Pistol": ((-0.08, 0, 0.66), (0, 0, -15)),
    "SMG": ((0.78, 0, 0.64), (0, 0, -15)),
    "Shotgun": ((-0.74, 0, 0.2), (0, 0, -12)),
    "Sniper": ((0.56, 0, 0.2), (0, 0, -12)),
    "Crossbow": ((-1.0, 0, -0.26), (0, 0, -32)),
    "Hatchet": ((-0.3, 0, -0.44), (0, 28, -20)),
    "FlareGun": ((0.1, 0, -0.24), (0, 0, -20)),
    "EMP_Grenade": ((0.42, 0, -0.27), (0, 0, -20)),
    "Ammo_Crate": ((0.95, 0, -0.42), (0, 0, -25)),
}


def build(pack):
    for name, (loc, rot) in LAYOUT.items():
        o = bpy.data.objects.get(name)
        if o:
            wb.place(o, loc, rot)

    stage = wb.get_coll("Stage")
    for o in list(stage.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # beige backdrop wall with a curved floor sweep
    bd = wb.mat_basic("STG_Backdrop", "#CFC6BA", rough=0.9)
    me = bpy.data.meshes.new("Backdrop")
    import bmesh
    bm = bmesh.new()
    R, y0, zf = 0.6, 0.45, -0.75
    pts = [(y0 - 3.0, zf)] + [(y0 - R + R * math.cos(math.radians(270 + 90 * i / 12)),
                                 zf + R + R * math.sin(math.radians(270 + 90 * i / 12))) for i in range(13)] + \
          [(y0, 2.5)]
    left = [bm.verts.new((-4.0, y, z)) for y, z in pts]
    right = [bm.verts.new((4.0, y, z)) for y, z in pts]
    for i in range(len(pts) - 1):
        bm.faces.new((left[i], left[i + 1], right[i + 1], right[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    wall = bpy.data.objects.new("Backdrop", me)
    stage.objects.link(wall)
    wall.data.materials.append(bd)
    for p in wall.data.polygons:
        p.use_smooth = True

    # lights
    def light(name, kind, loc, rot, energy, size=None, color=(1, 1, 1), angle=None):
        ld = bpy.data.lights.get(name) or bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = color
        if size is not None:
            ld.size = size
        if angle is not None:
            ld.angle = math.radians(angle)
        ob = bpy.data.objects.new(name, ld)
        stage.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = [math.radians(a) for a in rot]
        return ob

    light("Key_Sun", "SUN", (-2, -3, 4), (68, 0, -18), 3.6, angle=11, color=(1.0, 0.96, 0.9))
    light("Fill_Area", "AREA", (2.5, -3.5, 1.2), (75, 0, 35), 250, size=3.0, color=(0.85, 0.9, 1.0))
    light("Rim_Area", "AREA", (0, -1.0, 3.0), (10, 0, 0), 120, size=4.0)

    # world
    w = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = w
    w.use_nodes = True
    bgn = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bgn.inputs["Color"].default_value = wb.srgb("#D9D2C7")
    bgn.inputs["Strength"].default_value = 0.45

    # camera (orthographic, like the reference sheet)
    cd = bpy.data.cameras.get("SheetCam") or bpy.data.cameras.new("SheetCam")
    cd.type = "ORTHO"
    cd.ortho_scale = 2.95
    cam = bpy.data.objects.new("SheetCam", cd)
    stage.objects.link(cam)
    cam.location = (-0.05, -6.0, 0.8)
    cam.rotation_euler = (math.radians(84), 0, 0)
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080

    # 3/4 perspective close-up of the AR carbine
    from mathutils import Vector
    cd2 = bpy.data.cameras.get("CloseCam") or bpy.data.cameras.new("CloseCam")
    cd2.lens = 50
    cam2 = bpy.data.objects.new("CloseCam", cd2)
    stage.objects.link(cam2)
    cam2.location = (-0.42, -1.4, 0.9)
    aim = Vector((-0.86, 0.0, 0.6)) - cam2.location
    cam2.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()

    # hide the stock startup light/camera if present
    for n in ("Light", "Camera"):
        o = bpy.data.objects.get(n)
        if o:
            o.hide_render = True
            o.hide_viewport = True
    return cam
