#include "SimConnectMonitor.h"
#include "Logger.h"
#include "Config.h"

#include <unordered_map>
#include <sstream>

#if defined(_WIN32) && defined(FSX_SIMCONNECT_ENABLED)
#  include <Windows.h>
#  include <SimConnect.h>
#endif

struct SimConnectMonitor::Impl {
    bool connected{false};
#if defined(_WIN32) && defined(FSX_SIMCONNECT_ENABLED)
    HANDLE hSimConnect{nullptr};
    std::unordered_map<DWORD, std::string> idToName;
    std::unordered_map<DWORD, std::string> lastValueById;
#endif
};

SimConnectMonitor::SimConnectMonitor(Logger& logger, const Config& config)
    : _logger(logger), _config(config), _impl(new Impl())
{
}

SimConnectMonitor::~SimConnectMonitor()
{
    delete _impl;
}

void SimConnectMonitor::start()
{
#if defined(_WIN32) && defined(FSX_SIMCONNECT_ENABLED)
    HRESULT hr = SimConnect_Open(&_impl->hSimConnect, "fsx_monitor", nullptr, 0, 0, 0);
    if (hr != S_OK) {
        _logger.error("SimConnect_Open failed.");
    } else {
        _impl->connected = true;
        for (const auto& var : _config.simVars) {
            // Each var its own definition and request id equal to definitionId
            HRESULT a = SimConnect_AddToDataDefinition(_impl->hSimConnect, var.definitionId, var.name.c_str(), var.unit.c_str(), SIMCONNECT_DATATYPE_FLOAT64);
            if (a != S_OK) {
                _logger.warn("SimConnect_AddToDataDefinition failed for " + var.name);
                continue;
            }
            _impl->idToName[static_cast<DWORD>(var.definitionId)] = var.name;
            HRESULT r = SimConnect_RequestDataOnSimObject(
                _impl->hSimConnect,
                static_cast<DWORD>(var.definitionId),
                static_cast<DWORD>(var.definitionId),
                SIMCONNECT_OBJECT_ID_USER,
                SIMCONNECT_PERIOD_VISUAL_FRAME,
                0
            );
            if (r != S_OK) {
                _logger.warn("SimConnect_RequestDataOnSimObject failed for " + var.name);
            }
        }
        _logger.info("SimConnect initialized.");
    }
#else
    _logger.warn("SimConnect disabled or not on Windows; running stub.");
#endif
    _started = true;
}

void SimConnectMonitor::pump()
{
    if (!_started) return;
#if defined(_WIN32) && defined(FSX_SIMCONNECT_ENABLED)
    if (!_impl->connected || !_impl->hSimConnect) return;
    SIMCONNECT_RECV* pData = nullptr;
    DWORD cbData = 0;
    while (SUCCEEDED(SimConnect_GetNextDispatch(_impl->hSimConnect, &pData, &cbData))) {
        switch (pData->dwID) {
            case SIMCONNECT_RECV_ID_SIMOBJECT_DATA: {
                auto* pObj = reinterpret_cast<SIMCONNECT_RECV_SIMOBJECT_DATA*>(pData);
                DWORD requestId = pObj->dwRequestID;
                auto it = _impl->idToName.find(requestId);
                if (it != _impl->idToName.end()) {
                    const char* raw = reinterpret_cast<const char*>(&pObj->dwData);
                    double value = *reinterpret_cast<const double*>(raw);
                    std::ostringstream oss;
                    oss.setf(std::ios::fixed);
                    oss.precision(6);
                    oss << value;
                    std::string valueStr = oss.str();
                    auto lastIt = _impl->lastValueById.find(requestId);
                    if (lastIt == _impl->lastValueById.end() || lastIt->second != valueStr) {
                        _impl->lastValueById[requestId] = valueStr;
                        _logger.logValue("SimConnect", it->second, valueStr);
                    }
                }
                break;
            }
            case SIMCONNECT_RECV_ID_QUIT:
                _logger.warn("SimConnect reported SIM quit.");
                break;
            default:
                break;
        }
    }
#else
    (void)_config;
#endif
}

void SimConnectMonitor::stop()
{
    if (!_started) return;
#if defined(_WIN32) && defined(FSX_SIMCONNECT_ENABLED)
    if (_impl->hSimConnect) {
        SimConnect_Close(_impl->hSimConnect);
        _impl->hSimConnect = nullptr;
    }
    _impl->connected = false;
#endif
    _started = false;
}

