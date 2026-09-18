# 420 QA vanilla building unlock fix

User reported missing vanilla building menu entries and confirmed the save was
created with the 420 QA start.

The QA start supplied only `30-420_Smoking.mod` in its explicit starting research
list, omitting vanilla `5359-gamedata.base` (`_Default Start`). The corrected start
includes both. A QA-only additive override also attaches the default research's
11 building unlocks and 1 item unlock to the already-completed Smoking research,
to cover existing QA saves without editing save files.

Production research costs and vanilla records are unchanged. This restores
standard starting construction; it does not grant every later-game research.

Validation: `tools/build_qa_start.py` binary readback/reference checks and
`tools/check_qa_building_unlock.py` merged-data regression checks passed.
The installed `mods/420_QA/420_QA.mod` was backed up to
`qa/vanilla_building_fix_20260918/420_QA.before.mod` and replaced. Installed and
built SHA-256: `416B5968ED9B645F1B43DB0D8CF6CAC54A991A3B1DC807B4B6F88707210CC4D8`.

Game restart and existing-save building menu verification remain pending.
Keep 420_QA enabled when testing the existing-save repair. No save was modified.
