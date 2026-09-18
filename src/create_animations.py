import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(r'E:\AI_Playground\420');OUT=ROOT/'build'/'420_Smoking'/'assets'
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
scene.render.fps=25;scene.render.fps_base=1
END_FRAME=300
# Finish inhaling, lower the prop, then wait three full seconds before exhaling.
TIMING={'raise':[1,2],'inhale':[2,4],'lower':[4,5],'hold':[5,8],'exhale':[8,11],'settle':[11,12]}
if 'sitting chair' not in bpy.data.actions:
    with bpy.data.libraries.load(str(ROOT/'assets'/'animation_lab.blend')) as (source,target):
        target.actions=['sitting chair']
rig=bpy.data.objects['male_skeleton'];rig.animation_data.action=bpy.data.actions['sitting chair']
rig.animation_data.action_slot=rig.animation_data.action.slots[0]
for tr in rig.animation_data.nla_tracks:tr.mute=True
scene.frame_set(0);bpy.context.view_layer.update()
base={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
def reset():
    for b in rig.pose.bones:b.matrix_basis=base[b.name].copy()
    bpy.context.view_layer.update()
def aim(b,target):
    m=b.matrix.copy();q=(b.tail-b.head).normalized().rotation_difference((target-b.head).normalized())
    m=Matrix.Translation(b.head)@q.to_matrix().to_4x4()@Matrix.Translation(-b.head)@m
    b.matrix=m;bpy.context.view_layer.update()
def arm(side,target,pole):
    upper=rig.pose.bones['Bip01 '+side+' UpperArm'];fore=rig.pose.bones['Bip01 '+side+' Forearm'];hand=rig.pose.bones['Bip01 '+side+' Hand']
    root=upper.head.copy();l1=(fore.head-root).length;l2=(hand.head-fore.head).length
    d=(target-root);length=min(d.length,l1+l2-.001);u=d.normalized()
    p=pole-root;v=(p-u*p.dot(u)).normalized()
    a=(l1*l1-l2*l2+length*length)/(2*length);h=math.sqrt(max(0,l1*l1-a*a))
    elbow=root+u*a+v*h;aim(upper,elbow);aim(fore,target)
    return hand
def smooth(v):return v*v*(3-2*v)
def phase(f):
    if f<25:return 0
    if f<50:return smooth((f-25)/25)
    if f<100:return 1
    if f<125:return 1-smooth((f-100)/25)
    return 0
restR=Vector((-1.8,-2.5,7.3));restL=Vector((1.65,-2.3,7.4))
for old_action_name in ['420_smoke_chillum','420_smoke_joint']:
    old_action=bpy.data.actions.get(old_action_name)
    if old_action:bpy.data.actions.remove(old_action)
actions=[];qa={}
for kind in ['chillum','joint']:
    act=bpy.data.actions.new('420_smoke_'+kind);act.use_fake_user=True;rig.animation_data.action=act
    errors=[]
    grip_local=None
    # Solve the mouth pose first, then retain that grip in hand-local space.
    for f in [80]+[v for v in range(0,END_FRAME+1,5) if v!=80]:
        scene.frame_set(f);reset();t=phase(f)
        highR=Vector((-.95,-3.4,12.65)) if kind=='chillum' else Vector((-1.2,-3.5,12.75))
        highL=Vector((.6,-3.1,12.6))
        targetR=restR.lerp(highR,t);targetL=restL.lerp(highL,t) if kind=='chillum' else restL
        handR=arm('R',targetR,Vector((-4,-2,9)));handL=arm('L',targetL,Vector((4,-2,9)))
        # Keep the hands converging underneath the bowl, and wrist relaxed for joint.
        hand_direction=Vector((.45,-.25,.3))
        if kind=='joint':hand_direction=hand_direction.lerp(Vector((.65,.35,.1)),t)
        aim(handR,handR.head+hand_direction)
        if kind=='joint':
            twist=Quaternion((handR.tail-handR.head).normalized(),math.pi*.5*t)
            handR.matrix=Matrix.Translation(handR.head)@twist.to_matrix().to_4x4()@Matrix.Translation(-handR.head)@handR.matrix
            bpy.context.view_layer.update()
        if kind=='chillum':
            aim(handL,handL.head+Vector((-.6,-.1,0)))
            # Turn the supporting palm upward instead of draping its back below the grip.
            twist=Quaternion((handL.tail-handL.head).normalized(),math.pi*t)
            handL.matrix=Matrix.Translation(handL.head)@twist.to_matrix().to_4x4()@Matrix.Translation(-handL.head)@handL.matrix
            bpy.context.view_layer.update()
        prop=rig.pose.bones['Bip01 Prop2']
        if kind=='chillum':
            mouth=Vector((-.045,-2.85,13.25))
            origin=mouth.copy()
            direction=Vector((0,-.8,.6)).normalized()
        else:
            # User-directed adjustment: lower only the joint by 0.15 units.
            origin=Vector((-.045,-2.85,13.10))
            direction=Vector((-.3,-1,0)).normalized()
        if grip_local is None:
            grip_local=handR.matrix.inverted()@Matrix.Translation(origin)@direction.to_track_quat('Z','Y').to_matrix().to_4x4()
        prop.matrix=handR.matrix@grip_local
        bpy.context.view_layer.update()
        errors.append((handR.head-targetR).length)
        for b in rig.pose.bones:
            b.rotation_mode='QUATERNION'
            b.keyframe_insert(data_path='location',frame=f,group=b.name)
            b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=b.name)
    for fc in act.fcurves:
        for kp in fc.keyframe_points:kp.interpolation='LINEAR'
    actions.append(act);qa[kind]={'duration_seconds':12,'fps':25,'timing_seconds':TIMING,'smoke_in_game_implemented':False,'max_right_wrist_target_error':max(errors),'finger_bones_present':False,'in_game_verified':False}
