"""Check vanilla starting construction and existing QA-save unlock coverage."""
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import kenshi

base = json.loads(Path('build/base_records.json').read_text(encoding='utf-8'))
main = kenshi.ModFileReader('build/420_Smoking/420_Smoking.mod')
qa = kenshi.ModFileReader('build/420_QA/420_QA.mod')
merged = copy.deepcopy(base)
kenshi.merge_records(main, merged)
before = copy.deepcopy(merged)
kenshi.merge_records(qa, merged)
start = merged['3-420_QA.mod']['extra']['research']
assert {'5359-gamedata.base', '30-420_Smoking.mod'} <= set(start)
defaults = base['5359-gamedata.base']['extra']
smoking = merged['30-420_Smoking.mod']
for category, refs in defaults.items():
    assert set(refs) <= set(smoking['extra'][category])
for category, refs in before['30-420_Smoking.mod']['extra'].items():
    assert set(refs) <= set(smoking['extra'][category])
assert smoking['fields'] == before['30-420_Smoking.mod']['fields']
for key in base:
    assert merged[key] == before[key], key
assert set(qa.records) & set(base) == set()
main.handle.close()
qa.handle.close()
print('PASS: default starting research; 11 vanilla buildings and 1 item restored through QA-only research overlay; smoking unlocks and vanilla records preserved.')
