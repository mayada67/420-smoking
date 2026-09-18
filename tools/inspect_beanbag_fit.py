import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/smoking_animation_work.blend'))
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
rig=bpy.data.objects['male_skeleton']
scene.frame_set(80);bpy.context.view_layer.update()
for b in rig.pose.bones:
    if any(s in b.name.lower() for s in ['pelvis','thigh','calf','foot']):print('BONE',b.name,list(rig.matrix_world@b.head))
deps=bpy.context.evaluated_depsgraph_get()
human=bpy.data.objects['human_male-0'];ev=human.evaluated_get(deps);mesh=ev.to_mesh()
pts=[ev.matrix_world@v.co for v in mesh.vertices]
print('BODY_BOUNDS',[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)])
ev.to_mesh_clear()
print('RIG',list(rig.location),list(rig.rotation_euler))
