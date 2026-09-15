"""Create worn beanbag furniture with mesh-native seams and patched cloth."""
import bpy, math, random
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/420_Smoking/assets'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
random.seed(42026)
# Cloth atlas: faded olive sackcloth, dirty ochre repair cloth, dark thread.
im=bpy.data.images.new('Beanbag cloth',512,512,alpha=True)
pixels=[]
for y in range(512):
    for x in range(512):
        base=(.25,.235,.16) if x<256 else (.37,.28,.17)
        stain=max(0,math.sin(x*.033+math.sin(y*.027)*2)*math.cos(y*.039))
        grain=random.uniform(-.035,.035)+(.014 if (x+y)%3==0 else -.008)
        pixels.extend([max(.025,c*(1-.63*stain)+grain) for c in base]+[1])
im.pixels.foreach_set(pixels);im.filepath_raw=str(OUT/'420_beanbag_cloth.png');im.file_format='PNG';im.save()
mat=bpy.data.materials.new('Worn sackcloth');mat.use_nodes=True
nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.96
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
parts=[]
def sack(name,loc,scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=loc)
    o=bpy.context.object;o.name=name
    for v in o.data.vertices:
        p=v.co;ang=math.atan2(p.y,p.x)
        wobble=1+.045*math.sin(ang*7+p.z*5)+.025*math.cos(ang*13-p.z*8)
        p.x*=wobble;p.y*=wobble
    o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    o.data.materials.append(mat);parts.append(o);return o
def cord(name,points,r=.035):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=1
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,cu);scene.collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    o=bpy.context.object;o.data.materials.append(mat);parts.append(o)
# Wide collapsed base, raised back and side bolsters; seating surface matches
# the existing smoking pose so mouth/hand particle alignment stays intact.
sack('Slumped beanbag base',(0,1.0,1.35),(4.5,3.2,1.85))
sack('Compressed seat',(0,.65,2.45),(3.25,2.6,1.0))
back=sack('Soft leaning back',(0,3.65,4.7),(3.7,1.0,4.0))
back.rotation_euler.x=math.radians(-28)
for x in [-3.65,3.65]:sack('Sagging side bolster',(x,1.25,2.6),(.95,2.5,1.3))
# Merge overlapping cushions into one continuous stuffed fabric shell.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();shell=bpy.context.object
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
rem=shell.modifiers.new('Continuous beanbag shell','REMESH');rem.mode='VOXEL';rem.voxel_size=.16
bpy.ops.object.modifier_apply(modifier=rem.name)
sm=shell.modifiers.new('Soft cloth transitions','SMOOTH');sm.factor=1.1;sm.iterations=5;bpy.ops.object.modifier_apply(modifier=sm.name)
# A broad flattened contact patch, rather than a sphere balanced on one point.
for v in shell.data.vertices:
    p=shell.matrix_world@v.co
    if p.z<.18:
        p.z=0
        v.co=shell.matrix_world.inverted()@p
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
for poly in shell.data.polygons:
    for li in poly.loop_indices:
        p=shell.matrix_world @ shell.data.vertices[shell.data.loops[li].vertex_index].co
        shell.data.uv_layers.active.data[li].uv=(.015+.46*(math.atan2(p.y,p.x)/math.tau+.5),p.z/11)
for p in shell.data.polygons:p.use_smooth=True
parts=[shell]
for z,rx,ry in [(1.0,4.2,3.0)]:
    cord('Hand sewn perimeter',[(rx*math.cos(t*math.tau/100),1+ry*math.sin(t*math.tau/100),z+.07*math.sin(t*.7)) for t in range(101)])
# Flat repair patch follows the front slope, with visible irregular stitches.
verts=[(-2.7,-1.65,.65),(-.6,-2.18,.65),(-.6,-2.2,1.6),(-2.7,-1.68,1.6)]
me=bpy.data.meshes.new('Patch');me.from_pydata(verts,[],[(0,1,2,3)]);me.update()
o=bpy.data.objects.new('Large mismatched repair patch',me);scene.collection.objects.link(o);me.materials.append(mat)
uv=me.uv_layers.new()
for d,p in zip(uv.data,[(.55,.12),(.96,.12),(.96,.75),(.55,.75)]):d.uv=p
parts.append(o)
for a,b in zip(verts,verts[1:]+verts[:1]):
    for i in range(10):
        p=Vector(a).lerp(Vector(b),(i+.25)/10);q=p+Vector((.11,-.045,.10))
        cord('Repair stitch',[p+Vector((0,-.055,0)),q],.025)
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='420_beanbag'
scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
getattr(bpy.ops,'export').kenshi_ogre_objects(filepath=str(OUT/'420_beanbag.mesh'),export_skeleton=False,tangent_format='TANGENT_4')
# Small floor collision keeps the operator's path to the seating anchor open.
tree=ET.parse(OUT/'420_smoking_seat.xml')
collection=tree.getroot().find('NxuPhysicsCollection');collection.set('id','420_beanbag.xml')
desc=collection.find('NxSceneDesc')
for actor in list(desc):
    if actor.get('name')!='420_COL_base':desc.remove(actor)
actor=desc.find('NxActorDesc');actor.set('name','420_COL_beanbag')
actor.find('NxBoxShapeDesc').set('dimensions','3.8 2.5 1.35')
pose=actor.find('.//localPose');pose.text='1 0 0 0 1 0 0 0 1 0 1.0 1.35'
tree.write(OUT/'420_beanbag.xml',encoding='UTF-8',xml_declaration=True)
world=bpy.data.worlds.new('Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.13,.15,1);scene.world=world
for loc,power in [((0,-12,18),2600),((-10,4,14),2100)]:
    bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=10;l.rotation_euler=(Vector((0,0,4))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(15,-23,15));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,4.5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=15;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1000;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'qa/beanbag_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/beanbag.blend'));bpy.ops.render.render(write_still=True)
