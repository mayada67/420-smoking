"""Assemble the visual alpha. This is NOT a release until in-game QA passes."""
import copy,json,runpy,sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
prototype=runpy.run_path(str(Path(__file__).parent/'build_prototype.py'))
BASE=prototype['BASE'];OUT=Path('build/420_Smoking');OUT.mkdir(exist_ok=True)
def remap(v):
    if isinstance(v,str):return v.replace('420_Smoking_Prototype.mod','420_Smoking.mod').replace('[PROTOTYPE]','[ALPHA]')
    if isinstance(v,dict):return {remap(k):remap(x) for k,x in v.items()}
    if isinstance(v,list):return [remap(x) for x in v]
    return v
records=remap(prototype['records'])
def sid(n):return f'{n}-420_Smoking.mod'
def clone(source,n,name):
    r=copy.deepcopy(BASE[source]);r.update(name=name,id=0,instance_count=0,datatype_id=-2147483646,datatype='NEW');records[sid(n)]=r;return r
def asset(name):return '.\\mods\\420_Smoking\\assets\\'+name
def icon(name):
    # Custom inventory textures must be packaged under lowercase items.
    target=OUT/'items'/'icons'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(OUT/'assets'/name,target)
    return '.\\mods\\420_Smoking\\items\\icons\\'+name
for n,source in [(50,'5263-lanterns_otto.mod'),(51,'3403-otto.mod')]:
    r=clone(source,n,'420 Surface material '+str(n))
    for k in r['fields']['filename']:r['fields']['filename'][k]=''
    r['fields']['filename'].update({'texture map':asset('420_surfaces.png'),'normal map':asset('420_normal.png')})
    if n==51:
        # Single-texture meshes have no COLOR0 stream required by DUAL.
        r['fields']['int']['material type']=0 # BuildingShader.DEFAULT
        r['fields']['filename']['metalness map']=asset('420_metalness.png')
    r['fields']['float']['specular mult']=.15
for n,mesh in [(1,'420_paper'),(2,'420_joint')]:
    r=records[sid(n)];r['fields']['filename'].update({'mesh':asset(mesh+'.mesh'),'ground mesh':'','physics file':'','icon':icon(mesh+'_icon.png')});r['extra']['material']={sid(50):[0,0,0]}
    r['fields']['bool']['auto icon']=False
chillum=clone('46981-Newwworld.mod',3,'420 Chillum prop')
chillum['fields']['filename'].update({'mesh':asset('420_chillum.mesh'),'icon':icon('420_chillum_icon.png')});chillum['extra']['material']={sid(50):[0,0,0]}
chillum['fields']['bool']['auto icon']=False
# Display-only lit props: keep crafted inventory/ground items smoke-free.
smoke_material=clone('5263-lanterns_otto.mod',53,'420 Static tip wisp alpha material')
smoke_material['fields']['filename'].update({'texture map':asset('420_smoke_prop_diffuse.png'),'normal map':asset('420_smoke_prop_normal.png')})
smoke_material['fields']['int']['material type']=1 # ItemShader.ALPHA
smoke_material['fields']['float']['specular mult']=0.0
for n,source,kind in [(54,3,'chillum'),(55,2,'joint')]:
    r=copy.deepcopy(records[sid(source)])
    r.update(name='420 '+kind+' lit display prop [STATIC WISP]')
    r['fields']['filename']['mesh']=asset('420_'+kind+'_lit.mesh')
    r['extra']['material']={sid(53):[0,0,0]}
    records[sid(n)]=r
for n,kind in [(40,'chillum'),(41,'joint')]:
    r=clone('14533-gamedata.base',n,'420_smoke_'+kind)
    r['fields']['string']['anim name']='420_smoke_'+kind
    r['fields']['float']['play speed']=1.0
    r['fields']['bool'].update({'delete weapons':False,'uses right arm':True,'uses left arm':kind=='chillum','unarmed':True,'is action':True,'loop':True})
    r['fields']['int']['has weapon R']=0
