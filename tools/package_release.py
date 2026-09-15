"""Create a candidate ZIP from an allowlist; inspect its contents and hashes."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'dist';out.mkdir(exist_ok=True)
files={}
for name in ['420_Smoking','420_Smoking_RE']:
    folder=root/'build'/name
    files[f'mods/{name}/{name}.mod']=folder/f'{name}.mod'
    if name=='420_Smoking':
        for p in (folder/'assets').iterdir():
            if p.suffix in {'.mesh','.skeleton','.xml','.png'} and not p.name.endswith('_icon.png'):
                files[f'mods/{name}/assets/{p.name}']=p
        for p in (folder/'items/icons').glob('*.png'): files[f'mods/{name}/items/icons/{p.name}']=p
    else:
        for n in ['RE_Kenshi.json','SmokingSmoke.dll']:files[f'mods/{name}/{n}']=folder/n
files['README.md']=root/'release/README.md'
files['source/BUILD.md']=root/'release/BUILD.md'
files['source/LICENSE']=root/'build/420_Smoking_RE/LICENSE'
for p in ['src/re_smoke/SmokingSmoke.cpp','src/re_smoke/README.md','tools/build_re_smoke.ps1']:
    files['source/'+p]=root/p
manifest={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in sorted(files.items())}
archive=out/'420_Smoking_RE_release_candidate.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for name,path in sorted(files.items()): z.write(path,name)
    z.writestr('SHA256.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
assert not any('420_QA' in n or 'records.json' in n or 'Prototype' in n for n in files)
(root/'qa/release_package_checks.json').write_text(json.dumps({'archive':str(archive),'file_count':len(files)+1,'hashes_match':True,'game_launch_tested':False,'manifest':manifest},indent=2))
print(f'PASS: {archive}, {len(files)+1} files, all hashes verified.')
