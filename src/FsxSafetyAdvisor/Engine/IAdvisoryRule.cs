using FsxSafetyAdvisor.Domain;

namespace FsxSafetyAdvisor.Engine;

public interface IAdvisoryRule
{
    string Id { get; }

    AdvisoryResult? Evaluate(FlightState state);
}
