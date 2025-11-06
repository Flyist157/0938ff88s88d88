## Installation

1. **Prerequisites**
   - Windows 10/11 with Microsoft Flight Simulator X (Acceleration Pack recommended).
   - Visual Studio 2022 (Desktop development with C++ and .NET workload) or MSBuild with the .NET Framework 4.8 targeting pack.
   - Microsoft Flight Simulator X SDK (for the SimConnect managed library). Install from the Deluxe/Acceleration media or legacy downloads.

2. **SimConnect managed assembly**
   - Copy `Microsoft.FlightSimulator.SimConnect.dll` from the SDK into `lib/` at the repository root.
   - Ensure the DLL's *Copy Local* property is set to `true` inside the project so it ships alongside the executable.

3. **Build steps**
   - Open `src/FsxSafetyAdvisor.sln` in Visual Studio.
   - Restore NuGet packages (none required beyond the framework; the solution uses only in-box assemblies).
   - Build the solution in `Release` mode to produce `bin/Release/FsxSafetyAdvisor.exe`.

4. **Deploy**
   - Copy the compiled `FsxSafetyAdvisor.exe`, the `Microsoft.FlightSimulator.SimConnect.dll`, and the contents of `data/` into a directory on the simulator PC.
   - (Optional) Create a desktop shortcut for quick launch.

5. **Configure SimConnect**
   - Ensure `SimConnect.xml` on the FSX PC allows local clients (default). For networked setups create a matching `SimConnect.cfg` as documented in the FSX SDK.

6. **Run**
   - Launch FSX and load a flight.
   - Start `FsxSafetyAdvisor.exe` once the aircraft is on the runway or at the gate.
   - The advisor will announce readiness and begin monitoring immediately.
