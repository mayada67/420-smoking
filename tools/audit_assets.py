"""Audit packaged custom references from the actual MOD binary."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'vendor'))
import kenshi
root=Path('build/420_Smoking')
reader=kenshi.ModFileReader(root/'420_Smoking.mod')
records=reader.records
reader.handle.close()
files={}
for ident,record in records.items():
    for field,value in record['fields']['filename'].items():
        prefix='.\\mods\\420_Smoking\\'
        if not value.startswith(prefix):continue
        relative=value[len(prefix):].replace('\\','/')
        path=root/relative
        assert path.is_file() and path.stat().st_size>0,(ident,field,value)
        data=path.read_bytes()
        entry={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        if path.suffix=='.png':
            assert data[:8]==b'\x89PNG\r\n\x1a\n',relative
            pos=8;compressed=b'';ended=False
            while pos<len(data):
                size=struct.unpack('>I',data[pos:pos+4])[0]
                kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+size]
                crc=struct.unpack('>I',data[pos+8+size:pos+12+size])[0]
                assert zlib.crc32(kind+chunk)&0xffffffff==crc,relative
                if kind==b'IHDR':entry['png_header']=list(struct.unpack('>IIBBBBB',chunk))
                if kind==b'IDAT':compressed+=chunk
                pos+=size+12
                if kind==b'IEND':ended=True;break
            assert ended and zlib.decompress(compressed),relative
        if field=='icon':
            assert relative.startswith('items/icons/'),relative
            assert record['fields']['bool']['auto icon'] is False
        files[relative]=entry
storage=records['25-420_Smoking.mod']
assert storage['extra']['limit inventory']=={'1-420_Smoking.mod':(0,0,0)}
report={'binary_custom_references_exist':True,'png_crc_and_decompression':True,'files':files,'in_game_verified':False}
Path('qa/asset_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(f'{len(files)} referenced asset files checked; PNG integrity and explicit icon settings passed. Game rendering remains unverified.')
