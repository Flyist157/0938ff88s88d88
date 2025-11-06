using System;
using System.Collections.Generic;
using System.Linq;
using FsxSafetyAdvisor.Domain;
using FsxSafetyAdvisor.Infrastructure;
using FsxSafetyAdvisor.Speech;

namespace FsxSafetyAdvisor.Engine;

public sealed class AdvisoryEngine
{
    private readonly IReadOnlyList<IAdvisoryRule> _rules;
    private readonly Dictionary<string, DateTime> _lastTriggerUtc = new(StringComparer.OrdinalIgnoreCase);
    private readonly SpeechService _speechService;
    private readonly ConsoleLogger _logger;

    public AdvisoryEngine(IEnumerable<IAdvisoryRule> rules, SpeechService speechService, ConsoleLogger logger)
    {
        _rules = rules.ToList();
        _speechService = speechService;
        _logger = logger;
    }

    public event EventHandler<AdvisoryResult>? AdvisoryGenerated;

    public void Process(FlightState state)
    {
        foreach (var rule in _rules)
        {
            AdvisoryResult? result = null;
            try
            {
                result = rule.Evaluate(state);
            }
            catch (Exception ex)
            {
                _logger.Error($"Rule '{rule.Id}' threw an exception.", ex);
            }

            if (result is null)
            {
                continue;
            }

            if (!ShouldEmit(result))
            {
                continue;
            }

            _lastTriggerUtc[result.RuleId] = DateTime.UtcNow;
            _logger.Warn($"Advisory triggered: {result.Headline}");
            _speechService.Enqueue(result.SpokenMessage);
            AdvisoryGenerated?.Invoke(this, result);
        }
    }

    private bool ShouldEmit(AdvisoryResult result)
    {
        if (!_lastTriggerUtc.TryGetValue(result.RuleId, out var lastTime))
        {
            return true;
        }

        return DateTime.UtcNow - lastTime > result.SuppressionWindow;
    }
}
