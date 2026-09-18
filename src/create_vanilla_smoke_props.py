"""Build clean vanilla display props; rejected static wisps are opt-in only.

Run with smoking_animation_work.blend. The inventory meshes remain unchanged.
Kenshi's stock ItemShader.ALPHA clips normal-map alpha: keep a connected
core so texture filtering does not average sparse dots below the cutoff.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector

ROOT=Path(r'E:\AI_Playground\420');OUT=ROOT/'build/420_Smoking/assets'
# Rejected in game: static wisps look like paper attached to the prop.
# Keep the experiment reproducible, but ship clean display props by default.
experimental_wisp='--experimental-static-wisp' in sys.argv
scene=bpy.data.scenes['420_Animation_Lab'];bpy.context.window.scene=scene
rig=bpy.data.objects['male_skeleton']
for track in rig.animation_data.nla_tracks:track.mute=True
source=bpy.data.images.load(str(OUT/'420_surfaces.png'),check_existing=False)
base=list(source.pixels);width=1024;height=512
diffuse=[];normal=[]
for y in range(height):
    for x in range(width):
        if x<512:
            i=(y*512+x)*4;diffuse.extend(base[i:i+3]+[0.0]);normal.extend([.5,.5,1,1])
        else:
            u=(x-512+.5)/512;v=(y+.5)/512
            center=.5+.13*math.sin(v*12)+.035*math.sin(v*31)
            spread=(.13+.055*math.sin(v*19)**2)*math.sin(math.pi*v)**.55
            # A continuous, tapered core survives bilinear filtering and mipmaps.
            alpha=1.0 if abs(u-center)<spread else 0.0
            diffuse.extend([.66,.68,.70,0]);normal.extend([.5,.5,1,alpha])
for name,data in [('420_smoke_prop_diffuse',diffuse),('420_smoke_prop_normal',normal)]:
    image=bpy.data.images.new(name,width,height,alpha=True)
    if name.endswith('normal'):image.colorspace_settings.name='Non-Color'
    image.pixels.foreach_set(data);image.filepath_raw=str(OUT/(name+'.png'));image.file_format='PNG';image.save()

report={}
for kind,tip in [('chillum',1.79),('joint',1.23)]:
    rig.animation_data.action=bpy.data.actions['420_smoke_'+kind]
    rig.animation_data.action_slot=rig.animation_data.action.slots[0]
    scene.frame_set(80);bpy.context.view_layer.update()
    up=rig.pose.bones['Bip01 Prop2'].matrix.to_3x3().inverted()@Vector((0,0,1))
    up.normalize();side=up.cross(Vector((1,0,0))).normalized();across=up.cross(side).normalized()
    original=bpy.data.objects['420_'+kind]
    obj=original.copy();obj.data=original.data.copy();obj.name='420_'+kind+'_lit';scene.collection.objects.link(obj)
    obj.location=(0,0,0);obj.rotation_euler=(0,0,0);obj.scale=(1,1,1)
    for uv in obj.data.uv_layers.active.data:uv.uv.x*=.5
    vertices=[];faces=[];coords=[]
    # Keep the rigid wisp close to the ember: long ribbons visibly rotate
    # with the hand, especially during the reclined animation.
    length=.60 if kind=='chillum' else .45
    half_width=.12 if kind=='chillum' else .10
    for cross,facing in ([(side,1),(side,-1),(across,1),(across,-1)] if experimental_wisp else []):
        start=len(vertices)
        for j in range(17):
            t=j/16;center=Vector((0,0,tip))+up*(length*t)+side*(.018*math.sin(t*8)*t)
            for sign,u in [(-1,.501),(1,.999)]:
                # Separate front/back surfaces to avoid coplanar z-fighting.
                vertices.append(center+cross*(sign*half_width*(1+.6*t))+cross.cross(up).normalized()*(.01*facing))
                coords.append((u,.002+.996*t))
        for j in range(16):
            a=start+j*2
            faces.append((a,a+1,a+3,a+2) if facing==1 else (a+2,a+3,a+1,a))
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    if experimental_wisp:
        mesh=bpy.data.meshes.new('tip_wisp');mesh.from_pydata(vertices,[],faces);mesh.update()
        uv=mesh.uv_layers.new()
        for polygon in mesh.polygons:
            for li in polygon.loop_indices:uv.data[li].uv=coords[mesh.loops[li].vertex_index]
        wisp=bpy.data.objects.new('tip_wisp',mesh);scene.collection.objects.link(wisp)
        wisp.data.materials.append(obj.data.materials[0]);wisp.select_set(True)
        bpy.ops.object.join()
    getattr(bpy.ops,'export').kenshi_ogre_objects(filepath=str(OUT/(obj.name+'.mesh')),export_skeleton=False,tangent_format='TANGENT_4')
    report[kind]={'mesh':obj.name+'.mesh','tip_local_z':tip,'added_faces':len(faces),'wisp_length':length if experimental_wisp else 0,'max_half_width':half_width*1.6 if experimental_wisp else 0,'mode':'experimental static wisp' if experimental_wisp else 'clean prop; rejected static smoke disabled'}
(ROOT/'qa/vanilla_smoke_asset_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report)
