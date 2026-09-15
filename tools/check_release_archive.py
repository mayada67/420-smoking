"""Verify the existing ZIP independently of the packaging operation."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
game=Path(r'C:\Program Files (x86)\Steam\steamapps\common\Kenshi')
audit=json.loads((root/'qa/release_audit.json').read_text(encoding='utf-8'))
assert not audit['missing_files'] and not audit['missing_references']
assert not audit['development_labels']
assert all(audit['json_matches_binary'].values())
runtime=[]
with zipfile.ZipFile(root/'dist/420_Smoking_RE_release_candidate.zip') as z:
    assert z.testzip() is None
    names=z.namelist()
    assert len(names)==len(set(names))
    assert all(not n.startswith('/') and '..' not in n.split('/') for n in names)
    manifest=json.loads(z.read('SHA256.json'))
    assert set(names)==set(manifest)|{'SHA256.json'}
    for name,digest in manifest.items():
        data=z.read(name)
        assert hashlib.sha256(data).hexdigest()==digest,name
        if name.startswith('mods/'):
            relative=name.removeprefix('mods/')
            assert data==(root/'build'/relative).read_bytes(),name
            assert data==(game/name).read_bytes(),name
            runtime.append(name)
    for relative in audit['custom_files']:
        assert 'mods/'+relative in names,relative
    for n in ['SmokingSmoke.dll','RE_Kenshi.json','420_Smoking_RE.mod']:
        assert 'mods/420_Smoking_RE/'+n in names
    assert z.read('source/src/re_smoke/SmokingSmoke.cpp')==(root/'src/re_smoke/SmokingSmoke.cpp').read_bytes()
    assert z.read('source/tools/build_re_smoke.ps1')==(root/'tools/build_re_smoke.ps1').read_bytes()
    assert z.read('README.md')==(root/'release/README.md').read_bytes()
    assert not any('420_QA' in n or 'records.json' in n for n in names)
report={'existing_archive_verified':True,'runtime_files_matching_build_and_game':len(runtime),
        'all_fcs_assets_packaged':True,'source_and_instructions_current':True,
        'runtime_visual_tested':False}
(root/'qa/release_recheck.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
