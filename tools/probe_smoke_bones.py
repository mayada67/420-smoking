import bpy, json
from mathutils import Vector
rig=bpy.data.objects['male_skeleton']
rig.animation_data.action=bpy.data.actions['420_smoke_chillum']
bpy.context.scene.frame_set(200)
bpy.context.view_layer.update()
head=rig.pose.bones['Bip01 Head']
target=Vector((-.045,-2.96,13.25))
print('MOUTH_LOCAL', list(head.matrix.inverted() @ target))
print('HEAD_WORLD', list(head.matrix.translation))
