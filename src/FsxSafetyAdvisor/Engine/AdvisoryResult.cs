using System;
using FsxSafetyAdvisor.Knowledge;

namespace FsxSafetyAdvisor.Engine;

public enum AdvisorySeverity
{
    Info = 0,
    Caution = 1,
    Warning = 2,
    Critical = 3
}

public sealed class AdvisoryResult
{
    public AdvisoryResult(string ruleId, AdvisorySeverity severity, string headline, string spokenMessage, Procedure? procedure, TimeSpan suppressionWindow)
    {
        RuleId = ruleId;
        Severity = severity;
        Headline = headline;
        SpokenMessage = spokenMessage;
        Procedure = procedure;
        SuppressionWindow = suppressionWindow;
    }

    public string RuleId { get; }
    public AdvisorySeverity Severity { get; }
    public string Headline { get; }
    public string SpokenMessage { get; }
    public Procedure? Procedure { get; }
    public TimeSpan SuppressionWindow { get; }
}
