#include "Logger.h"
#include "Config.h"

#include <iostream>
#include <chrono>
#include <iomanip>

static std::string nowIso8601()
{
    using clock = std::chrono::system_clock;
    auto now = clock::now();
    std::time_t t = clock::to_time_t(now);
    auto tm = *std::gmtime(&t);
    char buffer[64];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &tm);
    return buffer;
}

static std::string csvEscape(const std::string& s)
{
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
        if (c == '"') out += '"';
        out += c;
    }
    return out;
}

static std::string jsonEscape(const std::string& s)
{
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c; break;
        }
    }
    return out;
}

Logger::Logger(const Config& config)
{
    _logToCsv = config.logCsv;
    _logToNdjson = config.logNdjson;

    if (_logToCsv) {
        _csv.emplace(config.csvPath);
        *_csv << "timestamp,source,name,value" << std::endl;
    }
    if (_logToNdjson) {
        _ndjson.emplace(config.ndjsonPath);
    }
}

Logger::~Logger()
{
    flush();
}

void Logger::info(const std::string& message)
{
    std::lock_guard<std::mutex> lock(_mutex);
    std::cout << "[INFO] " << message << std::endl;
}

void Logger::warn(const std::string& message)
{
    std::lock_guard<std::mutex> lock(_mutex);
    std::cout << "[WARN] " << message << std::endl;
}

void Logger::error(const std::string& message)
{
    std::lock_guard<std::mutex> lock(_mutex);
    std::cerr << "[ERROR] " << message << std::endl;
}

void Logger::logValue(const std::string& source,
                      const std::string& name,
                      const std::string& valueString)
{
    std::lock_guard<std::mutex> lock(_mutex);
    std::string ts = nowIso8601();
    std::cout << "[" << ts << "] " << source << ": " << name << "=" << valueString << std::endl;
    if (_csv) {
        *_csv << '"' << csvEscape(ts) << '"' << ','
              << '"' << csvEscape(source) << '"' << ','
              << '"' << csvEscape(name) << '"' << ','
              << '"' << csvEscape(valueString) << '"' << std::endl;
    }
    if (_ndjson) {
        *_ndjson << "{\"ts\":\"" << jsonEscape(ts) << "\",\"source\":\"" << jsonEscape(source)
                 << "\",\"name\":\"" << jsonEscape(name) << "\",\"value\":\"" << jsonEscape(valueString) << "\"}" << std::endl;
    }
}

void Logger::flush()
{
    std::lock_guard<std::mutex> lock(_mutex);
    if (_csv) _csv->flush();
    if (_ndjson) _ndjson->flush();
}

