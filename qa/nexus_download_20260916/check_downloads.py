from pathlib import Path
import json,hashlib,zipfile,sys,shutil,os,runpy,struct
root=Path.cwd(); out=root/'qa/nexus_download_20260916'; stage=out/'stage';(stage/'build').mkdir(parents=True,exist_ok=True);(stage/'qa').mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools/vendor'));import kenshi
report={'archives':{},'build_differences':[],'installed_differences':[],'source_differences':[],'mods':{},'missing_assets':[],'missing_references':[],'gameplay_tested':False}
game=Path('C:/Program Files (x86)/Steam/steamapps/common/Kenshi')
for label in ['core','races']:
 folder=out/label
 manifest=json.loads((folder/'SHA256.json').read_text())
 files={p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
 assert files==set(manifest)|{'SHA256.json'}
 for name,digest in manifest.items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest,name
 report['archives'][label]={'manifest_files_verified':len(manifest),'crc_ok':True}
 for p in (folder/'mods').rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(folder/'mods');target=stage/'build'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  for key,base in [('build_differences',root/'build'),('installed_differences',game/'mods')]:
   q=base/rel
   if not q.is_file() or q.read_bytes()!=p.read_bytes():report[key].append(str(rel))
 for p in (folder/'source/src/re_smoke').glob('*'):
  if p.suffix not in ['.cpp','.h']:continue
  if p.read_bytes()!=(root/'src/re_smoke'/p.name).read_bytes():report['source_differences'].append(p.name)
base=json.loads((root/'build/base_records.json').read_text(encoding='utf-8'));known=set(base);allrecords={}
for p in (stage/'build').glob('*/*.mod'):
 reader=kenshi.ModFileReader(p);allrecords[p.stem]=reader.records;known.update(reader.records)
 report['mods'][p.stem]={'records':len(reader.records),'dependencies':reader.dependencies};reader.handle.close()
for mod,records in allrecords.items():
 for ident,r in records.items():
  for field,refs in r['extra'].items():
   for ref in refs:
    if ref not in known:report['missing_references'].append([ident,field,ref])
  for field,value in r['fields']['filename'].items():
   if not value:continue
   value=value.replace('\\','/').removeprefix('./');p=stage/'build'/value[5:] if value.startswith('mods/') else game/value
   if not p.is_file():report['missing_assets'].append([ident,field,value])
races=allrecords['420_Races'];assert len(races)==6 and all(r['type']=='BASE_ANIMATIONS' for r in races.values())
config=json.loads((stage/'build/420_Races/Races.json').read_text());assert len({r['id'] for r in config['races']})==len(config['races'])==59
for p in (stage/'build').glob('*/*.dll'):
 data=p.read_bytes();off=struct.unpack_from('<I',data,0x3c)[0];assert data[off:off+4]==b'PE\0\0' and struct.unpack_from('<H',data,off+4)[0]==0x8664
for p in (stage/'build').glob('*/RE_Kenshi.json'):
 for dll in json.loads(p.read_text())['Plugins']:assert (p.parent/dll).is_file()
shutil.copyfile(root/'build/base_records.json',stage/'build/base_records.json');(stage/'src').mkdir(exist_ok=True);shutil.copyfile(root/'src/vanilla_humanoid_races.json',stage/'src/vanilla_humanoid_races.json')
os.chdir(stage)
for name in ['check_research_unlock.py','check_shared_workbench.py','check_release_candidate.py']:runpy.run_path(str(root/'tools'/name),run_name='__main__')
os.chdir(root)
report['enabled_mods']=(game/'data/mods.cfg').read_text().splitlines();report['data_tests_passed']=True
(out/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
