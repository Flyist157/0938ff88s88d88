## Usage

1. Launch Microsoft Flight Simulator X and load the desired aircraft/scenario.
2. Start `FsxSafetyAdvisor.exe`.
3. Wait for the console message “SimConnect connection established” and the spoken confirmation.
4. Fly normally. When the advisor detects a hazardous trend it will:
   - Log the advisory headline in the console.
   - Speak a concise warning and the first three steps of the relevant checklist.
5. To exit, close the console window or press `Ctrl+C`. The advisor will disconnect cleanly from SimConnect.

### Configuration
- **Voice**: Edit `SpeechService.ConfigureVoice` to specify a preferred installed Windows TTS voice.
- **Rule Cooldowns**: Adjust per-rule suppression windows in the rule constructors to change how frequently advisories repeat.
- **Adding Rules**: Implement `IAdvisoryRule` and register the rule in `SafetyAdvisorApp`. Use `FlightState` and `DerivedMetrics` to access telemetry.
