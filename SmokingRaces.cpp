// SPDX-License-Identifier: GPL-3.0-or-later
#include <kenshi/GameDataManager.h>
#include <kenshi/GameData.h>
#include <core/Functions.h>
#include <Debug.h>
#include <exception>
#include <sstream>
#include <fstream>
#include <Windows.h>
#include "RacePatchLogic.h"
#include "RacePatchConfig.h"

namespace {
char moduleAnchor;
std::vector<ConfiguredRace> configuredRaces;
bool configurationReady = false;
void loadConfiguration() {
    HMODULE module = 0;
    if (!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
        reinterpret_cast<LPCWSTR>(&moduleAnchor), &module)) throw std::runtime_error("Plugin path unavailable");
    wchar_t path[32768];
    const DWORD length = GetModuleFileNameW(module, path, 32768);
    if (!length || length >= 32768) throw std::runtime_error("Plugin path too long");
    const std::wstring full(path, length);
    const size_t slash = full.find_last_of(L"\\/");
    if (slash == std::wstring::npos) throw std::runtime_error("Plugin directory unavailable");
    std::ifstream input((full.substr(0, slash + 1) + L"Races.json").c_str(), std::ios::binary);
    if (!input) throw std::runtime_error("Races.json missing beside SmokingRaces.dll");
    configuredRaces = readRaceConfiguration(input);
    configurationReady = true;
}
struct GameBackend {
    GameDataManager* database;
    explicit GameBackend(GameDataManager* value) : database(value) {}
    bool hasRace(const char* id) {
        GameData* item = database->getData(std::string(id), RACE);
        return item && item->type == RACE;
    }
    bool hasAnimation(const char* id) {
        GameData* item = database->getData(std::string(id), ANIMATION_FILE);
        return item && item->type == ANIMATION_FILE;
    }
    void addIfMissing(const char* raceId, const char* animationId) {
        GameData* race = database->getData(std::string(raceId), RACE);
        if (race && !race->findInList("animation files", animationId))
            race->addToList("animation files", animationId, 0, 0, 0);
    }
};
void (*originalPostProcess)(GameDataManager*) = 0;
void postProcessHook(GameDataManager* database) {
    // All mod records are available, but runtime race/animation caches have not
    // been built by this post-processing pass. Never save or create race data.
    try {
        if (database && configurationReady) {
            GameBackend backend(database);
            unsigned count = 0;
            for (size_t i = 0; i < configuredRaces.size(); ++i) {
                const ConfiguredRace& row = configuredRaces[i];
                RacePatchEntry entry = {row.id.c_str(), row.standing.c_str(), row.reclining.c_str()};
                count += applyRacePatches(backend, &entry, 1);
            }
            std::ostringstream message;
            message << "420 Races: applied to " << count
                << " existing supported races; absent races skipped";
            DebugLog(message.str());
        }
    } catch (const std::exception& error) {
        ErrorLog(std::string("420 Races: registration failed: ") + error.what());
    }
    originalPostProcess(database);
}
}

__declspec(dllexport) void startPlugin() {
    try { loadConfiguration(); }
    catch (const std::exception& error) {
        ErrorLog(std::string("420 Races: configuration rejected; no changes applied: ") + error.what());
        return;
    }
    if (KenshiLib::AddHook(KenshiLib::GetRealAddress(&GameDataManager::postProcessingTheDatas),
        &postProcessHook, &originalPostProcess) != KenshiLib::SUCCESS) {
        ErrorLog("420 Races: registration hook unavailable; no race patches applied");
        return;
    }
    DebugLog("420 Races: conditional registration hook installed");
}

