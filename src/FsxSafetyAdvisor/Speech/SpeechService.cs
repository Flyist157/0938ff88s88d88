using System;
using System.Collections.Concurrent;
using System.Speech.Synthesis;
using System.Threading;
using System.Threading.Tasks;
using FsxSafetyAdvisor.Infrastructure;

namespace FsxSafetyAdvisor.Speech;

public sealed class SpeechService : IDisposable
{
    private readonly SpeechSynthesizer _synthesizer;
    private readonly BlockingCollection<string> _queue;
    private readonly CancellationTokenSource _shutdownCts = new();
    private readonly ConsoleLogger _logger;
    private Task? _worker;

    public SpeechService(ConsoleLogger logger)
    {
        _logger = logger;
        _synthesizer = new SpeechSynthesizer
        {
            Rate = 0,
            Volume = 90
        };
        _queue = new BlockingCollection<string>(new ConcurrentQueue<string>());
    }

    public void ConfigureVoice(string? voiceName = null)
    {
        if (!string.IsNullOrWhiteSpace(voiceName))
        {
            try
            {
                _synthesizer.SelectVoice(voiceName);
                _logger.Info($"Speech voice set to '{voiceName}'.");
            }
            catch (Exception ex)
            {
                _logger.Warn($"Unable to set voice '{voiceName}': {ex.Message}");
            }
        }
    }

    public void Start()
    {
        if (_worker is { IsCompleted: false })
        {
            return;
        }

        _worker = Task.Run(() => PumpAsync(_shutdownCts.Token));
    }

    public void Enqueue(string text)
    {
        if (string.IsNullOrWhiteSpace(text))
        {
            return;
        }

        if (!_queue.IsAddingCompleted)
        {
            _queue.Add(text.Trim());
        }
    }

    public void Stop()
    {
        _shutdownCts.Cancel();
        _queue.CompleteAdding();
        try
        {
            _worker?.Wait(TimeSpan.FromSeconds(2));
        }
        catch (AggregateException)
        {
            // swallow cancellation aggregate
        }
    }

    private void PumpAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            string? text = null;
            try
            {
                text = _queue.Take(token);
            }
            catch (OperationCanceledException)
            {
                break;
            }
            catch (InvalidOperationException)
            {
                break;
            }

            if (string.IsNullOrEmpty(text))
            {
                continue;
            }

            try
            {
                _logger.Info($"Speaking advisory: {text}");
                _synthesizer.Speak(text);
            }
            catch (Exception ex)
            {
                _logger.Error("Failed to play advisory", ex);
            }
        }
    }

    public void Dispose()
    {
        Stop();
        _synthesizer.Dispose();
        _queue.Dispose();
        _shutdownCts.Dispose();
    }
}
