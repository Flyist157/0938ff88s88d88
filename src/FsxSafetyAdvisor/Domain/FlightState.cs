using System;

namespace FsxSafetyAdvisor.Domain;

public sealed class FlightState
{
    public FlightState(
        DateTime timestampUtc,
        double indicatedAirspeedKts,
        double trueAirspeedKts,
        double mach,
        double pressureAltitudeFeet,
        double radioAltitudeFeet,
        double verticalSpeedFpm,
        double pitchDegrees,
        double bankDegrees,
        double headingDegrees,
        double angleOfAttackDegrees,
        double gForce,
        bool onGround,
        double latitude,
        double longitude,
        double totalAirTemperatureC,
        double outsideAirTemperatureC,
        ControlInputs controls,
        AircraftConfiguration configuration,
        AutopilotState autopilot,
        WarningFlags warnings)
    {
        TimestampUtc = timestampUtc;
        IndicatedAirspeedKts = indicatedAirspeedKts;
        TrueAirspeedKts = trueAirspeedKts;
        Mach = mach;
        PressureAltitudeFeet = pressureAltitudeFeet;
        RadioAltitudeFeet = radioAltitudeFeet;
        VerticalSpeedFpm = verticalSpeedFpm;
        PitchDegrees = pitchDegrees;
        BankDegrees = bankDegrees;
        HeadingDegrees = headingDegrees;
        AngleOfAttackDegrees = angleOfAttackDegrees;
        GForce = gForce;
        OnGround = onGround;
        Latitude = latitude;
        Longitude = longitude;
        TotalAirTemperatureC = totalAirTemperatureC;
        OutsideAirTemperatureC = outsideAirTemperatureC;
        Controls = controls;
        Configuration = configuration;
        Autopilot = autopilot;
        Warnings = warnings;
        Derived = DerivedMetrics.From(this);
    }

    public DateTime TimestampUtc { get; }
    public double IndicatedAirspeedKts { get; }
    public double TrueAirspeedKts { get; }
    public double Mach { get; }
    public double PressureAltitudeFeet { get; }
    public double RadioAltitudeFeet { get; }
    public double VerticalSpeedFpm { get; }
    public double PitchDegrees { get; }
    public double BankDegrees { get; }
    public double HeadingDegrees { get; }
    public double AngleOfAttackDegrees { get; }
    public double GForce { get; }
    public bool OnGround { get; }
    public double Latitude { get; }
    public double Longitude { get; }
    public double TotalAirTemperatureC { get; }
    public double OutsideAirTemperatureC { get; }
    public ControlInputs Controls { get; }
    public AircraftConfiguration Configuration { get; }
    public AutopilotState Autopilot { get; }
    public WarningFlags Warnings { get; }
    public DerivedMetrics Derived { get; }
}

public sealed class ControlInputs
{
    public ControlInputs(double elevator, double aileron, double rudder, double throttleLeverPosition, double spoilerHandlePosition)
    {
        Elevator = elevator;
        Aileron = aileron;
        Rudder = rudder;
        ThrottleLeverPosition = throttleLeverPosition;
        SpoilerHandlePosition = spoilerHandlePosition;
    }

    public double Elevator { get; }
    public double Aileron { get; }
    public double Rudder { get; }
    public double ThrottleLeverPosition { get; }
    public double SpoilerHandlePosition { get; }
}

public sealed class AircraftConfiguration
{
    public AircraftConfiguration(double flapHandleIndex, double gearHandlePosition, double spoilerPosition, bool parkingBrakeSet)
    {
        FlapHandleIndex = flapHandleIndex;
        GearHandlePosition = gearHandlePosition;
        SpoilerPosition = spoilerPosition;
        ParkingBrakeSet = parkingBrakeSet;
    }

    public double FlapHandleIndex { get; }
    public double GearHandlePosition { get; }
    public double SpoilerPosition { get; }
    public bool ParkingBrakeSet { get; }

    public bool GearDown => GearHandlePosition > 0.5;
    public bool FlapsExtended => FlapHandleIndex > 0.1;
    public bool SpoilersDeployed => SpoilerPosition > 0.1;
}

public sealed class AutopilotState
{
    public AutopilotState(bool master, bool headingHold, bool navHold, bool approachHold, bool altitudeHold, bool airspeedHold)
    {
        Master = master;
        HeadingHold = headingHold;
        NavHold = navHold;
        ApproachHold = approachHold;
        AltitudeHold = altitudeHold;
        AirspeedHold = airspeedHold;
    }

    public bool Master { get; }
    public bool HeadingHold { get; }
    public bool NavHold { get; }
    public bool ApproachHold { get; }
    public bool AltitudeHold { get; }
    public bool AirspeedHold { get; }
}

public sealed class WarningFlags
{
    public WarningFlags(bool stallWarning, bool overspeedWarning, bool masterWarning, bool masterCaution)
    {
        StallWarning = stallWarning;
        OverspeedWarning = overspeedWarning;
        MasterWarning = masterWarning;
        MasterCaution = masterCaution;
    }

    public bool StallWarning { get; }
    public bool OverspeedWarning { get; }
    public bool MasterWarning { get; }
    public bool MasterCaution { get; }
}

public sealed class DerivedMetrics
{
    private DerivedMetrics(bool isTakeoff, bool isApproach, bool isLanding, bool isGoAround, double energyMarginKts, double loadFactorMargin)
    {
        IsTakeoff = isTakeoff;
        IsApproach = isApproach;
        IsLanding = isLanding;
        IsGoAround = isGoAround;
        EnergyMarginKts = energyMarginKts;
        LoadFactorMargin = loadFactorMargin;
    }

    public bool IsTakeoff { get; }
    public bool IsApproach { get; }
    public bool IsLanding { get; }
    public bool IsGoAround { get; }
    /// <summary>
    /// Difference between current IAS and a typical safe reference (Vref/Vapp estimate) for the detected phase.
    /// Positive values mean excess energy, negative values indicate low energy.
    /// </summary>
    public double EnergyMarginKts { get; }
    /// <summary>
    /// G-load relative to 1G. Useful for over/under-load detection.
    /// </summary>
    public double LoadFactorMargin { get; }

    public static DerivedMetrics From(FlightState state)
    {
        var isTakeoff = state.OnGround && state.IndicatedAirspeedKts > 40 && state.VerticalSpeedFpm > 200;
        var isApproach = !state.OnGround && state.RadioAltitudeFeet is > 0 and < 1500 && state.VerticalSpeedFpm < -100;
        var isLanding = isApproach && state.RadioAltitudeFeet < 200;
        var isGoAround = !state.OnGround && state.VerticalSpeedFpm > 800 && state.RadioAltitudeFeet < 800 && state.ThrottlesHigh();

        var referenceSpeed = isLanding ? 140 : isApproach ? 160 : isTakeoff ? 150 : 210;
        var energyMargin = state.IndicatedAirspeedKts - referenceSpeed;
        var loadMargin = state.GForce - 1.0;

        return new DerivedMetrics(isTakeoff, isApproach, isLanding, isGoAround, energyMargin, loadMargin);
    }
}

internal static class FlightStateExtensions
{
    public static bool ThrottlesHigh(this FlightState state) => state.Controls.ThrottleLeverPosition > 0.65;
}
