"""Compile and exercise the actual registration implementation with a fake database."""
import json, subprocess, shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'qa/runtime_races'; out.mkdir(exist_ok=True)
source=(root/'src/re_smoke/SmokingRaces.cpp').read_text(encoding='utf-8-sig')
body='\n'.join(line for line in source.splitlines() if not line.startswith('#include'))
header=r'''
#include <string>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <cassert>
#include <cstdio>
#include <fstream>
#include <Windows.h>
#include "../../src/re_smoke/RacePatchLogic.h"
#include "../../src/re_smoke/RacePatchTable.h"
#include "../../src/re_smoke/RacePatchConfig.h"
enum itemType {RACE=7, ANIMATION_FILE=112};
struct GameData {
 itemType type; std::set<std::string> refs; int stats; bool fail;
 GameData():type(RACE),stats(123),fail(false){}
 bool findInList(const std::string&,const std::string& id){return refs.count(id)!=0;}
 void addToList(const std::string&,const std::string& id,int,int,int){if(fail)throw std::runtime_error("injected");refs.insert(id);}
};
struct GameDataManager {
 std::map<std::string,GameData> data;
 GameData* getData(const std::string& id,itemType t){std::map<std::string,GameData>::iterator it=data.find(id);return it!=data.end()&&it->second.type==t?&it->second:0;}
 void postProcessingTheDatas(){}
};
int postCalls=0, logs=0, errors=0;
void DebugLog(const std::string&){++logs;} void ErrorLog(const std::string&){++errors;}
void originalFake(GameDataManager*){++postCalls;}
namespace KenshiLib {
 const int SUCCESS=0; int result=0;
 template<class T> void* GetRealAddress(T){return 0;}
 template<class T> int AddHook(void*,T hook,T* original){if(result==0)*original=&originalFake;return result;}
}
'''
tests=r'''
void animations(GameDataManager& d){for(unsigned i=0;i<59;++i){d.data[kRacePatches[i].standing].type=ANIMATION_FILE;d.data[kRacePatches[i].reclining].type=ANIMATION_FILE;}}
int main(){
 loadConfiguration(); assert(configuredRaces.size()==59&&configurationReady);
 originalPostProcess=&originalFake;
 GameDataManager empty; postProcessHook(&empty); assert(empty.data.empty()&&postCalls==1);
 GameDataManager zero; animations(zero); size_t n=zero.data.size(); postProcessHook(&zero); assert(zero.data.size()==n);
 for(unsigned count=1;count<=59;++count){
  GameDataManager d; animations(d);
  for(unsigned i=0;i<count;++i){d.data[kRacePatches[i].race].refs.insert("existing-animation");}
  d.data["unsupported-race"].refs.insert("other"); n=d.data.size();
  postProcessHook(&d);postProcessHook(&d);
  assert(d.data.size()==n&&d.data["unsupported-race"].refs.size()==1);
  for(unsigned i=0;i<count;++i){GameData& r=d.data[kRacePatches[i].race];assert(r.stats==123&&r.refs.size()==3&&r.refs.count("existing-animation"));}
 }
 GameDataManager missing; missing.data[kRacePatches[0].race]; missing.data[kRacePatches[0].standing].type=ANIMATION_FILE;
 postProcessHook(&missing);assert(missing.data[kRacePatches[0].race].refs.empty());
 GameDataManager wrong; animations(wrong); wrong.data[kRacePatches[0].race].type=ANIMATION_FILE;
 postProcessHook(&wrong);assert(wrong.data[kRacePatches[0].race].refs.empty());
 GameDataManager broken;animations(broken);broken.data[kRacePatches[0].race].fail=true;
 int before=postCalls;postProcessHook(&broken);assert(postCalls==before+1&&errors==1);
 KenshiLib::result=1;startPlugin();assert(errors==2);
 KenshiLib::result=0;startPlugin();assert(originalPostProcess==&originalFake);
 const char* bad[]={"{}", "{\"version\":2,\"races\":[]}", "{\"version\":1,\"races\":[{\"id\":\"x\",\"profile\":\"wrong\"}]}", "{\"version\":1,\"races\":[{\"id\":\"x\",\"profile\":\"male_male\"},{\"id\":\"x\",\"profile\":\"male_male\"}]}"};
 for(unsigned i=0;i<4;++i){bool rejected=false;try{std::istringstream in(bad[i]);readRaceConfiguration(in);}catch(const std::exception&){rejected=true;}assert(rejected);}
 std::istringstream custom("{\"version\":1,\"races\":[{\"id\":\"user-race\",\"profile\":\"male_female\"}]}");
 configuredRaces=readRaceConfiguration(custom);GameDataManager extended;animations(extended);extended.data["user-race"];
 postProcessHook(&extended);assert(extended.data["user-race"].refs.size()==2);
 puts("PASS: zero originals, 59 subset sizes, all originals, repeat application, unsupported race, missing animation, wrong type, exception continuation, hook failure.");
}
'''
(out/'test.cpp').write_text(header+body+tests,encoding='utf-8')
shutil.copyfile(root/'build/420_Races/Races.json',out/'Races.json')
setup=(root/'tools/build_re_smoke.ps1').read_text(encoding='utf-8-sig').split('$outPath =')[0]
setup=setup.replace('$rootPath = Split-Path -Parent $PSScriptRoot', "$rootPath = '"+str(root)+"'")
setup += '''
& "$vc64\\bin\\amd64\\cl.exe" /nologo /EHsc /MD qa/runtime_races/test.cpp /Foqa/runtime_races/test.obj /Feqa/runtime_races/test.exe /link kernel32.lib
if ($LASTEXITCODE -ne 0) { throw 'Compile failed' }
& ./qa/runtime_races/test.exe
if ($LASTEXITCODE -ne 0) { throw 'Test failed' }
'''
(out/'run.ps1').write_text(setup,encoding='utf-8-sig')
result=subprocess.run(['pwsh','-NoProfile','-File',str(out/'run.ps1')],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(out/'test.log').write_bytes(result.stdout)
print(result.stdout.decode('utf-8',errors='replace'));result.check_returncode()
(out/'results.json').write_text(json.dumps({'passed':True,'actual_source_tested':True,'game_database_mocked':True,'gameplay_tested':False,'subset_sizes':list(range(60))},indent=2))
