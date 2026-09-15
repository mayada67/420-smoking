// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <string>
#include <vector>
#include <set>
#include <stdexcept>

struct ConfiguredRace {
    std::string id, standing, reclining;
};

inline std::vector<ConfiguredRace> readRaceConfiguration(std::istream& input) {
    boost::property_tree::ptree document;
    boost::property_tree::read_json(input, document);
    if (document.get<int>("version") != 1) throw std::runtime_error("Unsupported Races.json version");
    std::vector<ConfiguredRace> result;
    std::set<std::string> seen;
    const boost::property_tree::ptree& races = document.get_child("races");
    for (boost::property_tree::ptree::const_iterator it = races.begin(); it != races.end(); ++it) {
        if (result.size() >= 4096) throw std::runtime_error("Too many race entries");
        ConfiguredRace entry;
        entry.id = it->second.get<std::string>("id");
        const std::string profile = it->second.get<std::string>("profile");
        if (entry.id.empty() || entry.id.size() > 256 || entry.id.find_first_of("\r\n\t") != std::string::npos)
            throw std::runtime_error("Invalid race ID");
        if (!seen.insert(entry.id).second) throw std::runtime_error("Duplicate race ID: " + entry.id);
        // Fixed profiles prevent a typo from selecting an unrelated animation.
        if (profile == "female_female") { entry.standing="1-420_Races.mod"; entry.reclining="2-420_Races.mod"; }
        else if (profile == "male_female") { entry.standing="3-420_Races.mod"; entry.reclining="4-420_Races.mod"; }
        else if (profile == "male_male") { entry.standing="5-420_Races.mod"; entry.reclining="6-420_Races.mod"; }
        else throw std::runtime_error("Unknown skeleton profile: " + profile);
        result.push_back(entry);
    }
    return result;
}
