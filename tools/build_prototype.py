"""Build an explicitly experimental, vanilla-only FCS consumption prototype."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import kenshi
BASE = json.loads(Path('build/base_records.json').read_text(encoding='utf-8'))
OUT = Path('build/420_Smoking_Prototype')
OUT.mkdir(parents=True, exist_ok=True)
records = {}
def clone(source, ident, name):
    r = copy.deepcopy(BASE[source])
    r.update(name=name, id=0, instance_count=0, datatype_id=-2147483646, datatype='NEW')
    records[ident] = r
    return r
def sid(n): return f'{n}-420_Smoking_Prototype.mod'
hemp, hashish = '1965-gamedata.base', '1230-gamedata.base'
paper = clone('584-gamedata.base', sid(1), '420 Hemp Paper [PROTOTYPE]')
paper['fields']['string']['description'] = 'Paper made from hemp. Used with hemp to craft joints.'
paper['fields']['int'].update({'inventory footprint width':2,'inventory footprint height':2,'stackable':20,'production time':1})
paper['fields']['float']['weight kg'] = 0.05
paper['extra']['ingredients'] = {hemp:[100,0,0]}
joint = clone('1230-gamedata.base',sid(2),'420 Joint [PROTOTYPE]')
joint['fields']['string']['description'] = 'Made from hemp and paper. Supply to the joint smoking seat. No stat effects.'
joint['fields']['int'].update({'inventory footprint width':2,'inventory footprint height':2,'stackable':20,'production time':1})
joint['fields']['float']['weight kg'] = 0.05
joint['extra']['ingredients'] = {hemp:[100,0,0],sid(1):[100,0,0]}

def functionality(n,name,inputs,output=None,sitting=False):
    r=clone('2018-gamedata.base',sid(n),name)
    r['fields']['int'].update({'stat used':0,'max operators':1})
    r['fields']['float'].update({'production mult':48.0,'hunger rate':1.0,'use range':20.0})
    if sitting:r['fields']['float']['use range']=0.5
    r['fields']['bool'].update({'has progress bar when used':True,'overrides ingredients':True})
    r['extra']={'consumes':{k:[20,v,0] for k,v in inputs.items()},'animation':{'14533-gamedata.base' if sitting else '43871-rebirth.mod':[0,0,0]}}
    if sitting:
        # Keep the observed ingredient gate and no-output operation; cap the
        # dedicated input slot at one item instead of a supply stack.
        r['extra']['consumes']={k:[1,v,0] for k,v in inputs.items()}
        r['fields']['bool']['has progress bar when used']=False
    if output: r['extra']['produces']={output:[20,0,0]}
    return r
# Use vanilla recipe-queue crafting, not fixed-output production. Each item
# supplies its own ingredients, so paper never requires paper as an input.
for n in [11,12]:
    craft=clone('43954-rebirth.mod',sid(n),'420 Paper and Joint crafting')
    craft['fields']['int']['max operators']=1
    # Bandana base work: 1.3 * 0.4 head coverage * 0.6 head-slot factor
    # = 0.312 game hours at 1x crafting speed. ITEM time is integer hours,
    # so keep each recipe at 1 hour and express the fraction on the bench.
    craft['fields']['float']['production mult']=1.0/0.312
    craft['fields']['bool']['overrides ingredients']=False
    craft['extra']={'animation':{'43871-rebirth.mod':[0,0,0]},
                    'item crafts':{sid(1):[20,0,0],sid(2):[20,0,0]}}
functionality(13,'420 Hashish smoking gimmick - single item',{hashish:100},sitting=True)
functionality(14,'420 Joint smoking gimmick - single item',{sid(2):100},sitting=True)
for n,func,name,sitting in [(21,11,'Smoking Workbench',False),(22,11,'Smoking Workbench (Legacy)',False),(23,13,'Chillum Seat',True),(24,14,'Joint Seat',True)]:
    r=clone('3468-otto.mod' if sitting else '42166-gamedata.base',sid(n),'420 '+name+' [PROTOTYPE]')
    r['fields']['string'].update({'building category':'420 SMOKING TEST','Description':'Experimental prototype. Supply the required ingredients and assign one operator. No stat effects. Consumption behavior is not yet verified.'})
    r['fields']['int'].update({'power output':0,'max operators':1})
    # Production benches and smoking seats are indoor furniture by default.
    # Outdoor support must be decided and verified separately for each facility.
    r['fields']['bool'].update({'is exterior furniture':False,'is interior furniture':True})
    r['extra']['functionality']={sid(func):[0,0,0]}
    r['extra'].pop('sounds',None)
    r['extra']['construction']={'42159-gamedata.base':[1,0,0]}
    if not sitting:
        r['fields']['string']['Description']='Craft hemp paper and joints at this workbench. Queue paper first (1 hemp), then joints (1 hemp + 1 paper).'
    if sitting:
        r['extra']['parts']={'3447-D-otto.mod':[0,100,0]}
        r['instances']={'420_operator':{'target':'1183-gamedata.base','position':[0,0,0],'rotation':[1,0,0,0],'states':[]}}
storage=clone('55236-rebirth.mod',sid(25),'420 Storage: Paper')
storage['fields']['string']['Description']='Dedicated storage for hemp paper used to craft joints.'
storage['extra']['limit inventory']={sid(1):[0,0,0]}
joint_storage=clone('55236-rebirth.mod',sid(26),'420 Storage: Joints')
joint_storage['fields']['string']['Description']='Dedicated storage for crafted joints used at the joint smoking seat.'
joint_storage['extra']['limit inventory']={sid(2):[0,0,0]}
tech=clone('2263-gamedata.base',sid(30),'420 Smoking Prototype')
tech['fields']['int'].update({'level':3,'time':0})
tech['fields']['string']['description']='Prototype test facilities; not a completed mod.'
tech['extra']={'enable buildings':{sid(i):[0,0,0] for i in [21,23,24,25,26]},'enable item':{sid(i):[0,0,0] for i in [1,2]}}
tech['extra']['cost']={'16855-nodes_otto1.mod':[3,0,0],'1965-gamedata.base':[3,0,0]} # 3 ordinary Books + 3 hemp.
path=OUT/'420_Smoking_Prototype.mod'
writer=kenshi.ModFileWriter(path,1,'420 project','EXPERIMENTAL consumption prototype. Not release-ready.','gamedata.base,Newwworld.mod,Dialogue.mod,rebirth.mod','')
writer.records(records)
writer.handle.close()
readback=kenshi.ModFileReader(path)
assert len(readback.records)==len(records)
for key,r in records.items():
    assert key not in BASE, key
    for category,refs in r['extra'].items():
        for ref in refs: assert ref in records or ref in BASE, (key,category,ref)
readback.handle.close()
(OUT/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Built {path}: {len(records)} records; readback and reference checks passed.')
