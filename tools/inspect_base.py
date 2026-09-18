import sys, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import kenshi
root = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Kenshi')
records = {}
for name in ['gamedata.base', 'Newwworld.mod', 'Dialogue.mod', 'rebirth.mod']:
    source = kenshi.ModFileReader(root / 'data' / name)
    print(name, source.record_count)
    kenshi.merge_records(source, records)
    source.handle.close()
Path('build/base_records.json').write_text(json.dumps(records, ensure_ascii=False), encoding='utf-8')
pattern = re.compile(r'hemp|hashish|fabric|loom|stool|chair|bench|furnace|sitting|sit chair', re.I)
selection = {k:v for k,v in records.items() if v['type_id'] in [0,4,24,62] and pattern.search(v['name'])}
Path('qa/base_candidates.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2), encoding='utf-8')
for k,v in selection.items(): print(k, v['type'], v['name'])
