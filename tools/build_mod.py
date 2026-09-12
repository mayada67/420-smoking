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
    if n==51:r['fields']['filename'].update({'texture map 2':asset('420_surfaces.png'),'normal map 2':asset('420_normal.png'),'metalness map':asset('420_metalness.png'),'metalness map 2':asset('420_metalness.png')})
    r['fields']['float']['specular mult']=.15
for n,mesh in [(1,'420_paper'),(2,'420_joint')]:
    r=records[sid(n)];r['fields']['filename'].update({'mesh':asset(mesh+'.mesh'),'ground mesh':'','physics file':'','icon':icon(mesh+'_icon.png')});r['extra']['material']={sid(50):[0,0,0]}
    r['fields']['bool']['auto icon']=False
chillum=clone('46981-Newwworld.mod',3,'420 Chillum prop')
chillum['fields']['filename'].update({'mesh':asset('420_chillum.mesh'),'icon':icon('420_chillum_icon.png')});chillum['extra']['material']={sid(50):[0,0,0]}
chillum['fields']['bool']['auto icon']=False
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
for fn,building,anim,tool in [(13,23,40,3),(14,24,41,2)]:
    records[sid(fn)]['extra']['animation']={sid(anim):[0,0,0]}
    records[sid(fn)]['extra']['special tool']={sid(tool):[0,0,0]}
    records[sid(building)]['extra']['parts']={sid(52):[0,100,0]}
    records[sid(building)]['fields']['string']['Description']='ALPHA: smoking consumption is not yet verified. Supply hashish for the chillum seat, or crafted joints for the joint seat. Assign one operator. No stat effects.'
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
