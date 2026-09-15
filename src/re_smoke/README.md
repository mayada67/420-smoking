# 420 Smoking RE_Kenshi extension — experimental

This optional overlay uses the existing 420_Smoking items, furniture and animation IDs. Load 420_Smoking_RE after 420_Smoking. Disable the overlay to restore the vanilla static tip meshes; do not enable the overlay without RE_Kenshi.

The DLL emits billboard smoke only for 420_smoke_chillum and 420_smoke_joint. Mouth emission is restricted to animation seconds [8,11). Tip emission continues while those animations are active. Existing puffs fade over 1.8 / 2.5 seconds. State is transient and is cleared on world reset. Other animations are ignored.

The game-provided kenshi_smoke1 alpha-blended material is cloned at runtime; no original game texture or shader is redistributed. The output is a first implementation, not a claim of verified visual quality. Bone offsets, frame timing at accelerated speed, visibility and reset behavior require game QA.

2026-09-15 QA: the installed axis-corrected DLL was verified in Kenshi 1.0.65 with a human male using the chillum. Forward mouth smoke and rising tip smoke were visible. Normal-speed animation samples advanced at approximately real time. Joint visuals, other bodies, accelerated speed, interruption and world-reset behavior remain unverified. See qa/checkpoint_2026-09-15.md in the source project.

Build from the project root with tools/build_re_smoke.ps1 after extracting Microsoft Windows SDK 7.1's VC2010 compiler and SDK build components into build/toolchain. Uses the official KenshiLib_Examples_deps includes, Ogre/KenshiLib import libraries and Boost 1.60 headers. Local extraction paths are recorded in the script. Run tools/build_re_smoke_mod.py with Blender's Python to generate the optional FCS overlay.

Source license: GPL-3.0-or-later. KenshiLib and its dependencies retain their own licenses. This project has not modified or rebuilt KenshiLib or RE_Kenshi.

Exhale density update: mouth emission is 24 puffs/second (previously 12), with base size 0.52 (previously 0.45). The 8–11 second emission window and tip smoke settings are unchanged.
