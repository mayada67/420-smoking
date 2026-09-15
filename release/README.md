# 420 Smoking — RE_Kenshi

Adds chillum and joint smoking seats, worn beanbag seats, hemp paper and joint crafting, dedicated storage, and animated mouth/tip smoke. No stat buffs or debuffs.

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

Animation registrations cover vanilla humanoid races: Greenlander, Scorchlander, Shek, the three Hive castes, Skeletons, and their vanilla humanoid NPC variants. Male and female animation files are included. Animals and custom mod races are outside this scope. Skeleton smoking is a cosmetic interaction too.

This is a release candidate. The newly expanded race registrations and female animation exports have passed static bone/reference checks; visual fitting across every race and body slider combination has not been verified. Previously tested smoking behavior is recorded separately in the project. Many simultaneous smokers have not been performance-tested.

Existing mod filenames and record IDs are retained. Already completed research remains completed. Existing legacy workbenches remain usable. Back up saves before changing a mod setup. Disable test-start mods such as `420_QA` for normal play; they are not included here.

For uninstalling, use a save from before installation for a clean return to an unmodified setup. Avoid uninstalling while characters are using the furniture.

## Contents and credits

The main archive contains the two runtime mods, this guide, and the smoke plugin source, build script and GPL license. RE_Kenshi, KenshiLib, compiler binaries, game textures and game base data are not bundled. The plugin uses the game's smoke material at runtime.

The smoke plugin source is GPL-3.0-or-later; see `source/LICENSE` and `source/BUILD.md`. Original project models/textures/animations have no separate redistribution grant in this candidate; obtain author permission for reuse. Dependency licenses remain with their respective authors.

## 日本語の要点

RE_Kenshiを別途導入し、`420_Smoking` → `420_Smoking_RE` の順に有効化してください。研究「420 Smoking」はレベル3、通常の本3冊＋麻3個、基準4ゲーム内時間。屋内に設備を置き、チラム席にはハシシ1個、ジョイント席にはジョイント1個をセットします。紙とジョイントは共通作業台で製作できます。

バニラ人型種族・男女用の登録とファイルを追加しています。今回追加した種族・女性用ファイルの実機での見た目は最終確認前です。
