# 420 Smoking - RE_Kenshi

Give your squad a place to sit back between trips through the wasteland. Adds chillum and joint smoking seats, worn beanbags, hemp paper and joint crafting, dedicated storage, and animated mouth and tip smoke through RE_Kenshi. Cosmetic interactions only: no stat buffs or debuffs.

## Features

- Four smoking interactions: chillum or joint, on a regular seat or a reclined beanbag.
- Male and female animations for vanilla humanoid races.
- Animated exhaled smoke and light smoke from the tip.
- A shared workbench for hemp paper and joints, plus dedicated storage.
- One optional compatibility add-on for 59 humanoid race IDs across 17 locally checked race mods.

## Downloads

**420_Core.zip — Main file.** Includes 420_Smoking, 420_Smoking_RE, installation instructions, and smoke plugin source with its GPL license.

**420_Races.zip — Optional file (0.1.0-rc2).** One folder, with explicit runtime skipping of absent races. Requires 420 Core and RE_Kenshi. Replaces the individual patch pack. Disable old `420_Smoking_Patch_*` entries when upgrading.

## Requirements and installation

The smoke plugin requires RE_Kenshi, installed separately. Tested engine environment: Kenshi 1.0.65 with RE_Kenshi 0.3.5.

1. Extract 420_Core.zip.
2. Copy `mods/420_Smoking` and `mods/420_Smoking_RE` into your Kenshi `mods` folder.
3. Enable `420_Smoking`, then `420_Smoking_RE`, in that order.
4. Restart Kenshi. Keep `RE_Kenshi.json` and `SmokingSmoke.dll` inside the smoke mod folder.

For the optional add-on, copy `mods/420_Races` into `Kenshi/mods`. Enable it after your race mods, `420_Smoking`, and `420_Smoking_RE`. Keep its DLL and JSON files together. You do not need every supported race mod. Original race mods and their assets are not included.

The add-on MOD contains six animation definitions and zero race records. Its plugin looks up each configured race and both animations before adding missing references; absent and unlisted races are skipped explicitly. It does not create races or edit original mod files. Extend `Races.json` with exact FCS string IDs and one of three skeleton profiles, without rebuilding the DLL. The included English guide covers choosing profiles, JSON examples, testing and rollback. Invalid configuration rejects all registration; back up custom entries before updating.

## How to play

For unsupported races, please refer to the included extension guide. Custom additions require your own testing and troubleshooting. A custom skeleton may need new animations; adding an ID alone does not guarantee compatibility.

Research **420 Smoking** in Crafting: research level 3, 3 Books + 3 hemp, and 4 base game hours. Actual time depends on research speed.

Build the workbench and seats under **420 SMOKING**; dedicated containers appear under **STORAGE**. Place the furniture indoors in an owned building.

At the **420 Smoking Workbench**, craft Hemp Paper using 1 hemp, then craft a Joint using 1 hemp + 1 Hemp Paper.

Place 1 hashish in a Chillum Seat or Chillum Beanbag, or 1 Joint in a Joint Seat or Joint Beanbag, and assign a character. Smoking is a continuous interaction without routine refills. Moving away interrupts it.

## Compatibility and release status

This is a **release candidate**. Data references, animation timing, skeleton links, archive integrity, and locally installed original race mods have been checked. Previous in-game testing covered smoking, crafting, storage, pause/speed changes, interruption, and save/load.

The included renderer-error cleanup fix passed injected exception tests; its rebuilt DLL has not yet been retested in game. Visual fitting has not been verified for every race, sex, or body-slider combination, and large groups of simultaneous smokers have not been performance-tested.

The new 420 Races registration code passed simulated-database tests for absent races, subsets through all 59 configured races, duplicate prevention, missing animations, invalid configuration and user-added IDs. The new hook has not yet been exercised in a running game: hook timing and visual fitting remain unverified. This is an experimental release candidate, not a claim of full gameplay validation. Source and build instructions are included in the optional download.

Animals and mechanical beasts are excluded. Skeleton smoking is cosmetic. Skeleton JRPG is included in the optional patches; its original female mesh reference is unresolved locally, and that smoking combination has not been visually verified. Users should test other original-mod versions and environments themselves.

Existing record IDs and mod folder names are retained. Completed research remains completed, and existing legacy workbenches remain usable. Disable development starts such as `420_QA` for normal play; they are not included.

Back up your save before changing your mod setup. For a clean uninstall, return to a save from before installation. Avoid uninstalling while characters are using the furniture.

## Credits and permissions

420 Smoking by dayama74b. Thanks to the Kenshi, RE_Kenshi, and KenshiLib developers.

The smoke plugin source is GPL-3.0-or-later; the main file includes the license and build instructions. The original models, textures, and animations have no separate redistribution grant in this release candidate: please obtain author permission for reuse. Third-party dependency licenses remain with their authors. RE_Kenshi, KenshiLib, compiler binaries, game textures, and game base data are not bundled. The plugin uses the game's smoke material at runtime.
