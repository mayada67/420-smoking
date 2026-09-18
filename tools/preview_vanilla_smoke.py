"""Close-up preview of exported props; game alpha clipping approximated in Blender."""
import bpy
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[1]
assets = root / 'build/420_Smoking/assets'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 24
scene.render.resolution_x = 1000
scene.render.resolution_y = 700
scene.render.resolution_percentage = 100
scene.world.color = (.15, .15, .15)
mat = bpy.data.materials.new('Game alpha clip approximation')
mat.use_nodes = True
n = mat.node_tree.nodes
n.clear()
links = mat.node_tree.links
out = n.new('ShaderNodeOutputMaterial')
mix = n.new('ShaderNodeMixShader')
transparent = n.new('ShaderNodeBsdfTransparent')
surface = n.new('ShaderNodeBsdfDiffuse')
color = n.new('ShaderNodeTexImage')
color.image = bpy.data.images.load(str(assets/'420_smoke_prop_diffuse.png'))
color.image.alpha_mode = 'NONE'  # Kenshi uses this channel for gloss, not transparency.
mask = n.new('ShaderNodeTexImage')
mask.image = bpy.data.images.load(str(assets/'420_smoke_prop_normal.png'))
mask.image.colorspace_settings.name = 'Non-Color'
clip = n.new('ShaderNodeMath')
clip.operation = 'GREATER_THAN'
clip.inputs[1].default_value = .5
links.new(color.outputs['Color'], surface.inputs['Color'])
links.new(mask.outputs['Alpha'], clip.inputs[0])
links.new(clip.outputs[0], mix.inputs[0])
links.new(transparent.outputs[0], mix.inputs[1])
links.new(surface.outputs[0], mix.inputs[2])
links.new(mix.outputs[0], out.inputs[0])
for kind, offset in [('chillum', -.65), ('joint', .65)]:
    before = set(bpy.data.objects)
    getattr(bpy.ops, 'import').kenshi_ogre_objects(filepath=str(assets/f'420_{kind}_lit.mesh'))
    for obj in set(bpy.data.objects)-before:
        if obj.type == 'MESH':
            obj.location.x += offset
            obj.data.materials.clear()
            obj.data.materials.append(mat)
points = [obj.matrix_world @ Vector(p) for obj in scene.objects if obj.type == 'MESH' for p in obj.bound_box]
bpy.context.view_layer.update()
points = [obj.matrix_world @ Vector(p) for obj in scene.objects if obj.type == 'MESH' for p in obj.bound_box]
center = (Vector(tuple(min(p[i] for p in points) for i in range(3))) + Vector(tuple(max(p[i] for p in points) for i in range(3)))) / 2
bpy.ops.object.camera_add(location=center+Vector((3,-6,2)))
cam = bpy.context.object
cam.rotation_euler = (center-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 3.8
scene.camera = cam
bpy.ops.object.light_add(type='AREA', location=center+Vector((1,-3,5)))
bpy.context.object.data.energy = 450
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 5
scene.render.filepath = str(root/'qa/vanilla_smoke_subtle_preview.png')
bpy.ops.render.render(write_still=True)
