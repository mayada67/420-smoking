"""Package English distribution guides while preserving runtime/source identifiers."""
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'release'
CJK = re.compile(r'[\u3040-\u30ff\u3400-\u9fff]')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def pack(entries):
    entries = {k: v for k, v in entries.items() if k != 'SHA256.json'}
    entries['SHA256.json'] = json.dumps({k: digest(v) for k, v in sorted(entries.items())}, indent=2).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    with zipfile.ZipFile(io.BytesIO(output.getvalue())) as archive:
        assert archive.testzip() is None
        for name, checksum in json.loads(archive.read('SHA256.json')).items():
            assert digest(archive.read(name)) == checksum
    return output.getvalue()

def main():
    readme = RELEASE / 'README.md'
    readme.write_text(readme.read_text(encoding='utf-8').split('## 日本語の要点')[0].rstrip() + '\n', encoding='utf-8')
    for target in ['src/re_smoke/README.md', 'build/420_Smoking_RE/README.md']:
        shutil.copyfile(RELEASE / 'SMOKE_PLUGIN_README.md', ROOT / target)
    subprocess.run([sys.executable, str(ROOT / 'tools/package_release.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/check_unified_races.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/package_runtime_races.py')], cwd=ROOT, check=True)
    patch_path = ROOT / 'dist/420_Patches.zip'
    patch_data = patch_path.read_bytes()
    core_path = ROOT / 'dist/420_Core.zip'
    shutil.copyfile(ROOT / 'dist/420_Smoking_RE_release_candidate.zip', core_path)
    sys.path.insert(0, str(ROOT / 'tools/vendor'))
    import kenshi
    game_text = []
    for mod in [ROOT / 'build/420_Smoking/420_Smoking.mod', ROOT / 'build/420_Smoking_RE/420_Smoking_RE.mod']:
        reader = kenshi.ModFileReader(mod)
        try:
            content = json.dumps({'description': reader.description, 'records': reader.records}, ensure_ascii=False)
            assert not CJK.search(content), mod
            game_text.append({'mod': mod.name, 'record_count': len(reader.records), 'japanese_text': False})
        finally:
            reader.handle.close()
    with zipfile.ZipFile(core_path) as core:
        assert core.testzip() is None
        for name in core.namelist():
            assert not CJK.search(name), name
            if name.endswith(('.md', '.txt', '.cpp', '.ps1', '.json')):
                assert not CJK.search(core.read(name).decode('utf-8')), name
    bundle = ROOT / 'dist/420_Smoking_Pack.zip'
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
        prefix = '420_Smoking_Pack/'
        archive.writestr(prefix + core_path.name, core_path.read_bytes())
        archive.writestr(prefix + patch_path.name, patch_data)
        archive.writestr(prefix + 'TEST_INSTRUCTIONS.txt', (RELEASE / 'TEST_INSTRUCTIONS.txt').read_bytes())
    with zipfile.ZipFile(bundle) as archive:
        assert archive.testzip() is None
        assert all(not CJK.search(n) for n in archive.namelist())
    report = {'bundle': str(bundle), 'sha256': digest(bundle.read_bytes()), 'core_game_text': game_text,
              'guides_and_archive_paths_english': True, 'patch_format': 'conditional runtime add-on',
              'exception': 'Original third-party race names and identifiers are retained in patch MODs and source manifests.'}
    output = ROOT / 'qa/english_distribution_checks.json'
    output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
