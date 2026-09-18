# Smoke plugin source build

The accompanying `src/re_smoke/SmokingSmoke.cpp` is the exact source of the included SmokingSmoke.dll. `tools/build_re_smoke.ps1` builds the x64 DLL with VC2010 and synchronizes source documentation.

The build expects the following separately obtained dependencies beneath the source root:

- Microsoft Windows SDK 7.1 VC2010 x64 compiler: `build/toolchain/vc10_base/Program Files(64)/Microsoft Visual Studio 10.0/VC`.
- Its headers: `build/toolchain/vc10_base/Program Files/Microsoft Visual Studio 10.0/VC`.
- Windows SDK headers/libraries beneath `build/toolchain/sdk`.
- Official KenshiLib_Examples_deps contents under `build/KenshiLib_Examples_deps`, including KenshiLib headers/import libraries and Boost 1.60.

Run `powershell -ExecutionPolicy Bypass -File tools/build_re_smoke.ps1` from this source root on Windows. Output: `build/420_Smoking_RE/SmokingSmoke.dll`. These third-party dependencies and the game are not redistributed in this archive.

Refer to the upstream projects for dependency acquisition and their licenses. The plugin's own source license is GPL-3.0-or-later. Build instructions describe the locally verified legacy compiler environment, not a guarantee for other compilers.
