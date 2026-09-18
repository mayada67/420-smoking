"""Fault-inject the actual smoke error handler; no game process is needed."""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / 'qa/renderer_failure_fix'
out.mkdir(parents=True, exist_ok=True)
source = (root / 'src/re_smoke/SmokingSmoke.cpp').read_text(encoding='utf-8')
handler = source[source.index('void disableSmokeAfterError()'):source.index('void (*originalClear)')]
harness = r'''
#include <string>
#include <vector>
#include <cstdio>
namespace Ogre {
class Exception { public: std::string getFullDescription() const { return "injected failure"; } };
}
struct GameWorld {};
struct FakeBoards {
    bool visible, failHide, failClear;
    int count, hideCalls, clearCalls;
    FakeBoards() : visible(true), failHide(false), failClear(false), count(5), hideCalls(0), clearCalls(0) {}
    void setVisible(bool value) {
        ++hideCalls; if (failHide) throw Ogre::Exception(); visible=value;
    }
    void clear() {
        ++clearCalls; if (failClear) throw Ogre::Exception(); count=0;
    }
};
FakeBoards* boards=0;
bool disabled=false;
std::vector<int> emitters, puffs;
int gameUpdates=0, smokeUpdates=0;
void ErrorLog(const std::string&) {}
void updateSmoke(GameWorld*,float) { ++smokeUpdates; throw Ogre::Exception(); }
void originalNoop(GameWorld*,float) { ++gameUpdates; }
'''
harness += handler
harness += r'''
int main() {
    originalUpdate=&originalNoop;
    for (int test=0; test<5; ++test) {
        FakeBoards existing;
        existing.failHide=(test==2 || test==3);
        existing.failClear=(test==1 || test==3);
        boards=(test==4 ? 0 : &existing);
        disabled=false; gameUpdates=0; smokeUpdates=0;
        emitters.assign(2,1); puffs.assign(5,1);
        GameWorld world;
        try { updateHook(&world,.016f); updateHook(&world,.016f); }
        catch (...) { return 10+test; }
        if (!disabled || !emitters.empty() || !puffs.empty()) return 20+test;
        if (gameUpdates!=2 || smokeUpdates!=1) return 30+test;
        if (boards) {
            if (existing.hideCalls!=1 || existing.clearCalls!=1) return 40+test;
            if (!existing.failHide && existing.visible) return 50+test;
            if (!existing.failClear && existing.count!=0) return 60+test;
        }
        std::printf("PASS case=%d visible=%d count=%d gameUpdates=%d smokeUpdates=%d\n",
                    test,existing.visible,existing.count,gameUpdates,smokeUpdates);
    }
    return 0;
}
'''
(out / 'test.cpp').write_text(harness, encoding='utf-8')
setup = (root / 'tools/build_re_smoke.ps1').read_text(encoding='utf-8').split('$outPath =')[0]
setup = setup.replace('$rootPath = Split-Path -Parent $PSScriptRoot',
                      "$rootPath = '" + str(root).replace("'", "''") + "'")
setup += r'''
& "$vc64\bin\amd64\cl.exe" /nologo /EHsc /MD 'qa\renderer_failure_fix\test.cpp' /Foqa\renderer_failure_fix\test.obj /Feqa\renderer_failure_fix\test.exe /link kernel32.lib
if ($LASTEXITCODE -ne 0) { throw 'Fault-injection test compilation failed' }
& 'qa\renderer_failure_fix\test.exe'
if ($LASTEXITCODE -ne 0) { throw "Fault-injection test failed: $LASTEXITCODE" }
'''
(out / 'run.ps1').write_text(setup, encoding='utf-8-sig')
result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                         '-File', str(out / 'run.ps1')], cwd=root,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output = result.stdout.decode('utf-8', errors='replace')
(out / 'test.log').write_text(output, encoding='utf-8')
print(output)
result.check_returncode()
(out / 'results.json').write_text(json.dumps({
    'passed': True, 'cases': ['renderer_error', 'clear_also_throws',
                            'hide_also_throws', 'both_cleanup_calls_throw', 'no_billboards'],
    'real_handler_extracted_from_source': True,
    'game_runtime_tested': False,
    'limit': 'If both renderer operations fail, visibility cannot be guaranteed; neither exception escapes.'
}, indent=2), encoding='utf-8')
