import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
for name in ['420_smoking_seat','420_beanbag']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    getattr(bpy.ops,'import').kenshi_ogre_objects(filepath=str(root/'build/420_Smoking/assets'/f'{name}.mesh'))
    pts=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
    high=[p for p in pts if p.z>8]
    print('AXIS',name,'bounds',[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)],'back',list(sum(high,Vector())/len(high)))
