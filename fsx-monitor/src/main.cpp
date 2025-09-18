#include "Logger.h"
#include "Config.h"
#include "SimConnectMonitor.h"
#include "FSUIPCMonitor.h"

#include <atomic>
#include <csignal>
#include <chrono>
#include <thread>
#include <iostream>

using namespace std::chrono_literals;

static std::atomic<bool> g_shouldExit{false};

void handleSignal(int) {
    g_shouldExit.store(true);
}

int main(int argc, char** argv) {
    std::signal(SIGINT, handleSignal);
#ifdef _WIN32
    std::signal(SIGBREAK, handleSignal);
#endif

    std::string configPath = argc > 1 ? argv[1] : "config.txt";

    try {
        Config config = Config::loadFromFile(configPath);
        Logger logger{config};

        SimConnectMonitor simMonitor{logger, config};
        FSUIPCMonitor fsuipcMonitor{logger, config};

        simMonitor.start();
        fsuipcMonitor.start();

        logger.info("FSX monitor running. Press Ctrl+C to exit.");

        while (!g_shouldExit.load()) {
            simMonitor.pump();
            fsuipcMonitor.pump();
            std::this_thread::sleep_for(10ms);
        }

        logger.info("Shutting down...");
        simMonitor.stop();
        fsuipcMonitor.stop();

        logger.flush();
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << std::endl;
        return 1;
    }
}

