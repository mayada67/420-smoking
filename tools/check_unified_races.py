"""Prepare and verify unified patch against exact locally installed originals."""
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/vendor'))
import kenshi
game=Path('C:/Program Files (x86)/Steam/steamapps/common/Kenshi')
files=list((game/'mods').rglob('*.mod'))+list((game.parent.parent/'workshop/content/233860').rglob('*.mod'))
manifest=json.loads((ROOT/'build/420_Races/patch_manifest.json').read_text())
u=kenshi.ModFileReader(ROOT/'build/420_Races/420_Races.mod')
config=json.loads((ROOT/'build/420_Races/Races.json').read_text())
loader=json.loads((ROOT/'build/420_Races/RE_Kenshi.json').read_text())
assert loader == {'PreloadPlugins':['SmokingRaces.dll']}, 'Race registration must hook before game-data post-processing.'
configured={r['id']:r['profile'] for r in config['races']}
assert len(configured)==len(config['races'])==59
assert len(u.records)==6 and all(r['type']=='BASE_ANIMATIONS' for r in u.records.values())
expected={r['id']:'_'.join(r['profile']) for m in manifest['sources'] for r in m['included']}
assert configured==expected
for record in u.records.values():
    for asset in record['fields']['filename'].values():
        assert (ROOT/'build'/asset.replace('\\','/').split('/mods/',1)[-1]).is_file(), asset
scenarios=[]
for m in manifest['sources']:
    candidates=[p for p in files if p.name==m['original'] and hashlib.sha256(p.read_bytes()).hexdigest()==m['source_sha256']]
    assert candidates, m['original']
    path=candidates[0]
    original=kenshi.ModFileReader(path)
    for race in m['included']:
        sid=race['id']; assert sid in original.records
        assert original.records[sid]['type']=='RACE'
    original.handle.close()
    scenarios.append({'name':m['patch'],'file':str(path),'races':[r['id'] for r in m['included']]})
(ROOT/'qa/unified_race_scenarios.json').write_text(json.dumps(scenarios,indent=2),encoding='utf-8')
u.handle.close()
print('PASS: 59 configured original IDs/profiles, exact source hashes, six animation records/assets, zero race records.')
