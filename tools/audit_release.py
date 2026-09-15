"""Read the actual release-candidate binaries; do not rebuild or deploy them."""
import hashlib
import math
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
import kenshi

root = Path(__file__).resolve().parents[1]
game = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Kenshi')
base = json.loads((root / 'build/base_records.json').read_text(encoding='utf-8'))
mods = {}
report = {'mods': {}, 'missing_references': [], 'missing_files': [], 'custom_files': [],
          'installed_differences': [], 'names_and_descriptions': [], 'development_labels': []}
for name in ['420_Smoking', '420_Smoking_RE']:
    reader = kenshi.ModFileReader(root / f'build/{name}/{name}.mod')
    mods[name] = reader.records
    report['mods'][name] = {k: getattr(reader, k) for k in ['version', 'author', 'description', 'dependencies', 'record_count']}
    reader.handle.close()

known = set(base) | set(mods['420_Smoking']) | set(mods['420_Smoking_RE'])
custom = set()
for mod, records in mods.items():
    for ident, record in records.items():
        strings = record['fields']['string']
        report['names_and_descriptions'].append({'mod': mod, 'id': ident, 'name': record['name'], 'strings': strings})
        for field, value in {'name': record['name'], **strings}.items():
            if any(marker in value.lower() for marker in ['[alpha', 'prototype', 'static wisp', 'smoking test', 'not verified']):
                report['development_labels'].append({'id': ident, 'field': field, 'value': value})
        for category, refs in record['extra'].items():
            for ref in refs:
                if ref not in known:
                    report['missing_references'].append([ident, category, ref])
        for instance in record['instances'].values():
            if instance['target'] not in known:
                report['missing_references'].append([ident, 'instance', instance['target']])
        for field, value in record['fields']['filename'].items():
            if not value:
                continue
            relative = value.replace('\\', '/').removeprefix('./')
            if relative.startswith('mods/'):
                path = root / 'build' / relative[5:]
                custom.add(relative[5:])
            else:
                path = game / relative
            if not path.is_file():
                report['missing_files'].append([ident, field, value])

report['custom_files'] = sorted(custom)
report['not_directly_referenced_files'] = []
for mod in mods:
    for path in sorted((root / 'build' / mod).rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(root / 'build').as_posix()
        installed = game / 'mods' / relative
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if not installed.is_file() or hashlib.sha256(installed.read_bytes()).hexdigest() != digest:
            report['installed_differences'].append(relative)
        if relative not in custom:
            report['not_directly_referenced_files'].append(relative)
plugin = json.loads((root / 'build/420_Smoking_RE/RE_Kenshi.json').read_text(encoding='utf-8-sig'))
report['plugin_files_exist'] = all((root / 'build/420_Smoking_RE' / p).is_file() for p in plugin['Plugins'])
report['plugin_source_matches'] = (root / 'src/re_smoke/SmokingSmoke.cpp').read_bytes() == (root / 'build/420_Smoking_RE/SmokingSmoke.cpp').read_bytes()
report['enabled_mods'] = (game / 'data/mods.cfg').read_text().splitlines()
records = mods['420_Smoking']
sid = lambda n: f'{n}-420_Smoking.mod'
report['research_unlock'] = records[sid(30)]
report['animation_registration'] = {
    'race_overrides': [key for key in records if key in base and records[key]['extra'].get('animation files')],
    'files': {sid(n): records[sid(n)]['fields']['filename'] for n in [42, 62]},
}
source = (root / 'src/re_smoke/SmokingSmoke.cpp').read_text()
report['animation_routes'] = []
for building, fn, anim, prop, file_id in [(23,13,40,54,42),(24,14,41,55,42),(27,58,60,54,62),(28,59,61,55,62)]:
    name = records[sid(anim)]['fields']['string']['anim name']
    filename = records[sid(file_id)]['fields']['filename']['male animation'].replace('\\','/').removeprefix('./mods/')
    passed = (sid(fn) in records[sid(building)]['extra']['functionality']
              and sid(anim) in records[sid(fn)]['extra']['animation']
              and sid(prop) in records[sid(fn)]['extra']['special tool']
              and name in source and name.encode() in (root/'build'/filename).read_bytes())
    report['animation_routes'].append({'building': sid(building), 'animation': name, 'valid': passed})
report['json_matches_binary'] = {}
report['json_binary_differences'] = {}
def compare(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        return [x for key in a.keys() | b.keys() for x in compare(a.get(key), b.get(key), path+'/'+key)]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [x for i, (left, right) in enumerate(zip(a,b)) for x in compare(left,right,path+'/'+str(i))]
    if isinstance(a, (float,int)) and isinstance(b, (float,int)) and math.isclose(a,b,rel_tol=1e-6,abs_tol=1e-7):
        return []
    return [] if a == b else [{'path':path, 'json':a, 'binary':b}]
for mod in mods:
    cached = json.loads((root / f'build/{mod}/records.json').read_text(encoding='utf-8'))
    differences = compare(cached, json.loads(json.dumps(mods[mod])))
    report['json_matches_binary'][mod] = not differences
    report['json_binary_differences'][mod] = differences
(root / 'qa/release_audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
