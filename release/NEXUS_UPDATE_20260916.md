# Nexus update — 2026-09-16

Target: https://www.nexusmods.com/kenshi/mods/2173

## 420 Core — 0.1.0-rc2 (Main file)

Improved the visibility of the small smoke trail from chillum and joint tips. Mouth smoke, animations and smoke attachment positions are unchanged.

Tested in Kenshi 1.0.65 with RE_Kenshi 0.3.5 using a male Greenlander and chillum/joint beanbags in an existing test save. Visibility still depends on background, distance and viewing angle; this does not claim validation of every race, body shape or furniture variant.

Close Kenshi before updating. Extract into the Kenshi folder and replace the existing 420 Core files. Requires RE_Kenshi. Keep 420_Smoking before 420_Smoking_RE in the mod order.

File: dist/420_Core_0.1.0-rc2.zip
SHA256: ff0a46b93ff7609e8698e81ebde4b6fa18c34691cf31049e4e5eb05e0d64a886

## 420 Races — 0.1.0-rc3 (Optional file)

Fixed a loading-order issue that prevented runtime race animation registrations from being applied. The plugin now loads before game-data post-processing. The race plugin DLL and bundled race list are unchanged.

Startup tests confirmed zero registrations without supported race mods and two registrations with the installed 2B mod. This validates registration timing, not visual fitting for every supported race.

Close Kenshi before updating and back up any custom Races.json edits. Replace mods/420_Races, restore your custom entries if needed, and restart Kenshi. Load 420_Races after 420 Core and your race mods. To stop the preload DLL from loading entirely, move the 420_Races folder outside mods while Kenshi is closed; disabling the MOD alone stops registrations because its animation definitions are absent.

File: dist/420_Races_0.1.0-rc3.zip
SHA256: ebc57cddd0d194c257de88e50e47fc78b3d97ae8cb685f33fa2e25d255c9373d

## Source

https://github.com/mayada67/420-smoking/tree/c1257bd

Both archives include source. These fixes do not claim to resolve unrelated crashes in heavily modded saves.

## Publication status

Uploaded on 2026-09-16 as dayama74b. Public Files page verified:
- Core rc2: file ID 6166, Main / Primary; mod page version updated to 0.1.0-rc2.
- Races rc3: file ID 6167, Optional.
- Previous files 6153 and 6158 archived through the update workflow.
- Per-file descriptions and changelogs saved.
- Both new files were undergoing Nexus virus scanning and unavailable for download at verification time. Scan clearance is not yet confirmed.
