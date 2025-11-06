using System;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using FsxSafetyAdvisor.Domain;
using FsxSafetyAdvisor.Infrastructure;
using Microsoft.FlightSimulator.SimConnect;

namespace FsxSafetyAdvisor.Sim;

public sealed class SimConnectManager : IDisposable
{
    private const int SimConnectPollTimeoutMs = 500;

    private readonly AutoResetEvent _simEvent = new(false);
    private readonly ConsoleLogger _logger;

    private SimConnect? _simConnect;
    private Task? _pumpTask;
    private CancellationTokenSource? _internalShutdown;
    private bool _disposed;

    public SimConnectManager(ConsoleLogger logger)
    {
        _logger = logger;
    }

    public event EventHandler? Connected;
    public event EventHandler? Disconnected;
    public event EventHandler<FlightState>? FlightStateUpdated;

    public async Task ConnectAsync(CancellationToken cancellationToken)
    {
        if (_simConnect is not null)
        {
            return;
        }

        _logger.Info("Connecting to Microsoft Flight Simulator X via SimConnect...");
        var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        _internalShutdown = linkedCts;

        while (!linkedCts.IsCancellationRequested)
        {
            try
            {
                _simConnect = new SimConnect(
                    "FSX Safety Advisor",
                    IntPtr.Zero,
                    0,
                    _simEvent.SafeWaitHandle.DangerousGetHandle(),
                    0);

                WireEvents(_simConnect);
                RegisterDataDefinitions(_simConnect);
                RequestInitialData(_simConnect);

                _pumpTask = Task.Run(() => PumpAsync(linkedCts.Token), linkedCts.Token);
                Connected?.Invoke(this, EventArgs.Empty);
                _logger.Info("SimConnect connection established.");
                return;
            }
            catch (COMException)
            {
                _logger.Warn("SimConnect not available yet. Retrying in 5 seconds...");
                await Task.Delay(TimeSpan.FromSeconds(5), linkedCts.Token);
            }
        }
    }

    public async Task DisconnectAsync()
    {
        _internalShutdown?.Cancel();

        if (_pumpTask is not null)
        {
            try
            {
                await _pumpTask.ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                // ignore
            }
        }

        if (_simConnect is not null)
        {
            _simConnect.Dispose();
            _simConnect = null;
            Disconnected?.Invoke(this, EventArgs.Empty);
            _logger.Info("SimConnect disconnected.");
        }
    }

    private void PumpAsync(CancellationToken token)
    {
        try
        {
            while (!token.IsCancellationRequested)
            {
                if (_simEvent.WaitOne(SimConnectPollTimeoutMs))
                {
                    _simConnect?.ReceiveMessage();
                }
            }
        }
        catch (COMException ex)
        {
            _logger.Error("SimConnect pump encountered a COM exception.", ex);
        }
        catch (Exception ex)
        {
            _logger.Error("SimConnect pump exited unexpectedly.", ex);
        }
    }

    private void WireEvents(SimConnect simConnect)
    {
        simConnect.OnRecvOpen += SimConnectOnRecvOpen;
        simConnect.OnRecvQuit += SimConnectOnRecvQuit;
        simConnect.OnRecvException += SimConnectOnRecvException;
        simConnect.OnRecvSimobjectData += SimConnectOnRecvSimobjectData;
    }

    private void RegisterDataDefinitions(SimConnect simConnect)
    {
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AIRSPEED INDICATED", "Knots", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AIRSPEED TRUE", "Knots", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AIRSPEED MACH", "Number", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE ALTITUDE", "Feet", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "RADIO HEIGHT", "Feet", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "VERTICAL SPEED", "Feet per minute", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE PITCH DEGREES", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE BANK DEGREES", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE HEADING DEGREES TRUE", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE LATITUDE", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PLANE LONGITUDE", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "ANGLE OF ATTACK INDICATOR", "Degrees", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "G FORCE", "GForce", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "STALL WARNING", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "OVERSPEED WARNING", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "SIM ON GROUND", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "FLAPS HANDLE INDEX", "Number", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "SPOILERS HANDLE POSITION", "Percent", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "GEAR HANDLE POSITION", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "RUDDER POSITION", "Position", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "ELEVATOR POSITION", "Position", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AILERON POSITION", "Position", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "GENERAL ENG THROTTLE LEVER POSITION:1", "Percent", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "PARKING BRAKE HANDLE POSITION", "Position", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT MASTER", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT HEADING LOCK", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT NAV1 LOCK", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT APPROACH HOLD", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT ALTITUDE LOCK", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AUTOPILOT AIRSPEED HOLD", "Bool", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "TOTAL AIR TEMPERATURE", "Celsius", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);
        simConnect.AddToDataDefinition(DATA_DEFINITION.FlightState, "AMBIENT TEMPERATURE", "Celsius", SIMCONNECT_DATATYPE.FLOAT64, 0.0f, SimConnect.SIMCONNECT_UNUSED);

