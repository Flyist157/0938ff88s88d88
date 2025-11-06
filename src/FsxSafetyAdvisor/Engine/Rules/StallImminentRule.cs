using System;
using System.Linq;
using FsxSafetyAdvisor.Domain;
using FsxSafetyAdvisor.Knowledge;

namespace FsxSafetyAdvisor.Engine.Rules;

public sealed class StallImminentRule : IAdvisoryRule
{
    private readonly Procedure? _procedure;

    public StallImminentRule(Procedure? procedure)
    {
        _procedure = procedure;
    }

    public string Id => "STALL_IMMINENT";

    public AdvisoryResult? Evaluate(FlightState state)
    {
        if (state.OnGround)
        {
            return null;
        }

        var stallWarningActive = state.Warnings.StallWarning;
        var lowEnergy = state.IndicatedAirspeedKts < 130 && state.Derived.IsApproach;
        var highAoa = state.AngleOfAttackDegrees > 12;

        if (!stallWarningActive && !(lowEnergy && highAoa))
        {
            return null;
        }

        var spokenSummary = _procedure?.SpokenSummary ?? "Disconnect the autopilot, reduce angle of attack, add thrust, level your wings.";
        var steps = _procedure?.Steps.Take(3).ToArray() ?? Array.Empty<string>();
        var stepsText = steps.Length > 0 ? string.Join(", ", steps) : "Lower the nose, apply full power, level the wings, and recover to climb speed.";

        var speech = "Stall developing. " + spokenSummary + ". Key actions: " + stepsText + ".";

        return new AdvisoryResult(
            Id,
            AdvisorySeverity.Critical,
            "Stall developing",
            speech,
            _procedure,
            TimeSpan.FromSeconds(20));
    }
}
