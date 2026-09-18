import bpy
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/reclined_animation_work.blend'))
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
for o in scene.objects:
    if o.type=='MESH':o.hide_render=o.name not in ['human_male-0','preview_chillum']
with bpy.data.libraries.load(str(root/'assets/beanbag.blend')) as (source,target):
    target.objects=['420_beanbag']
chair=target.objects[0];scene.collection.objects.link(chair)
scene.frame_set(200)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03))
floor=bpy.context.object;mat=bpy.data.materials.new('Floor');mat.diffuse_color=(.17,.18,.19,1);floor.data.materials.append(mat)
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=80
for label,loc in [('front',(19,-27,16)),('side',(25,-1,11)),('inhale',(19,-27,16))]:
    scene.frame_set(80 if label=='inhale' else 200)
    cam=scene.camera;cam.location=loc;cam.rotation_euler=(Vector((0,0,6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=19
    scene.render.filepath=str(root/'qa'/f'beanbag_fit_{label}.png');bpy.ops.render.render(write_still=True)
