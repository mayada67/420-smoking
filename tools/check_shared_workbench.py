"""Validate the shipped binary's recipe routing and ingredient separation."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
reader=kenshi.ModFileReader(Path('build/420_Smoking/420_Smoking.mod'))
records=reader.records
def sid(n):return f'{n}-420_Smoking.mod'
for bench in [21,22]:
    refs=records[sid(bench)]['extra']['functionality']
    assert list(refs)==[sid(11)],refs
    fn=records[sid(11)]
    assert fn['fields']['int']['function']==10
    assert not fn['fields']['bool']['overrides ingredients']
    assert set(fn['extra']['item crafts'])=={sid(1),sid(2)}
    assert not fn['extra'].get('produces') and not fn['extra'].get('consumes')
assert records[sid(1)]['extra']['ingredients']=={'1965-gamedata.base':(100,0,0)}
assert records[sid(2)]['extra']['ingredients']=={'1965-gamedata.base':(100,0,0),sid(1):(100,0,0)}
for storage,item in [(25,1),(26,2)]:
    assert records[sid(storage)]['extra']['limit inventory']=={sid(item):(0,0,0)}
    assert sid(storage) in records[sid(30)]['extra']['enable buildings']
assert records[sid(25)]['fields']['int']==records[sid(26)]['fields']['int']
assert records[sid(25)]['fields']['float']==records[sid(26)]['fields']['float']
assert records[sid(25)]['extra']['parts']==records[sid(26)]['extra']['parts']
assert sid(22) not in records[sid(30)]['extra']['enable buildings']
assert {sid(1),sid(2)} <= set(records[sid(30)]['extra']['enable item'])
reader.handle.close()
report={'binary_readback':True,'shared_recipe_queue':True,'legacy_bench_supported':True,
        'paper_requires_only_hemp':True,'joint_requires_hemp_and_paper':True,
        'dedicated_paper_and_joint_storage':True,'in_game_production_verified':False}
Path('qa/shared_workbench_checks.json').write_text(json.dumps(report,indent=2))
print(report)