        simConnect.RegisterDataDefineStruct<AircraftTelemetry>(DATA_DEFINITION.FlightState);
    }

    private void RequestInitialData(SimConnect simConnect)
    {
        simConnect.RequestDataOnSimObject(
            DATA_REQUEST.FlightState,
            DATA_DEFINITION.FlightState,
            SimConnect.SIMCONNECT_OBJECT_ID_USER,
            SIMCONNECT_PERIOD.SECOND,
            SIMCONNECT_DATA_REQUEST_FLAG.DEFAULT,
            0,
            0,
            0);
    }

    private void SimConnectOnRecvSimobjectData(SimConnect sender, SIMCONNECT_RECV_SIMOBJECT_DATA data)
    {
        if ((DATA_REQUEST)data.dwRequestID != DATA_REQUEST.FlightState)
        {
            return;
        }

        if (data.dwData[0] is not AircraftTelemetry telemetry)
        {
            return;
        }

        var state = MapTelemetry(telemetry);
        FlightStateUpdated?.Invoke(this, state);
    }

    private FlightState MapTelemetry(AircraftTelemetry telemetry)
    {
        var controls = new ControlInputs(
            telemetry.ElevatorPosition,
            telemetry.AileronPosition,
            telemetry.RudderPosition,
            telemetry.ThrottleLeverPosition / 100.0,
            telemetry.SpoilersHandlePosition / 100.0);

        var configuration = new AircraftConfiguration(
            telemetry.FlapHandleIndex,
            telemetry.GearHandlePosition,
            telemetry.SpoilersHandlePosition / 100.0,
            telemetry.ParkingBrake >= 0.5);

        var autopilot = new AutopilotState(
            telemetry.AutopilotMaster >= 0.5,
            telemetry.AutopilotHeadingLock >= 0.5,
            telemetry.AutopilotNavLock >= 0.5,
            telemetry.AutopilotApproachHold >= 0.5,
            telemetry.AutopilotAltitudeLock >= 0.5,
            telemetry.AutopilotAirspeedHold >= 0.5);

        var warnings = new WarningFlags(
            telemetry.StallWarning >= 0.5,
            telemetry.OverspeedWarning >= 0.5,
            masterWarning: false,
            masterCaution: false);

        return new FlightState(
            DateTime.UtcNow,
            telemetry.IndicatedAirspeed,
            telemetry.TrueAirspeed,
            telemetry.Mach,
            telemetry.Altitude,
            telemetry.RadioAltitude,
            telemetry.VerticalSpeed,
            telemetry.Pitch,
            telemetry.Bank,
            telemetry.Heading,
            telemetry.AngleOfAttack,
            telemetry.GForce,
            telemetry.OnGround >= 0.5,
            telemetry.Latitude,
            telemetry.Longitude,
            telemetry.TotalAirTemperature,
            telemetry.AmbientAirTemperature,
            controls,
            configuration,
            autopilot,
            warnings);
    }

    private void SimConnectOnRecvException(SimConnect sender, SIMCONNECT_RECV_EXCEPTION data)
    {
        _logger.Error($"SimConnect exception received: {data.dwException} ({data.dwSendID})");
    }

    private async void SimConnectOnRecvQuit(SimConnect sender, SIMCONNECT_RECV eventData)
    {
        _logger.Warn("Simulator closed. Disconnecting SimConnect.");
        await DisconnectAsync().ConfigureAwait(false);
    }

    private void SimConnectOnRecvOpen(SimConnect sender, SIMCONNECT_RECV_OPEN data)
    {
        _logger.Info($"Connected to simulator version {data.dwApplicationBuildMajor}.{data.dwApplicationBuildMinor}.");
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _simConnect?.Dispose();
        _simEvent.Dispose();
        _internalShutdown?.Dispose();
    }

    private enum DATA_DEFINITION
    {
        FlightState = 0
    }

    private enum DATA_REQUEST
    {
        FlightState = 0
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi, Pack = 1)]
    private readonly struct AircraftTelemetry
    {
        public readonly double IndicatedAirspeed;
        public readonly double TrueAirspeed;
        public readonly double Mach;
        public readonly double Altitude;
        public readonly double RadioAltitude;
        public readonly double VerticalSpeed;
        public readonly double Pitch;
        public readonly double Bank;
        public readonly double Heading;
        public readonly double Latitude;
        public readonly double Longitude;
        public readonly double AngleOfAttack;
        public readonly double GForce;
        public readonly double StallWarning;
        public readonly double OverspeedWarning;
        public readonly double OnGround;
        public readonly double FlapHandleIndex;
        public readonly double SpoilersHandlePosition;
        public readonly double GearHandlePosition;
        public readonly double RudderPosition;
        public readonly double ElevatorPosition;
        public readonly double AileronPosition;
        public readonly double ThrottleLeverPosition;
        public readonly double ParkingBrake;
        public readonly double AutopilotMaster;
        public readonly double AutopilotHeadingLock;
        public readonly double AutopilotNavLock;
        public readonly double AutopilotApproachHold;
        public readonly double AutopilotAltitudeLock;
        public readonly double AutopilotAirspeedHold;
        public readonly double TotalAirTemperature;
        public readonly double AmbientAirTemperature;

        public AircraftTelemetry(
            double indicatedAirspeed,
            double trueAirspeed,
            double mach,
            double altitude,
            double radioAltitude,
            double verticalSpeed,
            double pitch,
            double bank,
            double heading,
            double latitude,
            double longitude,
            double angleOfAttack,
            double gForce,
            double stallWarning,
            double overspeedWarning,
            double onGround,
            double flapHandleIndex,
            double spoilersHandlePosition,
            double gearHandlePosition,
            double rudderPosition,
            double elevatorPosition,
            double aileronPosition,
            double throttleLeverPosition,
            double parkingBrake,
            double autopilotMaster,
            double autopilotHeadingLock,
            double autopilotNavLock,
            double autopilotApproachHold,
            double autopilotAltitudeLock,
            double autopilotAirspeedHold,
            double totalAirTemperature,
            double ambientAirTemperature)
        {
            IndicatedAirspeed = indicatedAirspeed;
            TrueAirspeed = trueAirspeed;
            Mach = mach;
            Altitude = altitude;
            RadioAltitude = radioAltitude;
            VerticalSpeed = verticalSpeed;
            Pitch = pitch;
            Bank = bank;
            Heading = heading;
            Latitude = latitude;
            Longitude = longitude;
            AngleOfAttack = angleOfAttack;
            GForce = gForce;
            StallWarning = stallWarning;
            OverspeedWarning = overspeedWarning;
            OnGround = onGround;
            FlapHandleIndex = flapHandleIndex;
            SpoilersHandlePosition = spoilersHandlePosition;
            GearHandlePosition = gearHandlePosition;
            RudderPosition = rudderPosition;
            ElevatorPosition = elevatorPosition;
            AileronPosition = aileronPosition;
            ThrottleLeverPosition = throttleLeverPosition;
            ParkingBrake = parkingBrake;
            AutopilotMaster = autopilotMaster;
            AutopilotHeadingLock = autopilotHeadingLock;
            AutopilotNavLock = autopilotNavLock;
            AutopilotApproachHold = autopilotApproachHold;
            AutopilotAltitudeLock = autopilotAltitudeLock;
            AutopilotAirspeedHold = autopilotAirspeedHold;
            TotalAirTemperature = totalAirTemperature;
            AmbientAirTemperature = ambientAirTemperature;
        }
    }
}
