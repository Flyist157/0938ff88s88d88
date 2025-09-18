#pragma once

#include <string>
#include <fstream>
#include <mutex>
#include <unordered_map>
#include <optional>
#include <vector>

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

    void setDashboardMode(bool enabled);
    void renderDashboard();

private:
    std::mutex _mutex;
    bool _logToCsv;
    bool _logToNdjson;
    bool _dashboardMode{false};
    std::optional<std::ofstream> _csv;
    std::optional<std::ofstream> _ndjson;

    // Latest values by source/name and stable order for display
    std::unordered_map<std::string, std::unordered_map<std::string, std::string>> _latestBySource;
    std::vector<std::pair<std::string, std::string>> _displayOrder;
};

