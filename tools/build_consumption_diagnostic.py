"""Build an optional diagnostic override; never enable it automatically."""
import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
base=json.loads(Path('build/base_records.json').read_text(encoding='utf-8'))
main=json.loads(Path('build/420_Smoking/records.json').read_text(encoding='utf-8'))
records={}
for n in [13,14,23,24]:
    ident=f'{n}-420_Smoking.mod'
    record=copy.deepcopy(main[ident])
    record.update(datatype_id=-2147483647,datatype='CHANGED')
    record['fields']={k:{} for k in record['fields']}
    record['instances']={}
    if n in [13,14]:
        animation=40 if n==13 else 41
        tool=3 if n==13 else 2
        record['extra']={'animation':{f'{animation}-420_Smoking.mod':kenshi.EXTRA_ITEM_REMOVED,'14533-gamedata.base':[0,0,0]},'special tool':{f'{tool}-420_Smoking.mod':kenshi.EXTRA_ITEM_REMOVED}}
    else:
        record['extra']={'parts':{'52-420_Smoking.mod':kenshi.EXTRA_ITEM_REMOVED,'3447-D-otto.mod':[0,100,0]}}
    records[ident]=record
out=Path('build/420_Consumption_Diagnostic');out.mkdir(exist_ok=True)
w=kenshi.ModFileWriter(out/'420_Consumption_Diagnostic.mod',1,'420 project','OPTIONAL TEST ONLY: vanilla stool/sitting, no custom hand props; consumption settings unchanged. Load after 420_Smoking. Disable after testing.','gamedata.base,Newwworld.mod,Dialogue.mod,rebirth.mod,420_Smoking.mod','')
w.records(records);w.handle.close()
r=kenshi.ModFileReader(out/'420_Consumption_Diagnostic.mod');assert len(r.records)==4
merged=copy.deepcopy(main)
kenshi.merge_records(r,merged)
for n in [13,14]:
    extra=merged[f'{n}-420_Smoking.mod']['extra']
    assert set(extra['animation'])=={'14533-gamedata.base'}
    assert not extra['special tool']
    assert extra['consumes']==main[f'{n}-420_Smoking.mod']['extra']['consumes']
for n in [23,24]:assert set(merged[f'{n}-420_Smoking.mod']['extra']['parts'])=={'3447-D-otto.mod'}
r.handle.close()
print('Built optional diagnostic override; NOT installed or enabled.')
