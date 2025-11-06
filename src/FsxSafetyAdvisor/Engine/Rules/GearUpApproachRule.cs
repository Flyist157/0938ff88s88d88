using System;
using System.Linq;
using FsxSafetyAdvisor.Domain;
using FsxSafetyAdvisor.Knowledge;

namespace FsxSafetyAdvisor.Engine.Rules;

public sealed class GearUpApproachRule : IAdvisoryRule
{
    private readonly Procedure? _procedure;

    public GearUpApproachRule(Procedure? procedure)
    {
        _procedure = procedure;
    }

    public string Id => "GEAR_UP_APPROACH";

    public AdvisoryResult? Evaluate(FlightState state)
    {
        if (!state.Derived.IsApproach)
        {
            return null;
        }

        var lowAltitude = state.RadioAltitudeFeet is > 0 and < 1200;
        var sinking = state.VerticalSpeedFpm < -300;
        var gearNotDown = !state.Configuration.GearDown;

        if (!(lowAltitude && sinking && gearNotDown))
        {
            return null;
        }

        var spokenSummary = _procedure?.SpokenSummary ?? "Extend the landing gear now and verify three green before continuing the approach.";
        var steps = _procedure?.Steps.Take(3).ToArray() ?? Array.Empty<string>();
        var stepsText = steps.Length > 0 ? string.Join(", ", steps) : "Select gear down, confirm green lights, call 'gear down'.";

        var speech = "Approach gear is still up. " + spokenSummary + ". Key actions: " + stepsText + ".";

        return new AdvisoryResult(
            Id,
            AdvisorySeverity.Warning,
            "Gear up on approach",
            speech,
            _procedure,
            TimeSpan.FromSeconds(15));
    }
}
