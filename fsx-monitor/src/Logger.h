#pragma once

#include <string>
#include <fstream>
#include <mutex>
#include <unordered_map>
#include <optional>

class Config;

class Logger {
public:
    explicit Logger(const Config& config);
    ~Logger();

    void info(const std::string& message);
    void warn(const std::string& message);
    void error(const std::string& message);

    void logValue(const std::string& source,
                  const std::string& name,
                  const std::string& valueString);

    void flush();

private:
    std::mutex _mutex;
    bool _logToCsv;
    bool _logToNdjson;
    std::optional<std::ofstream> _csv;
    std::optional<std::ofstream> _ndjson;
};

