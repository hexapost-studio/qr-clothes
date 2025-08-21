"""Blender script to place a 3D model using perspective data and render."""
import json
import sys

import bpy
import mathutils


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    if len(argv) < 3:
        raise SystemExit("Usage: blender -b -P render_blender.py -- <input> <output> <matrix-json> [model]")
    image_path, output_path, matrix_json = argv[:3]
    model_path = argv[3] if len(argv) > 3 else None
    return image_path, output_path, matrix_json, model_path


def setup_scene(image_path: str):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # Camera
    cam_data = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (0, -3, 1)
    cam_obj.rotation_euler = (1.2, 0, 0)

    # Light
    light_data = bpy.data.lights.new(name="light", type="SUN")
    light_obj = bpy.data.objects.new(name="light", object_data=light_data)
    light_obj.location = (0, -2, 2)
    scene.collection.objects.link(light_obj)

    # Background plane with the image
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.active_object
    mat = bpy.data.materials.new(name="bg")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = bpy.data.images.load(image_path)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
    plane.data.materials.append(mat)
    plane.location = (0, 0, 0)
    return plane


def load_model(model_path: str | None):
    if model_path:
        bpy.ops.import_scene.obj(filepath=model_path)
        obj = bpy.context.selected_objects[0]
    else:
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(0, 0, 0.25))
        obj = bpy.context.active_object
    return obj


def main():
    image_path, output_path, matrix_json, model_path = parse_args()
    plane = setup_scene(image_path)
    obj = load_model(model_path)

    matrix = mathutils.Matrix(json.loads(matrix_json))
    obj.matrix_world = matrix

    # Render
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
