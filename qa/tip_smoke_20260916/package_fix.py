"""Repackage the downloaded Core with only the verified smoke update."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
original = Path('C:/Users/DQN6/Desktop/420 Core 2173 0.1.0-rc1 2026-09-15T12-16Z XMZvUui1B.zip')
source = (root / 'src/re_smoke/SmokingSmoke.cpp').read_bytes()
assert b'kTipSize = .30f' in source and b'kTipOpacity = .28f' in source
assert b'setDepthCheckEnabled(true)' in source
assert b'Ogre::ColourValue(1,0,0,alpha)' not in source
with zipfile.ZipFile(original) as archive:
    files = {n: archive.read(n) for n in archive.namelist() if not n.endswith('/')}
files['mods/420_Smoking_RE/SmokingSmoke.dll'] = (root / 'build/420_Smoking_RE/SmokingSmoke.dll').read_bytes()
files['source/src/re_smoke/SmokingSmoke.cpp'] = source
files['source/src/re_smoke/README.md'] = (root / 'src/re_smoke/README.md').read_bytes()
files['README.md'] += b'\n\nTip smoke visibility update (Core rc2 candidate): increased tip emission, size and opacity. Mouth smoke and save data are unchanged.\n'
files.pop('SHA256.json', None)
files['SHA256.json'] = json.dumps({n: hashlib.sha256(v).hexdigest() for n, v in sorted(files.items())}, indent=2).encode()
output = root / 'dist/420_Core_0.1.0-rc2_candidate.zip'
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for n, data in sorted(files.items()):
        archive.writestr(n, data)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    for n, digest in json.loads(archive.read('SHA256.json')).items():
        assert hashlib.sha256(archive.read(n)).hexdigest() == digest
    game = Path('C:/Program Files (x86)/Steam/steamapps/common/Kenshi')
    for n in archive.namelist():
        if n.startswith('mods/'):
            assert archive.read(n) == (game / n).read_bytes(), n
print(output)
print(hashlib.sha256(output.read_bytes()).hexdigest())
