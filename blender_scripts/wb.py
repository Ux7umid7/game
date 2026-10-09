"""Weapon-builder helpers for the stylized island weapon pack.

Axes: +X = muzzle / forward, +Z = up, -Y = weapon's right side (faces the camera).
Units are metres (real-world scale).
"""
import bpy
import bmesh
import math
from mathutils import Vector, Matrix

CUR = {"coll": None, "root": None}


# ---------------------------------------------------------------- colours / materials
def srgb(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)


def _bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _set(bsdf, key, val):
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = val


def mat_basic(name, hexcol, metal=0.0, rough=0.6, emit=None, emit_str=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = _bsdf(m)
    _set(b, "Base Color", srgb(hexcol))
    _set(b, "Metallic", metal)
    _set(b, "Roughness", rough)
    if emit:
        _set(b, "Emission Color", srgb(emit))
        _set(b, "Emission Strength", emit_str)
    m.diffuse_color = srgb(hexcol)
    return m


def _ramp_mat(name, stops, tex_kind, scale, rough, interp="CONSTANT", metal=0.0, extra=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BSDF_PRINCIPLED", "OUTPUT_MATERIAL"):
            nt.nodes.remove(n)
    b = _bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    if tex_kind == "noise":
        tx = nt.nodes.new("ShaderNodeTexNoise")
        tx.inputs["Scale"].default_value = 1.0
        tx.inputs["Detail"].default_value = 2.0
        tx.inputs["Roughness"].default_value = 0.45
    else:  # wood grain, running along the weapon length (X)
        tx = nt.nodes.new("ShaderNodeTexWave")
        tx.wave_type = "BANDS"
        tx.bands_direction = "Z"
        tx.inputs["Scale"].default_value = 1.0
        tx.inputs["Distortion"].default_value = 2.5
        tx.inputs["Detail"].default_value = 2.0
        tx.inputs["Detail Scale"].default_value = 1.0
    nt.links.new(mp.outputs["Vector"], tx.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.interpolation = interp
    els = rp.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = stops[0][0]
    els[0].color = srgb(stops[0][1])
    for pos, col in stops[1:]:
        e = els.new(pos)
        e.color = srgb(col)
    nt.links.new(tx.outputs["Fac"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, "Roughness", rough)
    _set(b, "Metallic", metal)
    m.diffuse_color = srgb(stops[0][1])
    return m


def make_materials():
    M = {}
    M["metal"] = mat_basic("WPN_Gunmetal", "#2E3236", metal=0.75, rough=0.42)
    M["dark"] = mat_basic("WPN_DarkPolymer", "#24272A", rough=0.7)
    M["black"] = mat_basic("WPN_Black", "#0E0F10", rough=0.8)
    M["olive"] = mat_basic("WPN_Olive", "#6E6C3C", rough=0.75)
    M["olive_dk"] = mat_basic("WPN_OliveDark", "#4C4F2E", rough=0.75)
    M["rust"] = mat_basic("WPN_RustBrown", "#9A5631", rough=0.7)
    M["teal"] = mat_basic("WPN_TealTape", "#2E6B66", rough=0.85)
    M["rubber"] = mat_basic("WPN_Rubber", "#1A1B1C", rough=0.95)
    M["steel"] = mat_basic("WPN_Steel", "#9BA3AB", metal=0.9, rough=0.3)
    M["brass"] = mat_basic("WPN_Brass", "#C99A3B", metal=0.95, rough=0.3)
    M["copper"] = mat_basic("WPN_Copper", "#B8653A", metal=0.95, rough=0.35)
    M["shell_red"] = mat_basic("WPN_ShellRed", "#B02A22", rough=0.5)
    M["canvas"] = mat_basic("WPN_Canvas", "#7A7350", rough=0.95)
    M["rope"] = mat_basic("WPN_Rope", "#B89A63", rough=0.95)
    M["lens"] = mat_basic("WPN_Lens", "#1F6FD1", metal=0.3, rough=0.05, emit="#1F6FD1", emit_str=0.6)
    M["reddot"] = mat_basic("WPN_RedDotGlass", "#FF3B30", rough=0.05, emit="#FF3B30", emit_str=3.0)
    M["glow_cyan"] = mat_basic("WPN_GlowCyan", "#35E0FF", rough=0.3, emit="#35E0FF", emit_str=6.0)
    M["glow_orange"] = mat_basic("WPN_GlowOrange", "#FF7A1A", rough=0.3, emit="#FF7A1A", emit_str=5.0)
    M["flare_red"] = mat_basic("WPN_FlareRed", "#C2301B", rough=0.45)
    M["yellow"] = mat_basic("WPN_HazardYellow", "#E0B12A", rough=0.6)
    M["light_lens"] = mat_basic("WPN_FlashlightLens", "#FFF4D6", rough=0.05, emit="#FFF4D6", emit_str=2.0)
    M["camo"] = _ramp_mat("WPN_Camo", [(0.0, "#4C4F2E"), (0.42, "#6E6C3C"), (0.58, "#9A5631"), (0.74, "#3A3E30")],
                          "noise", (9.0, 9.0, 9.0), 0.75)
    M["wood"] = _ramp_mat("WPN_Wood", [(0.0, "#6A2F14"), (0.45, "#8A421F"), (1.0, "#9E5328")],
                          "wave", (1.5, 6.0, 7.0), 0.6, interp="LINEAR")
    M["wood_dk"] = _ramp_mat("WPN_WoodDark", [(0.0, "#45200F"), (0.45, "#5C2C15"), (1.0, "#70391C")],
                             "wave", (1.5, 6.0, 7.0), 0.6, interp="LINEAR")
    M["axe_head"] = _axe_mat()
    return M


def _axe_mat():
    """Dark forged steel with a bright sharpened edge (gradient along +X)."""
    m = bpy.data.materials.get("WPN_AxeHead") or bpy.data.materials.new("WPN_AxeHead")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type not in ("BSDF_PRINCIPLED", "OUTPUT_MATERIAL"):
            nt.nodes.remove(n)
    b = _bsdf(m)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.088
    mr.inputs["From Max"].default_value = 0.1
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = srgb("#33373B")
    rp.color_ramp.elements[1].color = srgb("#C9D0D6")
    nt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], rp.inputs["Fac"])
    nt.links.new(rp.outputs["Color"], b.inputs["Base Color"])
    _set(b, "Metallic", 0.85)
    _set(b, "Roughness", 0.35)
    m.diffuse_color = srgb("#5A6066")
    return m


# ---------------------------------------------------------------- scene structure
def get_coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


def begin(name, parent_coll):
    """Start a weapon: (re)create its collection and a root empty at the origin."""
    coll = get_coll(name, parent_coll)
    for o in list(coll.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = "ARROWS"
    root.empty_display_size = 0.08
    coll.objects.link(root)
    CUR["coll"] = coll
    CUR["root"] = root
    return root


def _finish(obj, mat, bevel, segs=2, angle=35, smooth=True, harden=True):
    CUR["coll"].objects.link(obj)
    obj.parent = CUR["root"]
    if mat is not None:
        obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
        obj.data.set_sharp_from_angle(angle=math.radians(angle))
    if bevel and bevel > 0:
        add_bevel(obj, bevel, segs, harden)
    return obj


def add_bevel(obj, width, segs=2, harden=True):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segs
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(35)
    m.harden_normals = harden
    return m


def _obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def _cube_into(bm, c, s, rot=None):
    r = bmesh.ops.create_cube(bm, size=1.0)
    vs = r["verts"]
    bmesh.ops.scale(bm, vec=Vector(s), verts=vs)
    if rot:
        R = Matrix.Rotation(math.radians(rot[0]), 4, "X") @ Matrix.Rotation(math.radians(rot[1]), 4, "Y") @ \
            Matrix.Rotation(math.radians(rot[2]), 4, "Z")
        bmesh.ops.transform(bm, matrix=R, verts=vs)
    bmesh.ops.translate(bm, vec=Vector(c), verts=vs)


# ---------------------------------------------------------------- primitives
def box(name, c, s, mat, bevel=0.003, rot=None, segs=2):
    bm = bmesh.new()
    _cube_into(bm, c, s, rot)
    return _finish(_obj(name, bm), mat, bevel, segs)


def boxes(name, items, mat, bevel=0.0015, segs=1):
    """Many boxes in one mesh. items: [(center, size) or (center, size, rot)]"""
    bm = bmesh.new()
    for it in items:
        _cube_into(bm, it[0], it[1], it[2] if len(it) > 2 else None)
    return _finish(_obj(name, bm), mat, bevel, segs)


def _prism_into(bm, pts, thick, y=0.0):
    vs = [bm.verts.new((x, y - thick / 2, z)) for x, z in pts]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [e for e in r["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, thick, 0), verts=nv)


def prism(name, pts, thick, mat, bevel=0.003, y=0.0, segs=2):
    """2D outline in the XZ plane [(x, z), ...] extruded along Y, centred on y."""
    bm = bmesh.new()
    _prism_into(bm, pts, thick, y)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(_obj(name, bm), mat, bevel, segs)


def _cyl_into(bm, p0, p1, r, verts=24, r2=None):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts,
                                radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    M = Matrix.Translation((p0 + p1) / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=res["verts"])


def cyl(name, p0, p1, r, mat, verts=24, bevel=0.0015, r2=None, segs=2):
    bm = bmesh.new()
    _cyl_into(bm, p0, p1, r, verts, r2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(_obj(name, bm), mat, bevel, segs)


def cyls(name, items, mat, verts=16, bevel=0.0, segs=1):
    """Many cylinders in one mesh. items: [(p0, p1, r)]"""
    bm = bmesh.new()
    for p0, p1, r in items:
        _cyl_into(bm, p0, p1, r, verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _finish(_obj(name, bm), mat, bevel, segs)


def lathe(name, prof, mat, origin=(0, 0, 0), axis=(1, 0, 0), segs=32, bevel=0.0, angle=35):
    """Revolve a profile [(along_axis, radius), ...] around an axis through origin."""
    bm = bmesh.new()
    vs = [bm.verts.new((a, 0.0, r)) for a, r in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(1, 0, 0), angle=2 * math.pi,
                   steps=segs, use_merge=True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    q = Vector((1, 0, 0)).rotation_difference(Vector(axis).normalized())
    M = Matrix.Translation(origin) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return _finish(_obj(name, bm), mat, bevel, 2, angle)


def apply_mods(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev)
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    me.name = obj.name
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def cut(obj, *cutters, keep_bevel=None):
    """Boolean-difference the cutters out of obj (applied), then delete cutters."""
    bevels = [(m.width, m.segments) for m in obj.modifiers if m.type == "BEVEL"]
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    for c in cutters:
        b = obj.modifiers.new("Cut", "BOOLEAN")
        b.operation = "DIFFERENCE"
        b.solver = "EXACT"
        b.object = c
    for c in cutters:
        c.modifiers.clear()
    apply_mods(obj)
    for c in cutters:
        me = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for p in obj.data.polygons:
        p.use_smooth = True
    obj.data.set_sharp_from_angle(angle=math.radians(35))
    w = keep_bevel if keep_bevel is not None else (bevels[0] if bevels else None)
    if w:
        add_bevel(obj, w[0], w[1])
    return obj


def mirror_y(obj):
    """Add a copy of obj mirrored to the other side (Y)."""
    m = obj.modifiers.new("MirrorY", "MIRROR")
    m.use_axis[0] = False
    m.use_axis[1] = True
    m.use_axis[2] = False
    m.mirror_object = CUR["root"]
    obj.modifiers.move(len(obj.modifiers) - 1, 0)
    return obj


def arc(cx, cz, r, a0, a1, n=8):
    """Points on an arc in XZ (degrees, 0 = +X, counter-clockwise)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def place(root, loc, rot=(0, 0, 0), scale=1.0):
    root.location = loc
    root.rotation_euler = [math.radians(a) for a in rot]
    root.scale = (scale, scale, scale)
