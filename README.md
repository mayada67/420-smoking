# 420 Smoking - RE_Kenshi plugin source

Source review package for [420 Smoking on Nexus Mods](https://www.nexusmods.com/kenshi/mods/2173), version 0.1.0-rc1.

The five source, documentation and license files are copied byte-for-byte from the source directory inside the uploaded 420_Core.zip. SOURCE_SHA256.json records their original relative paths and hashes. This repository contains no compiled plugin or game assets.

## Read the source

- [SmokingSmoke.cpp](SmokingSmoke.cpp): plugin implementation (GPL-3.0-or-later).
- [build_re_smoke.ps1](build_re_smoke.ps1): original build script.
- [BUILD.md](BUILD.md): dependency paths and build instructions.
- [PLUGIN_README.md](PLUGIN_README.md): plugin behavior and setup.
- [LICENSE](LICENSE): GNU GPL version 3.

## Build with the original directory structure

Extract [source.zip](source.zip) into an empty folder. It restores src/re_smoke/SmokingSmoke.cpp, src/re_smoke/README.md, tools/build_re_smoke.ps1, BUILD.md and LICENSE. Obtain the separately distributed dependencies and place them at the paths listed in BUILD.md. From the extracted root run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_re_smoke.ps1
```

Output: build/420_Smoking_RE/SmokingSmoke.dll. Toolchain: VC2010 x64, Windows SDK 7.1, KenshiLib_Examples_deps and Boost 1.60. Dependencies are not bundled. The files displayed at this repository root are for convenient review; use the archive layout when building.

## Uploaded artifact identification

420_Core.zip SHA256: 794c9fc48b2dbf47a86f667a71710812653661fc0753075be541090ac20d4ccc

SmokingSmoke.dll SHA256: f742e4105472ffd5f9dbab95c772547fd37e610da60794c4f50c2f15d977124e

The source archive is provided for review and rebuilding. Distribution of the compiled mod remains on Nexus Mods and subject to its review process.
