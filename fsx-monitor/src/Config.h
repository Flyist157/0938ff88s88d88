#pragma once

#include <string>
#include <vector>

struct SimVarConfig {
    std::string name;           // e.g. "PLANE ALTITUDE"
    std::string unit;           // e.g. "feet"
    std::string datum;          // e.g. "number"
    int definitionId;           // assigned id
};

struct FsuipcOffsetConfig {
    unsigned int offset;        // e.g. 0x3324
    unsigned int size;          // bytes
    std::string name;           // label
    std::string type;           // e.g. "u16", "i32", "f64"
};

struct Config {
    bool logCsv{true};
    bool logNdjson{false};
    std::string csvPath{"fsx_monitor.csv"};
    std::string ndjsonPath{"fsx_monitor.ndjson"};

    std::vector<SimVarConfig> simVars;
    std::vector<FsuipcOffsetConfig> fsuipcOffsets;

    static Config loadFromFile(const std::string& path);
};

