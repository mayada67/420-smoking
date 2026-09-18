"""Blender: transfer local pose curves to the native female rest skeleton."""
import bpy, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'build/toolchain/blender_wheel'))
female=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Kenshi\data\character\meshes\female_skeleton\female_skeleton.skeleton')
for family, prefix in [('smoking','420_smoke_'),('reclined','420_recline_')]:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for action in list(bpy.data.actions): bpy.data.actions.remove(action)
    bpy.context.scene.render.fps=25
    getattr(bpy.ops,'import').kenshi_ogre_skeleton_objects(filepath=str(root/f'build/420_Smoking/assets/420_{family}_male.skeleton'),import_animations=True,use_selected_skeleton=False)
    actions=[a for a in bpy.data.actions if a.name.startswith(prefix)]
    assert len(actions)==2
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    getattr(bpy.ops,'import').kenshi_ogre_skeleton_objects(filepath=str(female),import_animations=False,use_selected_skeleton=False)
    rig=bpy.context.view_layer.objects.active
    for bone in rig.pose.bones: bone.rotation_mode='QUATERNION'
    rig.animation_data_create()
    for action in actions:
        slot=action.slots[0]
        bag=action.layers[0].strips[0].channelbag(slot)
        for curve in list(bag.fcurves):
            if any(f'pose.bones["{name}"]' in curve.data_path for name in ['Bip01 Jaw','Bip01 JawNub']):
                bag.fcurves.remove(curve)
        track=rig.animation_data.nla_tracks.new();track.name=action.name
        strip=track.strips.new(action.name,0,action);strip.action_slot=slot
        track.mute=True
    bpy.context.scene.frame_start=0;bpy.context.scene.frame_end=300
    getattr(bpy.ops,'export').kenshi_ogre_skeleton_objects(filepath=str(root/f'build/420_Smoking/assets/420_{family}_female.skeleton'),export_animation=True)
