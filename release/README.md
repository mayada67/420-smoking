# 420 Smoking — RE_Kenshi

Adds chillum and joint smoking seats, worn beanbag seats, hemp paper and joint crafting, dedicated storage, and animated mouth/tip smoke. No stat buffs or debuffs.

## September 18 update — Core 0.1.0-rc3

- Corrected the seated character's facing direction on both original smoking chairs. The user confirmed the direction in game.
- Increased the interaction radius from 0.5 to 1.5 for all four smoking seats to address intermittent immediate standing after manual seating. This is a mitigation; repeated in-game seating and position checks remain pending.
- Retains the previous tip-smoke visibility improvement. Existing furniture IDs, materials and animations are unchanged by this update.

Close Kenshi before replacing the two Core mod folders, then restart. The optional 420 Races add-on remains at 0.1.0-rc3; its version is independent of Core.

## Install

Tested engine environment: Kenshi 1.0.65 with RE_Kenshi 0.3.5. Install RE_Kenshi separately using its own instructions.

1. Copy the archive's `mods/420_Smoking` and `mods/420_Smoking_RE` folders into your Kenshi `mods` folder.
2. Enable `420_Smoking`, then `420_Smoking_RE`, in that order.
3. Restart Kenshi. The smoke requires RE_Kenshi and the second mod, including its `RE_Kenshi.json` and `SmokingSmoke.dll`.

## Play

- Research **420 Smoking** in Crafting: research level **3**, **3 Books + 3 hemp**, base research time **4 game hours** (actual time depends on research speed).
- Build the workbench and seats from **420 SMOKING**. Dedicated paper/joint containers appear under **STORAGE**. Use an owned building indoors.
- At **420 Smoking Workbench**, queue Hemp Paper first (1 hemp), then Joint (1 hemp + 1 Hemp Paper).
- Place 1 hashish in a Chillum Seat or Chillum Beanbag, or 1 Joint in a Joint Seat/Beanbag; assign one character. The seat is a continuous smoking interaction without routine refills.
- Mouth smoke runs during the exhale portion of the animation; light tip smoke continues while smoking. Moving away interrupts the interaction.

## Characters and compatibility

Animation registrations in Core cover vanilla humanoid races: Greenlander, Scorchlander, Shek, the three Hive castes, Skeletons, and their vanilla humanoid NPC variants. Male and female animation files are included. Custom mod races require the separate 420 Races add-on and a supported registration. Animals are outside this scope. Skeleton smoking is a cosmetic interaction too.

This is a release candidate. Users have confirmed the tested beanbag fit, crafting/storage behavior, joint and female displays, and interruption/load behavior in prior sessions. Static bone/reference checks cover the registered animations, but visual fitting across every race and body slider combination has not been verified. The September 18 immediate-standing mitigation still needs in-game confirmation. Many simultaneous smokers have not been performance-tested.

Existing mod filenames and record IDs are retained. Already completed research remains completed. Existing legacy workbenches remain usable. Back up saves before changing a mod setup. Disable test-start mods such as `420_QA` for normal play; they are not included here.

For uninstalling, use a save from before installation for a clean return to an unmodified setup. Avoid uninstalling while characters are using the furniture.

## Contents and credits

The main archive contains the two runtime mods, this guide, and the smoke plugin source, build script and GPL license. RE_Kenshi, KenshiLib, compiler binaries, game textures and game base data are not bundled. The plugin uses the game's smoke material at runtime.

The smoke plugin source is GPL-3.0-or-later; see `source/LICENSE` and `source/BUILD.md`. Original project models/textures/animations have no separate redistribution grant in this candidate; obtain author permission for reuse. Dependency licenses remain with their respective authors.