# Only our two clips enter the skeleton export.
for tr in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(tr)
rig.animation_data.action=actions[0]
track=rig.animation_data.nla_tracks.new();strip=track.strips.new(actions[1].name,0,actions[1]);track.mute=True
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
getattr(bpy.ops,'export').kenshi_ogre_skeleton_objects(filepath=str(OUT/'420_smoking_male.skeleton'),export_animation=True)
# Preview links use prop bone's evaluated world matrix, matching the test attachment.
for name,kind in [('420_chillum','chillum'),('420_joint','joint')]:
    old=bpy.data.objects.get('preview_'+kind)
    if old:bpy.data.objects.remove(old,do_unlink=True)
    obj=bpy.data.objects[name].copy();obj.data=bpy.data.objects[name].data.copy();obj.name='preview_'+kind;scene.collection.objects.link(obj)
    obj.location=(0,0,0);obj.rotation_euler=(0,0,0)
    constraint=obj.constraints.new('COPY_TRANSFORMS');constraint.target=rig;constraint.subtarget='Bip01 Prop2'
    obj.hide_render=kind!='chillum'
chair=bpy.data.objects.get('preview_seat')
if not chair:
    chair=bpy.data.objects['420_smoking_seat'].copy();chair.name='preview_seat';scene.collection.objects.link(chair);chair.location=(0,0,0)
human=bpy.data.objects['human_male-0'];material=bpy.data.materials.new('QA mannequin');material.diffuse_color=(.36,.32,.25,1);human.data.materials.clear();human.data.materials.append(material)
studio=bpy.data.scenes['420_Assets'];scene.world=studio.world
for ob in studio.objects:
    if ob.type=='LIGHT' and ob.name not in scene.objects:scene.collection.objects.link(ob)
bpy.ops.object.camera_add(location=(21,-29,19));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.5,8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=20;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=20;scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
rig.animation_data.action=actions[0];scene.frame_set(80);scene.frame_start=0;scene.frame_end=END_FRAME
scene.render.filepath=str(ROOT/'qa'/'chillum_pose.png');bpy.ops.render.render(write_still=True)
rig.animation_data.action=actions[1];scene.frame_set(80)
bpy.data.objects['preview_chillum'].hide_render=True;bpy.data.objects['preview_joint'].hide_render=False
scene.render.filepath=str(ROOT/'qa'/'joint_pose.png');bpy.ops.render.render(write_still=True)
(ROOT/'qa'/'animation_checks.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets'/'smoking_animation_work.blend'))
print(qa)
