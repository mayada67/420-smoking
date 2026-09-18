from pathlib import Path
import json, zipfile, hashlib
root=Path.cwd();out=root/'qa/nexus_download_20260916'
config=json.dumps({'PreloadPlugins':['SmokingRaces.dll']},indent=2).encode()+b'\n'
(root/'build/420_Races/RE_Kenshi.json').write_bytes(config)
with zipfile.ZipFile(next(Path('C:/Users/DQN6/Desktop').glob('420 Races 2173*.zip'))) as z: entries={n:z.read(n) for n in z.namelist() if n!='SHA256.json'}
entries['mods/420_Races/RE_Kenshi.json']=config
entries['README.md']=(root/'release/RACES_README.md').read_bytes()
entries['source/README.md']=(root/'release/RACES_BUILD.md').read_bytes()
entries['SHA256.json']=json.dumps({n:hashlib.sha256(b).hexdigest() for n,b in sorted(entries.items())},indent=2).encode()
target=root/'dist/420_Races_0.1.0-rc3_candidate.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for n,b in sorted(entries.items()):z.writestr(n,b)
with zipfile.ZipFile(target) as z:
 assert z.testzip() is None
 for n,h in json.loads(z.read('SHA256.json')).items():assert hashlib.sha256(z.read(n)).hexdigest()==h
assert entries['mods/420_Races/SmokingRaces.dll']==(out/'races/mods/420_Races/SmokingRaces.dll').read_bytes()
result={'corrected_archive':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'dll_unchanged':True,'runtime_changed_files':['mods/420_Races/RE_Kenshi.json'],'original_applied_log_absent':'420 Races: applied to' not in (out/'runtime_original.log').read_text(),'preload_no_originals_passed':'applied to 0 ' in (out/'runtime_preload_zero.log').read_text(),'preload_2B_passed':'applied to 2 ' in (out/'runtime_preload_2B.log').read_text(),'disabled_with_2B_passed':'applied to 0 ' in (out/'runtime_preload_disabled.log').read_text(),'published':False}
assert all(result[k] for k in ['original_applied_log_absent','preload_no_originals_passed','preload_2B_passed','disabled_with_2B_passed'])
(out/'runtime_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
