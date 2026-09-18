# 420 Smoking — RE_Kenshi Edition (In Development)

This project targets RE_Kenshi and uses a base mod plus a smoke plugin.

## Installation

1. Install RE_Kenshi. Tested environment: Kenshi 1.0.65 / RE_Kenshi 0.3.5.
2. Copy `build/420_Smoking` and `build/420_Smoking_RE` into the game's `mods` folder.
3. Enable `420_Smoking`, followed by `420_Smoking_RE`, and restart the game.

The smoke mod requires `420_Smoking_RE.mod`, `RE_Kenshi.json`, and `SmokingSmoke.dll`. `420_QA` is a development-only game start.

## Smoke behavior

- Supported animations: `420_smoke_chillum`, `420_smoke_joint`, `420_recline_chillum`, and `420_recline_joint`.
- Mouth smoke appears at seconds 8–11 of the 12-second loop. Tip smoke continues during the interaction.
- Exhaled smoke uses 72 particles per second and a base size of 1.56. The increased setting was confirmed in game by the user; these values do not represent a measured visual multiplier.
- Tip smoke uses 9 particles per second, a base size of 0.30 and peak particle opacity of 0.28. The earlier 3/s, 0.17, 0.08 settings were too subtle in the tested interior. Texture alpha and distance also affect visibility.
- Existing smoke fades out. Temporary state is cleared when the world resets.
- On a rendering error, the plugin attempts to hide and clear the smoke independently, clears its temporary emitters and particles, and disables smoke updates. Game updates continue.
- The base mod works without smoke when the extension is disabled. The static smoke prototype is not used.

The plugin clones the game's `kenshi_smoke1` material at runtime. Original game textures and shaders are not redistributed. The project's `qa/user_confirmation_2026-09-15.md` records the scope of user testing.

## Build

Run `tools/build_re_smoke.ps1` from the project root. It uses the local VC2010 x64 compiler, Windows SDK 7.1, official KenshiLib_Examples_deps, and Boost 1.60. Dependency paths are specified in the script. `tools/build_re_smoke_mod.py` generates the FCS smoke mod.

The canonical source is `src/re_smoke/SmokingSmoke.cpp`.

Source license: GPL-3.0-or-later. KenshiLib and its dependencies retain their own licenses. This project has not modified or rebuilt KenshiLib or RE_Kenshi.
