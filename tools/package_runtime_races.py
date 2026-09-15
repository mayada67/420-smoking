"""Package the conditional race add-on without altering the core under review."""
import hashlib,json,zipfile
from pathlib import Path
from package_english_bundle import pack
root=Path(__file__).resolve().parents[1]
entries={}
for name in ['420_Races.mod','SmokingRaces.dll','Races.json','RE_Kenshi.json','patch_manifest.json']:
    entries['mods/420_Races/'+name]=(root/'build/420_Races'/name).read_bytes()
entries['README.md']=(root/'release/RACES_README.md').read_bytes()
entries['source/README.md']=(root/'release/RACES_BUILD.md').read_bytes()
entries['source/BUILD.md']=(root/'release/BUILD.md').read_bytes()
entries['source/LICENSE']=(root/'build/420_Smoking_RE/LICENSE').read_bytes()
for name in ['SmokingRaces.cpp','RacePatchLogic.h','RacePatchConfig.h']:
    entries['source/src/re_smoke/'+name]=(root/'src/re_smoke'/name).read_bytes()
entries['source/tools/build_re_races.ps1']=(root/'tools/build_re_races.ps1').read_bytes()
archive=root/'dist/420_Patches.zip'
data=pack(entries);archive.write_bytes(data)
(root/'dist/420_Races.zip').write_bytes(data)
bundle=root/'dist/420_Smoking_Pack.zip'
contents={}
if bundle.exists():
    with zipfile.ZipFile(bundle) as z: contents={n:z.read(n) for n in z.namelist()}
else:
    contents['420_Smoking_Pack/420_Core.zip']=(root/'dist/420_Core.zip').read_bytes()
contents['420_Smoking_Pack/420_Patches.zip']=data
contents['420_Smoking_Pack/TEST_INSTRUCTIONS.txt']=(root/'release/TEST_INSTRUCTIONS.txt').read_bytes()
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in contents.items(): z.writestr(n,b)
report={'file':str(archive),'sha256':hashlib.sha256(data).hexdigest(),'dll_sha256':hashlib.sha256(entries['mods/420_Races/SmokingRaces.dll']).hexdigest(),'race_records':0,'configured_races':59,'individual_patch_count':0,'installer_included':False,'runtime_gameplay_tested':False,'nexus_updated':False}
(root/'qa/runtime_races/package.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
