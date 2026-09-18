"""Refresh current Core aliases and bundle, preserving the released Races rc3."""
import hashlib
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'

def verify(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None
        names = z.namelist()
        assert len(names) == len(set(names))
        manifest = json.loads(z.read('SHA256.json'))
        assert set(names) == set(manifest) | {'SHA256.json'}
        for name, digest in manifest.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest, name

def main():
    # Preserve the tested preload fix; the older generic aliases predate it.
    races = (DIST / '420_Races_0.1.0-rc3_candidate.zip').read_bytes()
    verify(races)
    with zipfile.ZipFile(io.BytesIO(races)) as z:
        config = json.loads(z.read('mods/420_Races/RE_Kenshi.json'))
        assert 'SmokingRaces.dll' in config['PreloadPlugins']
    subprocess.run([sys.executable, str(ROOT / 'tools/package_release.py')], cwd=ROOT, check=True)
    core = (DIST / '420_Smoking_RE_release_candidate.zip').read_bytes()
    verify(core)
    for name in ['420_Core.zip', '420_Core_0.1.0-rc3.zip']:
        (DIST / name).write_bytes(core)
    for name in ['420_Races.zip', '420_Patches.zip']:
        (DIST / name).write_bytes(races)
    bundle = DIST / '420_Smoking_Pack.zip'
    entries = {'420_Core.zip': core, '420_Patches.zip': races,
               'TEST_INSTRUCTIONS.txt': (ROOT / 'release/TEST_INSTRUCTIONS.txt').read_bytes()}
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            z.writestr('420_Smoking_Pack/' + name, data)
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'420_Smoking_Pack/' + n for n in entries}
        for name, data in entries.items():
            assert z.read('420_Smoking_Pack/' + name) == data
    report = {'core_version': '0.1.0-rc3', 'races_version': '0.1.0-rc3',
              'archives_verified': True, 'races_rc3_preserved': True,
              'published': False, 'immediate_standing_runtime_verified': False,
              'sha256': {name: hashlib.sha256((DIST / name).read_bytes()).hexdigest()
                         for name in ['420_Core.zip', '420_Core_0.1.0-rc3.zip',
                                      '420_Patches.zip', '420_Races.zip', '420_Smoking_Pack.zip']}}
    (ROOT / 'qa/current_distribution_20260918.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
