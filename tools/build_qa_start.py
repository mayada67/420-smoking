import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
d=json.loads(Path('build/base_records.json').read_text(encoding='utf-8'));records={}
def add(source,n,name):
 r=copy.deepcopy(d[source]);r.update(name=name,id=0,instance_count=0,datatype_id=-2147483646,datatype='NEW');records[f'{n}-420_QA.mod']=r;return r
c=add('1533662-rebirth.mod',1,'420 QA Tester')
stats=add('1773-gamedata.base',4,'420 QA All Skills 100')
stats['fields']['float']={k:100.0 for k in stats['fields']['float']}
bag=add('45555-changes_otto.mod',5,'420 QA Supply Backpack')
bag['fields']['int'].update({'storage size height':20,'storage size width':20,'stackable bonus minimum':1000,'combat skill bonus':0})
bag['fields']['float'].update({'stackable bonus mult':1000.0,'encumbrance effect':0.0,'weight kg':0.0,'athletics mult':1.0,'combat speed mult':1.0,'stealth mult':1.0})
bag['fields']['string']['description']='Development supplies backpack: 20x20, large stacks, no weight or skill penalty.'
c['fields']['int']['female chance']=0
c['fields']['int']['stats randomise']=0
c['extra']['stats']={'4-420_QA.mod':[0,100,0]}
c['extra']['race']={'17-gamedata.quack':[100,0,0]}
c['extra']['backpack']={'5-420_QA.mod':[1,100,0]}
supplies={'580-gamedata.base':200,'42159-gamedata.base':200,'579-gamedata.base':100,'42164-gamedata.base':100,'1965-gamedata.base':200,'1230-gamedata.base':200,'1-420_Smoking.mod':200,'2-420_Smoking.mod':100,'43959-rebirth.mod':20}
c['extra']['inventory']={k:[v,0,0] for k,v in supplies.items()}
s=add('45550-gamedata.base',2,'420 QA Squad');s['extra']['leader']={'1-420_QA.mod':[1,0,0]}
start=add('1980-gamedata.base',3,'420 QA - ALL 100 - 1M CATS - HEFT')
start['fields']['int']['money']=1000000
start['fields']['string']['description']='Smoking MOD test: all 33 skills 100, 1,000,000 Cats, supply backpack, building materials, iron plates, steel bars, electrical components, hemp, hashish, paper, joints and food. Starts in Heft. Buy an intact house for indoor testing. New game only.'
start['fields']['bool']['force start pos']=False
start['extra']['town']={'1078-gamedata.base':[0,0,0]}
start['extra']['squad']={'2-420_QA.mod':[0,0,0]};start['extra']['research']={'30-420_Smoking.mod':[0,0,0]}
out=Path('build/420_QA');out.mkdir(exist_ok=True)
w=kenshi.ModFileWriter(out/'420_QA.mod',1,'420 project','Development test start only','gamedata.base,Newwworld.mod,Dialogue.mod,rebirth.mod,420_Smoking.mod','');w.records(records);w.handle.close()
r=kenshi.ModFileReader(out/'420_QA.mod')
assert len(r.records)==5
assert set(r.records['4-420_QA.mod']['fields']['float'].values())=={100.0}
assert r.records['3-420_QA.mod']['fields']['int']['money']==1000000
main=json.loads(Path('build/420_Smoking/records.json').read_text(encoding='utf-8'))
for rec in r.records.values():
 for refs in rec['extra'].values():
  for ref in refs: assert ref in records or ref in d or ref in main,ref
r.handle.close()
(out/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
Path('qa/test_start_checks.json').write_text(json.dumps({'readback':True,'skills':len(stats['fields']['float']),'skill_value':100,'cats':1000000,'spawn':'Heft','supplies':supplies,'in_game_verified':False},indent=2),encoding='utf-8')
print('Built QA start: all skills 100, 1M Cats, Heft, supply backpack. Readback and references passed.')
