"""Check the built extension against installed game exports, without loading code."""
import json,re,sys,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
text=Path('qa/re_smoke_imports.txt').read_text(encoding='utf-8-sig')
checked={}
for name,file in [('KenshiLib.dll','installed_kenshilib_exports.txt'),('OgreMain_x64.dll','installed_ogre_exports.txt')]:
    match=re.search(r'^    '+re.escape(name)+r'\s*\n(.*?)(?=^    \S|\Z)',text,re.M|re.S)
    assert match,name
    imported=re.findall(r'^\s+[0-9A-F]+ (\?\S+)',match.group(1),re.M)
    assert imported,name
    exports=Path('qa/'+file).read_text(encoding='utf-8-sig')
    names=set(re.findall(r'^\s+\d+\s+[0-9A-F]+\s+[0-9A-F]+\s+(\S+)',exports,re.M))
    missing=[symbol for symbol in imported if symbol not in names]
    assert not missing,(name,missing)
    checked[name]=len(imported)
dll=Path('build/420_Smoking_RE/SmokingSmoke.dll').read_bytes()
offset=struct.unpack_from('<I',dll,0x3c)[0]
assert dll[offset:offset+4]==b'PE\0\0'
assert struct.unpack_from('<H',dll,offset+4)[0]==0x8664
assert b'?startPlugin@@YAXXZ\0' in dll
reader=kenshi.ModFileReader(Path('build/420_Smoking_RE/420_Smoking_RE.mod'))
assert set(reader.records)=={'53-420_Smoking.mod','54-420_Smoking.mod','55-420_Smoking.mod'}
for item in reader.records.values(): assert item['datatype']=='CHANGED'
reader.handle.close()
report={'x64_dll':True,'plugin_entry_exported':True,'installed_game_imports_resolve':checked,'overlay_records':3,'scope':'static binary and FCS checks; runtime evidence is recorded separately'}
Path('qa/re_smoke_checks.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report))
