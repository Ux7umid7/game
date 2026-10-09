"""Export each asset root (and its children) to its own .glb for Godot 4.

The root is moved to the origin for the export and put back afterwards. Modifiers (bevels) are applied,
lights and cameras are skipped, +Y up (Godot converts automatically).
"""
import os
import bpy


def export_roots(names, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    done = []
    for name in names:
        root = bpy.data.objects.get(name)
        if root is None:
            continue
        saved = root.matrix_world.copy()
        root.location, root.rotation_euler = (0, 0, 0), (0, 0, 0)
        bpy.context.view_layer.update()
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        root.select_set(True)
        for o in root.children_recursive:
            if o.type in ("MESH", "EMPTY"):
                o.select_set(True)
        bpy.context.view_layer.objects.active = root
        path = os.path.join(out_dir, name + ".glb")
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                                  export_lights=False, export_cameras=False, export_yup=True)
        root.matrix_world = saved
        done.append(path)
    bpy.context.view_layer.update()
    return done
