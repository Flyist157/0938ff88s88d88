## FSX:SE Var Monitor (SimConnect + FSUIPC)

This tool monitors configured SimConnect variables and FSUIPC offsets and logs changes to console and files (CSV/NDJSON).

Currently includes stubs for non-Windows builds. To actually connect to FSX:SE, build on Windows with the SimConnect SDK (and FSUIPC client SDK) installed.

### Requirements (Windows)

- Visual Studio 2019+ with CMake support, or CMake + MSVC Build Tools
- SimConnect SDK (from FSX SDK or P3D SDK)
  - Set `SIMCONNECT_SDK_DIR` to the SDK root containing `include/` and `lib/`.
- FSUIPC (registered) and FSUIPC Client SDK (headers/libs) if using FSUIPC monitoring

### Build

Using CMake GUI or command line:

```bash
cmake -S . -B build -DSIMCONNECT_SDK_DIR="C:/Path/To/SimConnectSDK"
cmake --build build --config Release
```

### Run

Place `config.txt` alongside the executable, or pass a path:

```bash
build/Release/fsx_monitor.exe config.txt
```

Press Ctrl+C to exit. Output goes to console and `fsx_monitor.csv` by default.

### Config format

Simple key=value lines:

- `CSV=path` enables CSV output
- `NDJSON=path` enables NDJSON line-delimited JSON output
- `SIMVAR=name|unit|datum` adds a SimConnect variable
- `FSUIPC=offset_hex|size|name|type` adds an FSUIPC offset

See `config.txt` for examples.

### Notes

- The current code includes stubs for SimConnect and FSUIPC; replace with real SDK calls inside `src/SimConnectMonitor.cpp` and `src/FSUIPCMonitor.cpp` where indicated.
- Ensure FSX:SE is running before starting the monitor.

