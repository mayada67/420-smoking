# Chair operator direction correction

- User requested a 90-degree left turn for the original Chillum Seat and Joint Seat occupants.
- Changed only operator rotations on records 23/24 to Y-axis +90 degrees, quaternion (w,x,y,z) = (sqrt(0.5),0,sqrt(0.5),0).
- Binary comparison against both the previous build and installed mod confirmed these are the only changes. Beanbag records, positions, meshes, animations and all other data are unchanged.
- Build readback, reference validation and research unlock checks passed.
- Backups: `qa/chair_direction_20260918/build.before.mod` and `installed.before.mod`.
- Installed corrected `420_Smoking.mod` in the local Steam Kenshi mods directory. Built and installed SHA-256: `A185249FACF7DFA0944DAFECF5D8F0D4D6768162EA78446C59E3039CA23A4D1D`.
- In-game visual verification remains pending after restarting Kenshi.
