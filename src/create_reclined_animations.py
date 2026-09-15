"""Derive beanbag-only relaxed poses while preserving mouth/prop choreography."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/smoking_animation_work.blend'))
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
rig=bpy.data.objects['male_skeleton']
for tr in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(tr)
bones=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
def aim(b,target):
    q=(b.tail-b.head).normalized().rotation_difference((target-b.head).normalized())
    b.matrix=Matrix.Translation(b.head)@q.to_matrix().to_4x4()@Matrix.Translation(-b.head)@b.matrix
    bpy.context.view_layer.update()
actions=[]
for kind in ['chillum','joint']:
    source=bpy.data.actions['420_smoke_'+kind];rig.animation_data.action=source;rig.animation_data.action_slot=source.slots[0]
    samples={}
    for f in range(0,301,5):
        scene.frame_set(f);samples[f]={b.name:b.matrix.copy() for b in bones}
    pivot=samples[0]['Bip01 Pelvis'].translation
    transform=Matrix.Translation(pivot+Vector((0,.25,-1.6)))@Matrix.Rotation(math.radians(-28),4,'X')@Matrix.Translation(-pivot)
    act=bpy.data.actions.new('420_recline_'+kind);rig.animation_data.action=act
    for f,pose in samples.items():
        scene.frame_set(f)
        for b in bones:
            b.matrix=transform@pose[b.name];bpy.context.view_layer.update()
        t=0 if f<25 or f>=125 else (1 if 50<=f<=100 else ((f-25)/25 if f<50 else (125-f)/25))
        t=t*t*(3-2*t)
        prop=rig.pose.bones['Bip01 Prop2'];right=rig.pose.bones['Bip01 R Hand']
        grip=right.matrix.inverted()@prop.matrix
        for side,rest in [('R',(-2.9,-.3,4.6)),('L',(3.1,.1,4.3))]:
            upper=rig.pose.bones['Bip01 '+side+' UpperArm'];fore=rig.pose.bones['Bip01 '+side+' Forearm'];hand=rig.pose.bones['Bip01 '+side+' Hand']
            hm=hand.matrix.copy();target=Vector(rest).lerp(hand.head,t if side=='R' or kind=='chillum' else 0)
            origin=upper.head.copy();l1=(fore.head-origin).length;l2=(hand.head-fore.head).length
            delta=target-origin;d=min(delta.length,l1+l2-.001);u=delta.normalized()
            pole=Vector(((-4.5 if side=='R' else 4.5),1,6))-origin;v=(pole-u*pole.dot(u)).normalized()
            a=(l1*l1-l2*l2+d*d)/(2*d)
            aim(upper,origin+u*a+v*math.sqrt(max(0,l1*l1-a*a)));aim(fore,target)
            hm.translation=hand.head.copy();hand.matrix=hm;bpy.context.view_layer.update()
        prop.matrix=right.matrix@grip;bpy.context.view_layer.update()
        for side,x,y in [('L',2.6,-6.5),('R',-2.9,-7.0)]:
            thigh=rig.pose.bones['Bip01 '+side+' Thigh'];calf=rig.pose.bones['Bip01 '+side+' Calf'];foot=rig.pose.bones['Bip01 '+side+' Foot']
            target=Vector((x,y,pose[foot.name].translation.z))
            origin=thigh.head.copy();l1=(calf.head-origin).length;l2=(foot.head-calf.head).length
            delta=target-origin;d=min(delta.length,l1+l2-.001);u=delta.normalized()
            pole=Vector((x,-3,7))-origin;v=(pole-u*pole.dot(u)).normalized()
            a=(l1*l1-l2*l2+d*d)/(2*d);knee=origin+u*a+v*math.sqrt(max(0,l1*l1-a*a))
            aim(thigh,knee);aim(calf,target)
            fm=pose[foot.name].copy();fm.translation=foot.head.copy();foot.matrix=fm;bpy.context.view_layer.update()
        for b in bones:
            b.rotation_mode='QUATERNION';b.keyframe_insert(data_path='location',frame=f);b.keyframe_insert(data_path='rotation_quaternion',frame=f)
    for fc in act.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    actions.append(act)
rig.animation_data.action=actions[0]
track=rig.animation_data.nla_tracks.new();track.strips.new(actions[1].name,0,actions[1]);track.mute=True
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
getattr(bpy.ops,'export').kenshi_ogre_skeleton_objects(filepath=str(ROOT/'build/420_Smoking/assets/420_reclined_male.skeleton'),export_animation=True)
scene.frame_set(200)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/reclined_animation_work.blend'))
