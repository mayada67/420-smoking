"""Blender background QA for vanilla smoke display props and FCS wiring."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(r'E:\AI_Playground\420');OUT=ROOT/'build/420_Smoking'
sys.path.insert(0,str(ROOT/'tools/vendor'));import kenshi
reader=kenshi.ModFileReader(OUT/'420_Smoking.mod');records=reader.records;reader.handle.close()
sid=lambda n:str(n)+'-420_Smoking.mod'
assert records[sid(53)]['fields']['int']['material type']==1
assert records[sid(2)]['fields']['filename']['mesh'].endswith('420_joint.mesh')
assert records[sid(3)]['fields']['filename']['mesh'].endswith('420_chillum.mesh')
report={'binary_readback':True,'inventory_meshes_unchanged':True,'mode':'clean display props; no vanilla smoke','in_game_visual_verified':False}
for fn,prop,kind in [(13,54,'chillum'),(14,55,'joint'),(58,54,'chillum'),(59,55,'joint')]:
    refs=records[sid(fn)]['extra']['special tool']
    assert set(refs)=={sid(prop)} and list(refs[sid(prop)])==[0,0,0],refs
    assert sid(53) in records[sid(prop)]['extra']['material']
    before=set(bpy.data.objects)
    getattr(bpy.ops,'import').kenshi_ogre_objects(filepath=str(OUT/'assets'/('420_'+kind+'_lit.mesh')))
    meshes=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
    assert meshes
    coords=[uv.uv.x for o in meshes for uv in o.data.uv_layers.active.data]
    assert min(coords)<.5 and max(coords)<=.5001, 'Rejected smoke geometry still present'
    report[kind]={'display_prop_reference':prop,'mesh_readback':True,'only_body_uv_present':True}
im=bpy.data.images.load(str(OUT/'assets/420_smoke_prop_normal.png'))
assert tuple(im.size)==(1024,512)
pixels=list(im.pixels)
body_alpha=[pixels[(y*1024+x)*4+3] for y in range(512) for x in range(512)]
assert min(body_alpha)==1.0
report['body_opaque']=True
(ROOT/'qa/vanilla_smoke_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(report)
