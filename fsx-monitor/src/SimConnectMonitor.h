#pragma once

#include <vector>
#include <string>
#include <unordered_map>

class Logger;
struct Config;

class SimConnectMonitor {
public:
    SimConnectMonitor(Logger& logger, const Config& config);
    ~SimConnectMonitor();

    void start();
    void pump();
    void stop();

private:
    Logger& _logger;
    const Config& _config;
    bool _started{false};

    struct Impl;
    Impl* _impl; // opaque to avoid including SimConnect headers on non-Win
};

