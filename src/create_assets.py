import bpy, math, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'E:\AI_Playground\420')
OUT=ROOT/'build'/'420_Smoking'/'assets'
OUT.mkdir(parents=True,exist_ok=True)
random.seed(420)
scene=bpy.data.scenes.get('420_Assets') or bpy.data.scenes.new('420_Assets')
bpy.context.window.scene=scene
for ob in list(scene.objects): bpy.data.objects.remove(ob,do_unlink=True)
palette=[(.32,.15,.075),(.055,.038,.025),(.40,.36,.26),(.12,.13,.12),(.27,.17,.075),(.74,.68,.49),(.16,.12,.075),(.38,.18,.06)]
im=bpy.data.images.new('420_surface_atlas',512,512,alpha=True)
pixels=[]
for y in range(512):
    for x in range(512):
        idx=(x//128)+(y//256)*4
        col=palette[idx]
        n=random.uniform(-.055,.055)+.025*math.sin(x*.8+y*.025)
        if idx==4: n+=.05*math.sin(x*.42+math.sin(y*.03)*2)
        pixels.extend([max(0,min(1,c+n)) for c in col]+[1])
im.pixels.foreach_set(pixels);im.filepath_raw=str(OUT/'420_surfaces.png');im.file_format='PNG';im.save()
mat=bpy.data.materials.new('420_surfaces');mat.use_nodes=True
node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im
bs=mat.node_tree.nodes.get('Principled BSDF');mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.87
parts=[]
def tag(o,idx):
    o['surface']=idx;parts.append(o);return o
def box(name,loc,scale,idx,bevel=.03):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=o.modifiers.new('Worn edges','BEVEL');m.width=bevel;m.segments=2
        bpy.ops.object.modifier_apply(modifier=m.name)
    return tag(o,idx)
def rod(name,a,b,r,idx,vertices=12):
    a,b=Vector(a),Vector(b);delta=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=delta.length,location=(a+b)/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return tag(o,idx)
def lathe(name,rings,idx,sides=24):
    vs=[(r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),z) for z,r in rings for i in range(sides)]
    fs=[(j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i) for j in range(len(rings)-1) for i in range(sides)]
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);scene.collection.objects.link(o);return tag(o,idx)
def finish(name):
    global parts
    for o in parts:
        for old_uv in list(o.data.uv_layers): o.data.uv_layers.remove(old_uv)
        uv=o.data.uv_layers.new(name='UVMap')
        idx=int(o['surface']);cx=idx%4;cy=idx//4
        for p in o.data.polygons:
            for j,li in enumerate(p.loop_indices):
                co=o.data.vertices[o.data.loops[li].vertex_index].co
                u=(co.x*.17+co.z*.11)%1;v=(co.y*.19+co.z*.21)%1
                uv.data[li].uv=((cx+.08+.84*u)/4,(cy+.08+.84*v)/2)
        o.data.materials.clear();o.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    getattr(bpy.ops,'export').kenshi_ogre_objects(filepath=str(OUT/(name+'.mesh')),export_skeleton=False,tangent_format='TANGENT_4')
    parts=[];return o
# Straight hollow terracotta chillum: broad bowl, narrow lower mouthpiece.
lathe('Clay body',[(0,.105),(.16,.12),(.5,.16),(1.4,.28),(1.72,.34),(1.79,.35),(1.79,.285),(1.65,.27),(.65,.095),(.08,.045),(0,.045),(0,.105)],0)
lathe('Blackened bowl',[(1.52,.252),(1.72,.28),(1.79,.285)],1)
for z in [.42,.49,.56]:lathe('Clay incised collar',[(z,.173),(z+.025,.177),(z+.05,.173)],6)
for i in range(7):
    z=.04+i*.037;lathe('Cloth mouth wrap',[(z,.125),(z+.033,.128)],2)
for z in [.94,1.02]:lathe('Repair wire',[(z,.241),(z+.025,.242)],3)
chillum=finish('420_chillum')
lathe('Joint paper',[(0,.047),(.14,.056),(.82,.081),(1.13,.071),(1.16,.06)],5,16)
lathe('Joint ash',[(1.13,.071),(1.21,.064),(1.23,.032),(1.23,0)],6,16)
lathe('Paper mouth edge',[(0,.047),(.02,.05),(.02,.032),(0,.03),(0,.047)],2,16)
joint=finish('420_joint')
for i in range(5):box('Hemp paper sheet',(i*.012,0,i*.018),(1.2,1.65,.015),5,.009)
paper=finish('420_paper')
# Salvaged stool with low back and side tray; game units match imported human rig.
for x in [-1.8,1.8]:
    for y in [-1.45,1.45]:rod('Iron leg',(x*1.15,y*1.13,.15),(x,y,5.8),.15,3)
for y in [-1.45,1.45]:rod('Cross brace',(-2,y,2.0),(2,y,2.0),.11,7)
for x in [-1.8,1.8]:rod('Side brace',(x,-1.45,2),(x,1.45,2),.11,7)
for y in [-1.25,-.42,.42,1.25]:box('Seat plank',(0,y,5.92),(4.3,.78,.26),4,.06)
for x in [-1.75,1.75]:rod('Back post',(x,1.5,5.5),(x,1.8,10.3),.12,3)
for z in [8.0,9.25]:box('Backrest slat',(0,1.76,z),(4.15,.24,.72),4,.06)
for x in [-1.73,1.73]:
    for y in [-1.25,1.25]:rod('Seat rivet',(x,y,6.04),(x,y,6.11),.095,3)
rod('Tray support',(1.8,.4,3.6),(4,.4,6.4),.13,3)
box('Side tray',(4,.4,6.5),(2.5,2.4,.13),3,.035)
for x in [2.8,5.2]:box('Tray lip',(x,.4,6.67),(.09,2.4,.23),7)
for y in [-.75,1.55]:box('Tray lip',(4,y,6.67),(2.5,.09,.23),7)
seat=finish('420_smoking_seat')
# Preview staging only; meshes were exported at origin before this translation.
chillum.location=(-4,-3,7);joint.location=(-3,-3,7);paper.location=(-1,-3,7)
for o in [chillum,joint]:o.rotation_euler[1]=.25
world=bpy.data.worlds.new('420 studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.065,.075,1);world.node_tree.nodes['Background'].inputs[1].default_value=.5;scene.world=world
def area(loc,power,size):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
area((2,-10,18),2000,10);area((-9,4,12),1600,8)
bpy.ops.object.camera_add(location=(18,-26,18));cam=bpy.context.object;cam.rotation_euler=(Vector((.6,0,5))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=18;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1100;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.filepath=str(ROOT/'qa'/'assets_preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets'/'smoking_assets.blend'))
bpy.ops.render.render(write_still=True)
print('Asset meshes and preview exported:',OUT)
