// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once

struct RacePatchEntry {
    const char* race;
    const char* standing;
    const char* reclining;
};

// Backend lookup must never create an item. Apply only complete, existing pairs.
// Keep this policy independent of the game's file-loader missing-record behavior.
template<class Backend>
unsigned applyRacePatches(Backend& backend, const RacePatchEntry* entries, unsigned count) {
    unsigned matched = 0;
    for (unsigned i = 0; i < count; ++i) {
        const RacePatchEntry& entry = entries[i];
        if (!backend.hasRace(entry.race)) continue;
        if (!backend.hasAnimation(entry.standing) || !backend.hasAnimation(entry.reclining)) continue;
        backend.addIfMissing(entry.race, entry.standing);
        backend.addIfMissing(entry.race, entry.reclining);
        ++matched;
    }
    return matched;
}
