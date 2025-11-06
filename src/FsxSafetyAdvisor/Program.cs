using System;
using System.Threading;
using System.Threading.Tasks;

namespace FsxSafetyAdvisor;

internal static class Program
{
    [STAThread]
    private static async Task Main(string[] args)
    {
        using var cts = new CancellationTokenSource();
        Console.CancelKeyPress += (_, eventArgs) =>
        {
            eventArgs.Cancel = true;
            cts.Cancel();
        };

        try
        {
            using var app = new SafetyAdvisorApp();
            await app.RunAsync(cts.Token).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            Console.WriteLine("A fatal error occurred: " + ex);
        }
    }
}
