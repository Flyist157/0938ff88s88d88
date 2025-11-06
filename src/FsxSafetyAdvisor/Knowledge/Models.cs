using System.Collections.Generic;

namespace FsxSafetyAdvisor.Knowledge;

public sealed class Procedure
{
    public string Id { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Phase { get; set; } = string.Empty;
    public string Summary { get; set; } = string.Empty;
    public string SpokenSummary { get; set; } = string.Empty;
    public List<string> Steps { get; set; } = new();
}

public sealed class ProcedureDocument
{
    public List<Procedure> Procedures { get; set; } = new();
}
