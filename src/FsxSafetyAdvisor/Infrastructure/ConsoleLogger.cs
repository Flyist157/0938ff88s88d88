using System;

namespace FsxSafetyAdvisor.Infrastructure;

public sealed class ConsoleLogger
{
    private static readonly object Gate = new();

    public void Info(string message) => Write("INFO", message);
    public void Warn(string message) => Write("WARN", message);
    public void Error(string message) => Write("ERROR", message);
    public void Error(string message, Exception exception) => Write("ERROR", $"{message}{Environment.NewLine}{exception}");

    private static void Write(string level, string message)
    {
        lock (Gate)
        {
            var timestamp = DateTime.UtcNow.ToString("u");
            Console.WriteLine($"[{timestamp}] [{level}] {message}");
        }
    }
}
