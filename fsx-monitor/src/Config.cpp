#include "Config.h"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <cctype>

static std::string trim(const std::string& s)
{
    size_t start = 0;
    while (start < s.size() && std::isspace(static_cast<unsigned char>(s[start]))) start++;
    size_t end = s.size();
    while (end > start && std::isspace(static_cast<unsigned char>(s[end - 1]))) end--;
    return s.substr(start, end - start);
}

// Very simple config format:
// Lines starting with '#' are comments
// CSV-like directives:
// CSV=path/to/file.csv
// NDJSON=path/to/file.ndjson
// SIMVAR=name|unit|datum
// FSUIPC=offset_hex|size|name|type

Config Config::loadFromFile(const std::string& path)
{
    Config cfg;
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("Failed to open config file: " + path);
    }
    std::string line;
    int defId = 1;
    while (std::getline(in, line)) {
        line = trim(line);
        if (line.empty() || line[0] == '#') continue;
        auto pos = line.find('=');
        if (pos == std::string::npos) continue;
        std::string key = trim(line.substr(0, pos));
        std::string value = trim(line.substr(pos + 1));
        if (key == "CSV") {
            cfg.csvPath = value;
            cfg.logCsv = true;
        } else if (key == "NDJSON") {
            cfg.ndjsonPath = value;
            cfg.logNdjson = true;
        } else if (key == "SIMVAR") {
            // name|unit|datum
            std::stringstream ss(value);
            std::string name, unit, datum;
            std::getline(ss, name, '|');
            std::getline(ss, unit, '|');
            std::getline(ss, datum, '|');
            SimVarConfig s{trim(name), trim(unit), trim(datum), defId++};
            cfg.simVars.push_back(s);
        } else if (key == "FSUIPC") {
            // offset_hex|size|name|type
            std::stringstream ss(value);
            std::string offsetHex, sizeStr, name, type;
            std::getline(ss, offsetHex, '|');
            std::getline(ss, sizeStr, '|');
            std::getline(ss, name, '|');
            std::getline(ss, type, '|');
            unsigned int offset = std::stoul(offsetHex, nullptr, 16);
            unsigned int size = static_cast<unsigned int>(std::stoul(sizeStr));
            FsuipcOffsetConfig f{offset, size, trim(name), trim(type)};
            cfg.fsuipcOffsets.push_back(f);
        }
    }
    return cfg;
}

