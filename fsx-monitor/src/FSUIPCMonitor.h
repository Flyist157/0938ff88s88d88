#pragma once

class Logger;
struct Config;

class FSUIPCMonitor {
public:
    FSUIPCMonitor(Logger& logger, const Config& config);
    ~FSUIPCMonitor();

    void start();
    void pump();
    void stop();

private:
    Logger& _logger;
    const Config& _config;
    bool _started{false};
};

