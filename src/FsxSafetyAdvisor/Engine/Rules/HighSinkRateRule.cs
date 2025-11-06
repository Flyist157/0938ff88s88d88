using System;
using System.Linq;
using FsxSafetyAdvisor.Domain;
using FsxSafetyAdvisor.Knowledge;

namespace FsxSafetyAdvisor.Engine.Rules;

public sealed class HighSinkRateRule : IAdvisoryRule
{
    private readonly Procedure? _procedure;

    public HighSinkRateRule(Procedure? procedure)
    {
        _procedure = procedure;
    }

    public string Id => "HIGH_SINK_RATE";

    public AdvisoryResult? Evaluate(FlightState state)
    {
        if (!state.Derived.IsApproach)
        {
            return null;
        }

        var lowAltitude = state.RadioAltitudeFeet is > 0 and < 1000;
        var highSink = state.VerticalSpeedFpm < -1200;
        var lowEnergy = state.IndicatedAirspeedKts < 150 && state.AngleOfAttackDegrees > 8;

        if (!(lowAltitude && highSink && lowEnergy))
        {
            return null;
        }

        var spokenSummary = _procedure?.SpokenSummary ?? "Initiate a go-around: pitch to go-around attitude, add power, retract spoilers, and climb away.";
        var steps = _procedure?.Steps.Take(3).ToArray() ?? Array.Empty<string>();
        var stepsText = steps.Length > 0 ? string.Join(", ", steps) : "Advance thrust levers, pitch to 15 degrees, retract spoilers, clean up when positive climb.";

        var speech = "High sink rate detected. " + spokenSummary + ". Key actions: " + stepsText + ".";

        return new AdvisoryResult(
            Id,
            AdvisorySeverity.Critical,
            "High sink rate on approach",
            speech,
            _procedure,
            TimeSpan.FromSeconds(15));
    }
}
