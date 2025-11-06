using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using FsxSafetyAdvisor.Engine;
using FsxSafetyAdvisor.Engine.Rules;
using FsxSafetyAdvisor.Infrastructure;
using FsxSafetyAdvisor.Knowledge;
using FsxSafetyAdvisor.Sim;
using FsxSafetyAdvisor.Speech;

namespace FsxSafetyAdvisor;

public sealed class SafetyAdvisorApp : IDisposable
{
    private readonly ConsoleLogger _logger = new();
    private readonly ProcedureRepository _procedureRepository;
    private readonly SpeechService _speechService;
    private readonly SimConnectManager _simConnectManager;
    private readonly AdvisoryEngine _advisoryEngine;
    private bool _disposed;

    public SafetyAdvisorApp()
    {
        var dataPath = Path.Combine(AppContext.BaseDirectory, "data", "procedures.json");
        _procedureRepository = new ProcedureRepository(dataPath, _logger);
        _procedureRepository.Load();

        _speechService = new SpeechService(_logger);
        _speechService.ConfigureVoice();

        _simConnectManager = new SimConnectManager(_logger);
        _simConnectManager.Connected += SimConnectManagerOnConnected;
        _simConnectManager.Disconnected += SimConnectManagerOnDisconnected;
        _simConnectManager.FlightStateUpdated += SimConnectManagerOnFlightStateUpdated;

        var stallProcedure = _procedureRepository.GetById("stall_recovery");
        var gearProcedure = _procedureRepository.GetById("landing_gear_down_check");
        var goAroundProcedure = _procedureRepository.GetById("unstable_approach_go_around");

        var rules = new IAdvisoryRule[]
        {
            new StallImminentRule(stallProcedure),
            new GearUpApproachRule(gearProcedure),
            new HighSinkRateRule(goAroundProcedure)
        };

        _advisoryEngine = new AdvisoryEngine(rules, _speechService, _logger);
        _advisoryEngine.AdvisoryGenerated += AdvisoryEngineOnAdvisoryGenerated;
    }

    public async Task RunAsync(CancellationToken cancellationToken)
    {
        if (_disposed)
        {
            throw new ObjectDisposedException(nameof(SafetyAdvisorApp));
        }

        _logger.Info("FSX Safety Advisor starting. Press Ctrl+C to exit.");
        _speechService.Start();

        try
        {
            await _simConnectManager.ConnectAsync(cancellationToken).ConfigureAwait(false);

            try
            {
                await Task.Delay(Timeout.Infinite, cancellationToken).ConfigureAwait(false);
            }
            catch (OperationCanceledException)
            {
                // graceful shutdown
            }
        }
        finally
        {
            await _simConnectManager.DisconnectAsync().ConfigureAwait(false);
            _speechService.Stop();
        }
    }

    private void SimConnectManagerOnConnected(object? sender, EventArgs e)
    {
        _speechService.Enqueue("Safety advisor connected. Monitoring instruments and controls.");
    }

    private void SimConnectManagerOnDisconnected(object? sender, EventArgs e)
    {
        _speechService.Enqueue("Safety advisor disconnected from simulator.");
    }

    private void SimConnectManagerOnFlightStateUpdated(object? sender, Domain.FlightState state)
    {
        _advisoryEngine.Process(state);
    }

    private void AdvisoryEngineOnAdvisoryGenerated(object? sender, AdvisoryResult e)
    {
        _logger.Warn($"Advisory {e.RuleId}: {e.Headline}");
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _advisoryEngine.AdvisoryGenerated -= AdvisoryEngineOnAdvisoryGenerated;
        _simConnectManager.Connected -= SimConnectManagerOnConnected;
        _simConnectManager.Disconnected -= SimConnectManagerOnDisconnected;
        _simConnectManager.FlightStateUpdated -= SimConnectManagerOnFlightStateUpdated;
        _speechService.Dispose();
        _simConnectManager.Dispose();
    }
}
