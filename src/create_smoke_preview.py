"""Blender-only smoke study. This does not export a Kenshi particle effect.

Run after create_animations.py, with smoking_animation_work.blend open.
The baked world-space puffs stay behind as the hand moves away.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'E:\AI_Playground\420')
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
rig=bpy.data.objects['male_skeleton']
for track in rig.animation_data.nla_tracks:track.mute=True
for obj in list(bpy.data.objects):
    if obj.name.startswith('smoke_preview_'):bpy.data.objects.remove(obj,do_unlink=True)

def puff(name,positions,birth,life,radius,density,exhale=False):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
    obj=bpy.context.object;obj.name='smoke_preview_'+name
    mat=bpy.data.materials.new(obj.name);mat.use_nodes=True
    nodes=mat.node_tree.nodes;nodes.clear();links=mat.node_tree.links
    out=nodes.new('ShaderNodeOutputMaterial');vol=nodes.new('ShaderNodeVolumePrincipled')
    vol.inputs['Color'].default_value=(.72,.74,.76,1)
    coord=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=3.8;noise.inputs['Detail'].default_value=3
    links.new(coord.outputs['Generated'],noise.inputs['Vector'])
    # Soft radial edge avoids solid-looking balls of smoke.
    distance=nodes.new('ShaderNodeVectorMath');distance.operation='DISTANCE'
    distance.inputs[1].default_value=(.5,.5,.5)
    links.new(coord.outputs['Generated'],distance.inputs[0])
    edge=nodes.new('ShaderNodeMapRange');edge.clamp=True
    edge.inputs['From Min'].default_value=.15;edge.inputs['From Max'].default_value=.5
    edge.inputs['To Min'].default_value=1;edge.inputs['To Max'].default_value=0
    links.new(distance.outputs['Value'],edge.inputs['Value'])
    grain=nodes.new('ShaderNodeMath');grain.operation='MULTIPLY'
    links.new(edge.outputs['Result'],grain.inputs[0]);links.new(noise.outputs['Fac'],grain.inputs[1])
    strength=nodes.new('ShaderNodeMath');strength.operation='MULTIPLY'
    links.new(grain.outputs[0],strength.inputs[0]);links.new(strength.outputs[0],vol.inputs['Density'])
    links.new(vol.outputs['Volume'],out.inputs['Volume']);obj.data.materials.append(mat)
    for age in [-.01,0,.15,.4,.7,1,1.01]:
        frame=(birth+max(age,0)*life)*25 if age>=0 else birth*25-1
        a=max(0,min(1,age));size=radius*(.3+1.8*a)
        obj.location=positions(a)
        obj.scale=(size,size*(1.5 if exhale else 1),size)
        strength.inputs[1].default_value=density*math.sin(math.pi*a)**1.2
        for prop in ['location','scale']:obj.keyframe_insert(data_path=prop,frame=frame)
        strength.inputs[1].keyframe_insert(data_path='default_value',frame=frame)
    for datablock in [obj,mat.node_tree]:
        for fc in datablock.animation_data.action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
    return obj

groups={}
for kind,tip in [('chillum',1.79),('joint',1.23)]:
    rig.animation_data.action=bpy.data.actions['420_smoke_'+kind]
    groups[kind]=[]
    for i in range(-10,44):
        birth=i*.28;scene.frame_set(round((birth%12)*25));bpy.context.view_layer.update()
        origin=(rig.matrix_world@rig.pose.bones['Bip01 Prop2'].matrix)@Vector((0,0,tip))
        def position(a,origin=origin.copy(),i=i):
            return origin+Vector((.13*math.sin(a*6+i)*a,-.18*a,1.35*a))
        groups[kind].append(puff(kind+'_tip_'+str(i),position,birth,2.5,.16,.65))
    # Emission occurs only in [8,11); existing smoke dissipates afterward.
    for i in range(25):
        birth=8+i*.12;scene.frame_set(round(birth*25));bpy.context.view_layer.update()
        origin=rig.matrix_world@Vector((-.045,-2.96,13.25))
        def position(a,origin=origin.copy(),i=i):
            return origin+Vector((.13*math.sin(i+a*4)*a,-3.6*a,.55*a+.5*a*a))
        groups[kind].append(puff(kind+'_mouth_'+str(i),position,birth,1.8,.34,1.4,True))

scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=800;scene.render.resolution_y=800
scene.frame_start=0;scene.frame_end=300
for kind in groups:
    rig.animation_data.action=bpy.data.actions['420_smoke_'+kind]
    for other,objects in groups.items():
        bpy.data.objects['preview_'+other].hide_render=other!=kind
        for obj in objects:obj.hide_render=other!=kind;obj.hide_set(other!=kind)
    for label,frame in [('hold',150),('exhale',215)]:
        scene.frame_set(frame)
        scene.render.filepath=str(ROOT/'qa'/f'{kind}_smoke_{label}.png')
        bpy.ops.render.render(write_still=True)
scene.frame_set(215)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets'/'smoking_smoke_preview.blend'))
(ROOT/'qa'/'smoke_preview_checks.json').write_text(json.dumps({
    'scope':'Blender preview only; no Kenshi smoke export',
    'inhale_seconds':[2,4],'lower_seconds':[4,5],'hold_seconds':[5,8],'mouth_emission_seconds':[8,11],
    'tip_smoke':'continuous, both props; low density',
    'mouth_particle_tail_seconds':1.8,'in_game_verified':False
},indent=2),encoding='utf-8')