animfile=clone('1533847-gamedata.base',42,'420 Smoking animations [ALPHA male only]')
animfile['fields']['filename']={'male animation':asset('420_smoking_male.skeleton'),'female animation':''}
animfile['fields']['bool']['preprocess']=True
# Additive race reference only: no stats or existing animation entries replaced.
human=copy.deepcopy(BASE['17-gamedata.quack'])
human.update(instance_count=0,id=0,datatype_id=-2147483647,datatype='CHANGED')
human['fields']={k:{} for k in human['fields']};human['extra']={'animation files':{sid(42):[0,0,0]}};human['instances']={}
records['17-gamedata.quack']=human
part=clone('3447-D-otto.mod',52,'420 Smoking seat mesh')
part['fields']['bool']['passable']=True
part['fields']['filename'].update({'phs or mesh':asset('420_smoking_seat.mesh'),'xml collision':asset('420_smoking_seat.xml')});part['extra']['material']={sid(51):[0,0,0]}
for fn,building,anim,tool in [(13,23,40,54),(14,24,41,55)]:
    records[sid(fn)]['extra']['animation']={sid(anim):[0,0,0]}
    records[sid(fn)]['extra']['special tool']={sid(tool):[0,0,0]}
    records[sid(building)]['extra']['parts']={sid(52):[0,100,0]}
    item='hashish' if building==23 else 'joint'
    records[sid(building)]['fields']['string']['Description']=f'Smoking gimmick. Place one {item} in the seat, then assign one operator. Intended for continuous smoking without refills. No stat effects.'
# Additional beanbag seats share the proven one-item smoking functionality.
cloth=copy.deepcopy(records[sid(51)]);records[sid(57)]=cloth
cloth['name']='420 Worn beanbag cloth'
cloth['fields']['filename']['texture map']=asset('420_beanbag_cloth.png')
beanpart=copy.deepcopy(records[sid(52)]);records[sid(56)]=beanpart
beanpart['name']='420 Patched beanbag mesh'
beanpart['fields']['filename'].update({'phs or mesh':asset('420_beanbag.mesh'),'xml collision':asset('420_beanbag.xml')})
beanpart['extra']['material']={sid(57):[0,0,0]}
for n,source,label in [(27,23,'Hashish'),(28,24,'Joint')]:
    seat=copy.deepcopy(records[sid(source)]);records[sid(n)]=seat
    seat['name']='420 Worn Beanbag: '+label
    seat['extra']['parts']={sid(56):[0,100,0]}
    # In-game retest: -90 yaw faced backward. Use +90 instead (180 correction).
    # Kenshi stores quaternions as w,x,y,z, with vertical Y.
    seat['instances']['420_operator']['rotation']=[2**-.5,0,2**-.5,0]
    # Fit the cushion to the grounded pose instead of lifting the feet.
    seat['instances']['420_operator']['position']=[0,0,0]
    records[sid(30)]['extra']['enable buildings'][sid(n)]=[0,0,0]
for fn,anim,source_fn,source_anim,building,kind in [(58,60,13,40,27,'chillum'),(59,61,14,41,28,'joint')]:
    records[sid(anim)]=copy.deepcopy(records[sid(source_anim)])
    records[sid(anim)]['name']='420_recline_'+kind
    records[sid(anim)]['fields']['string']['anim name']='420_recline_'+kind
    records[sid(fn)]=copy.deepcopy(records[sid(source_fn)])
    records[sid(fn)]['name']='420 Reclined '+kind
    records[sid(fn)]['extra']['animation']={sid(anim):[0,0,0]}
    records[sid(building)]['extra']['functionality']={sid(fn):[0,0,0]}
records[sid(62)]=copy.deepcopy(records[sid(42)])
records[sid(62)]['name']='420 Beanbag reclined animations'
records[sid(62)]['fields']['filename']['male animation']=asset('420_reclined_male.skeleton')
records['17-gamedata.quack']['extra']['animation files'][sid(62)]=[0,0,0]
path=OUT/'420_Smoking.mod'
w=kenshi.ModFileWriter(path,1,'420 project','UNFINISHED ALPHA. Male human animation trial. In-game consumption, attachment, interruption and save/load NOT VERIFIED.','gamedata.base,Newwworld.mod,Dialogue.mod,rebirth.mod','');w.records(records);w.handle.close()
r=kenshi.ModFileReader(path);assert len(r.records)==len(records);r.handle.close()
missing=[]
for k,v in records.items():
    for cat,refs in v['extra'].items():
        for ref in refs:
            if ref not in records and ref not in BASE:missing.append((k,cat,ref))
assert not missing,missing
assert '1965-gamedata.base' not in records and '1230-gamedata.base' not in records
(OUT/'records.json').write_text(json.dumps(records,indent=2,ensure_ascii=False),encoding='utf-8')
report={'record_count':len(records),'binary_readback':True,'references_resolve':True,'hemp_and_hashish_unmodified':True,'release_ready':False,'in_game_qa':'pending','female_and_other_races':'pending','consumption_without_output':'experimental'}
Path('qa/mod_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
