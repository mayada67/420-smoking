# 420 Races

One optional RE_Kenshi add-on for 420 Smoking. Includes configuration for 59 humanoid race IDs from 17 race mods. Only races present in the loaded game database are patched; absent and unlisted races are not created or modified.

## Install

1. Install 420 Core and RE_Kenshi. Close Kenshi.
2. Copy `mods/420_Races` into your Kenshi `mods` folder.
3. Enable `420_Races` after `420_Smoking`, `420_Smoking_RE`, and your race mods. Restart Kenshi.

You do not need to install all supported race mods. No installer or individual race-patch selection is required.

**Upgrading from the individual patch pack:** disable the old `420_Smoking_Patch_*` entries. Do not run both versions together. Keep a backup of your saves and load order when changing your mod setup.

## How it works

The MOD contains six animation definitions and **zero race records**. `SmokingRaces.dll` hooks game-data post-processing and looks up configured race IDs in the loaded database. It adds the two smoking animation references only when the race and both animation definitions exist, and checks for duplicates. It never creates a race, writes a save, or edits an original mod file. Stats, appearance, names and existing animation references are not changed.

If the hook cannot be installed or the configuration is invalid, this add-on applies no patches and logs an error. Missing races and missing animation definitions are skipped. The smoke renderer in 420 Core is separate.

## Extend the patch

For unsupported races, please refer to the included extension guide. Custom additions require your own testing and troubleshooting. A custom skeleton may need new animations; adding an ID alone does not guarantee compatibility.

### Find the record and choose a profile

1. Close Kenshi and back up `Races.json` outside the mod folder.
2. Open the race's original mod in FCS and locate its RACE record. Read its string ID and copy it exactly. Do not rename or save changes to the original record. A display name, Steam Workshop ID, and MOD filename alone are not a race string ID.
3. Inspect the male and female mesh/skeleton references. Match both slots to the table below. If the references are missing or the skeleton is custom, leave the race out until its author or an animation test confirms compatibility. A humanoid appearance alone is insufficient.

Edit `Races.json` beside `SmokingRaces.dll`, then restart the game. Add an entry to the `races` array:

```json
{"id": "12345-MyRace.mod", "profile": "male_female"}
```

Use the race record's exact FCS string ID, not its display name or Workshop number. Choose the skeleton profile used by its male and female mesh slots:

| Profile | Male slot | Female slot |
|---|---|---|
| `male_female` | Standard male skeleton | Standard female skeleton |
| `male_male` | Standard male skeleton | Standard male skeleton |
| `female_female` | Standard female skeleton | Standard female skeleton |

These are skeleton choices, not assumptions about the character's sex. For example, both 2B slots use the female skeleton profile. Animals, mechanical beasts and incompatible skeletons should not be added. New profiles require animation assets and a code update.

Keep valid JSON, version `1`, and unique IDs. Unknown profiles, duplicate IDs, malformed JSON or a missing file disable this add-on's registration with an error log. To share an extension, share the updated configuration or its added entries; no DLL rebuild is needed. Keep a copy of your custom configuration before updating this add-on, since replacing the folder may overwrite it.

### Edit, test and undo

Add a comma between entries, but never after the last entry. Save as UTF-8. This is a complete example for a configuration containing just one custom race; normally add its entry to the existing list to retain bundled coverage:

```json
{
  "version": 1,
  "races": [
    {"id": "12345-MyRace.mod", "profile": "male_female"}
  ]
}
```

The ID above is a placeholder. Replace it with the real record ID. Change one entry at a time. Restart Kenshi and test the affected race in a disposable session, including both available mesh slots, standing and reclining poses, chillum and joint, and smoke placement. Keep your normal save untouched until satisfied.

- No effect: confirm that the original race mod, 420 Core and `420_Races` are enabled; verify the exact ID and inspect RE_Kenshi logs for `420 Races` messages. A skipped race does not prove skeleton compatibility.
- Configuration rejected: restore the backup, or correct JSON punctuation, duplicate IDs and profile spelling, then restart. One invalid entry rejects the whole configuration.
- Distorted pose or misplaced prop: remove your added entry or restore the backup and restart. Do not guess a profile from the race's display name.
- Remove the add-on: close Kenshi, disable `420_Races`, and move its folder out of `mods`. This stops its runtime additions on the next launch. Restore your saved load order if needed.

## Validation and limits

Built for the local Kenshi 1.0.65 / RE_Kenshi 0.3.5 environment. The actual registration code was tested with a simulated database for zero originals, 59 subset sizes, repeated calls, unsupported races, missing animation definitions, wrong record types, injected exceptions, configuration errors and a user-added race. The shipped MOD was read back and contains no race records. Bundled IDs and skeleton profiles were checked against locally installed originals.

The rc2 loader configuration used `Plugins`, which installed the hook after game-data post-processing and did not apply race registrations in the tested game. The corrected configuration uses `PreloadPlugins`. Startup tests on 2026-09-16 confirmed zero registrations with no supported race mods and two registrations with the installed 2B mod. These logs verify registration timing, not visual fitting across all supported races. Test standing and reclined chillum/joint actions on a disposable session before using an extended configuration. Extreme body proportions and other animation mods may affect results. Skeleton JRPG retains its existing provisional coverage; its female mesh reference is unresolved locally and visual fitting is unverified.

RE_Kenshi loads preload DLLs even when their MOD is disabled in the launcher. Registration still requires the animation definitions from the enabled `420_Races.mod`; without them the plugin skips the races. To stop loading the DLL entirely, close Kenshi and move the `420_Races` folder outside `mods`.

Plugin source is GPL-3.0-or-later; see `source/LICENSE`. Original race mods, RE_Kenshi and compiler/dependency binaries are not bundled.
