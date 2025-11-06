## FSX Safety Advisor Plug-in

Real-time assistant for Microsoft Flight Simulator X that monitors aircraft telemetry, understands key abnormal situations, and gives clear spoken instructions to prevent pilot-error accidents.

### Features
- Polls SimConnect for instrument readings, control inputs, autopilot status, and warning flags once per second.
- Normalises the raw data into a rich `FlightState` model with derived phase-of-flight cues.
- Evaluates a stack of safety rules (stall detection, gear-up landing prevention, unstable approach monitoring) backed by procedure knowledge.
- Speaks concise callouts and the first actions of the relevant checklist using Windows text-to-speech.

### Architecture Overview
- `SimConnectManager`: resilient connection manager that subscribes to telemetry variables and emits high-level flight states.
- `ProcedureRepository`: loads airline-standard recovery procedures from `data/procedures.json` for reuse by multiple rules.
- `AdvisoryEngine`: runs rule evaluations, handles cooldown logic, and queues advisories for speech output.
- `SpeechService`: manages a background speech synthesizer so advisories never overlap.
- `SafetyAdvisorApp`: bootstraps all services, maintains lifecycle, and exposes a simple console front-end.

### Building
Requires `Microsoft.FlightSimulator.SimConnect.dll` from the FSX SDK in `lib/`. Compile with Visual Studio on Windows following `docs/installation.md`.
