# Build SmokingRaces.dll

This plugin registers smoking animation references only for existing supported races. It does not modify SmokingSmoke.dll.

Use VC2010 x64, Windows SDK 7.1, the official KenshiLib_Examples_deps package and Boost 1.60, as documented in the core plugin's BUILD.md. Place the source files under `src/re_smoke` and the build script under `tools`. Run `tools/build_re_races.ps1` from the source root. The script documents the exact dependency paths and emits `build/420_Races/SmokingRaces.dll`.

`RacePatchLogic.h` contains the conditional lookup and duplicate policy. `RacePatchConfig.h` parses the user-editable configuration. `SmokingRaces.cpp` implements the game adapter, configuration path and hook. `Races.json` is loaded beside the DLL. The game MOD must provide animation records `1-420_Races.mod` through `6-420_Races.mod`.

Use `PreloadPlugins` for `SmokingRaces.dll` in `RE_Kenshi.json`. The normal `Plugins` stage runs after `postProcessingTheDatas` and misses registration. Startup tests on Kenshi 1.0.65 / RE_Kenshi 0.3.5 verified the corrected timing with no supported originals and with 2B (two matching races). The automated registration tests also use a simulated game database. Visual fitting across supported races remains unverified. No compiler or game binaries are redistributed.
