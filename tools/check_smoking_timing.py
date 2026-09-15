"""Run in Blender background: read back exported skeleton and verify its hold."""
import bpy,json
from pathlib import Path
root=Path(r'E:\AI_Playground\420')
bpy.context.scene.render.fps=25
getattr(bpy.ops,'import').kenshi_ogre_skeleton_objects(
    filepath=str(root/'build/420_Smoking/assets/420_smoking_male.skeleton'),
    import_animations=True,use_selected_skeleton=False,round_frames=False)
rig=bpy.context.view_layer.objects.active
report={}
for kind in ['chillum','joint']:
    action=bpy.data.actions['420_smoke_'+kind];rig.animation_data.action=action
    rig.animation_data.action_slot=action.slots[0]
    for track in rig.animation_data.nla_tracks:track.mute=True
    frames=action.frame_range
    assert abs((frames[1]-frames[0])/25-12)<.001,list(frames)
    poses=[]
    for frame in [125,150,175,200]:
        bpy.context.scene.frame_set(frame)
        poses.append([v for b in rig.pose.bones for row in b.matrix for v in row])
    hold_error=max(abs(a-b) for pose in poses[1:] for a,b in zip(poses[0],pose))
    assert hold_error<.0001,hold_error
    # A stationary prop at the mouth would pass a hold-only test, but would
    # still look like continuous inhalation. Verify it is lowered first.
    bpy.context.scene.frame_set(80)
    inhale_prop=rig.pose.bones['Bip01 Prop2'].matrix.translation.copy()
    bpy.context.scene.frame_set(125)
    held_prop=rig.pose.bones['Bip01 Prop2'].matrix.translation.copy()
    separation=(held_prop-inhale_prop).length
    assert separation>2.0,separation
    loop=[]
    for frame in [0,300]:
        bpy.context.scene.frame_set(frame)
        loop.append([v for b in rig.pose.bones for row in b.matrix for v in row])
    loop_error=max(abs(a-b) for a,b in zip(*loop))
    assert loop_error<.0001,loop_error
    report[kind]={'duration_seconds':12,'hold_seconds':3,'hold_interval':[5,8],'prop_displacement_before_hold':separation,'hold_error':hold_error,'loop_error':loop_error}
(root/'qa/smoking_timing_roundtrip.json').write_text(json.dumps(report,indent=2))
print(report)
