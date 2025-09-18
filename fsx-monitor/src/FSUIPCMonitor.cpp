#include "FSUIPCMonitor.h"
#include "Logger.h"
#include "Config.h"

#if defined(_WIN32) && defined(FSUIPC_CLIENT_ENABLED)
#  include <Windows.h>
#  include "FSUIPC_User.h"
#endif

#include <unordered_map>
#include <sstream>

FSUIPCMonitor::FSUIPCMonitor(Logger& logger, const Config& config)
    : _logger(logger), _config(config)
{
}

FSUIPCMonitor::~FSUIPCMonitor() = default;

void FSUIPCMonitor::start()
{
#if defined(_WIN32) && defined(FSUIPC_CLIENT_ENABLED)
    DWORD dwResult = 0;
    if (!FSUIPC_Open(SIM_ANY, &dwResult)) {
        _logger.error("FSUIPC_Open failed: code " + std::to_string(dwResult));
    } else {
        _logger.info("FSUIPC connected.");
    }
#else
    _logger.warn("FSUIPC disabled or not on Windows; running stub.");
#endif
    _started = true;
}

void FSUIPCMonitor::pump()
{
    if (!_started) return;
#if defined(_WIN32) && defined(FSUIPC_CLIENT_ENABLED)
    DWORD dwResult = 0;
    // We'll read each configured offset sequentially and process in one call
    std::unordered_map<unsigned int, std::string> valueByOffset;
    for (const auto& off : _config.fsuipcOffsets) {
        unsigned char buffer[8] = {0};
        if (!FSUIPC_Read(off.offset, off.size, buffer, &dwResult)) {
            continue;
        }
        if (!FSUIPC_Process(&dwResult)) {
            continue;
        }
        std::ostringstream oss;
        oss.setf(std::ios::fixed);
        if (off.type == "i16" && off.size >= 2) {
            short v = *reinterpret_cast<short*>(buffer);
            oss << v;
        } else if (off.type == "u16" && off.size >= 2) {
            unsigned short v = *reinterpret_cast<unsigned short*>(buffer);
            oss << v;
        } else if (off.type == "i32" && off.size >= 4) {
            int v = *reinterpret_cast<int*>(buffer);
            oss << v;
        } else if (off.type == "u32" && off.size >= 4) {
            unsigned int v = *reinterpret_cast<unsigned int*>(buffer);
            oss << v;
        } else if (off.type == "f32" && off.size >= 4) {
            float v = *reinterpret_cast<float*>(buffer);
            oss.precision(6);
            oss << v;
        } else if (off.type == "f64" && off.size >= 8) {
            double v = *reinterpret_cast<double*>(buffer);
            oss.precision(6);
            oss << v;
        } else {
            // default hex dump
            oss << "0x" << std::hex;
            for (unsigned int i = 0; i < off.size && i < sizeof(buffer); ++i) {
                oss.width(2);
                oss.fill('0');
                oss << static_cast<int>(buffer[i]);
            }
        }
        _logger.logValue("FSUIPC", off.name, oss.str());
    }
#endif
}

void FSUIPCMonitor::stop()
{
    if (!_started) return;
#if defined(_WIN32) && defined(FSUIPC_CLIENT_ENABLED)
    FSUIPC_Close();
    _logger.info("FSUIPC disconnected.");
#endif
    _started = false;
}

