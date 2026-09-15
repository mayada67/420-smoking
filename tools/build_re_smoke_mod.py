"""Create an optional overlay. Base MOD stays usable without RE_Kenshi."""
import copy, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
out=Path('build/420_Smoking_RE');out.mkdir(parents=True,exist_ok=True)
base=json.loads(Path('build/420_Smoking/records.json').read_text(encoding='utf-8'))
records={}
# Override the display models, preserving the existing special-tool references.
# This avoids combining the vanilla static wisps with emitted particles.
for n,original in [(54,3),(55,2)]:
    key=f'{n}-420_Smoking.mod'
    record=copy.deepcopy(base[key])
    record.update(datatype_id=-2147483647,datatype='CHANGED',instance_count=0,id=0)
    record['fields']={category:{} for category in record['fields']}
    record['fields']['filename']['mesh']=base[f'{original}-420_Smoking.mod']['fields']['filename']['mesh']
    record['extra']={}
    record['instances']={}
    records[key]=record
# Keep the single material reference intact; override its texture fields instead
# of adding a second reference through FCS's additive reference merging.
material=copy.deepcopy(base['53-420_Smoking.mod'])
material.update(datatype_id=-2147483647,datatype='CHANGED',instance_count=0,id=0)
material['fields']={category:{} for category in material['fields']}
for category in ['filename','int','float']:
    material['fields'][category]=copy.deepcopy(base['50-420_Smoking.mod']['fields'][category])
material['extra']={};material['instances']={}
records['53-420_Smoking.mod']=material
path=out/'420_Smoking_RE.mod'
writer=kenshi.ModFileWriter(path,1,'420 project','EXPERIMENTAL: animated mouth and tip smoke. Requires RE_Kenshi and 420_Smoking.','gamedata.base,Newwworld.mod,Dialogue.mod,rebirth.mod,420_Smoking.mod','')
writer.records(records);writer.handle.close()
reader=kenshi.ModFileReader(path)
assert set(reader.records)==set(records)
reader.handle.close()
(out/'RE_Kenshi.json').write_text(json.dumps({'Plugins':['SmokingSmoke.dll']},indent=2),encoding='utf-8')
(out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Optional overlay generated; DLL and in-game verification are separate checks.')
