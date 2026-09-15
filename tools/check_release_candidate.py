"""Validate the release FCS, race scope and existing save identities."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
base=json.loads(Path('build/base_records.json').read_text(encoding='utf-8'))
manifest=json.loads(Path('src/vanilla_humanoid_races.json').read_text())
reader=kenshi.ModFileReader(Path('build/420_Smoking/420_Smoking.mod'))
records=reader.records
sid=lambda n:f'{n}-420_Smoking.mod'
core={'Greenlander','Scorchlander','Shek','Hive Prince','Hive Soldier Drone','Hive Worker Drone','Skeleton'}
assert core <= set(manifest.values())
for key in manifest:
    r=records[key]
    assert r['datatype']=='CHANGED'
    assert all(not fields for fields in r['fields'].values())
    assert r['extra']=={'animation files':{sid(42):(0,0,0),sid(62):(0,0,0)}}
    assert not r['instances']
assert {k for k in records if k in base} == set(manifest)
for n in [42,62]:
    f=records[sid(n)]['fields']['filename']
    assert f['male animation'] and f['female animation']==f['male animation'].replace('_male','_female')
for r in records.values():
    if r['type']=='RACE': continue
    text=json.dumps([r['name'],r['fields']['string']]).lower()
    assert not any(s in text for s in ['[alpha','prototype','smoking test','static wisp','not verified'])
assert records[sid(30)]['name']=='420 Smoking'
assert records[sid(30)]['fields']['int']['time']==4
reader.handle.close()
print(f'PASS: {len(manifest)} humanoid registrations, both gender slots, additive race changes, release labels.')
