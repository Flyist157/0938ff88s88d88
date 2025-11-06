using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using FsxSafetyAdvisor.Infrastructure;

namespace FsxSafetyAdvisor.Knowledge;

public sealed class ProcedureRepository
{
    private readonly string _documentPath;
    private readonly ConsoleLogger _logger;
    private readonly Dictionary<string, Procedure> _procedureIndex = new(StringComparer.OrdinalIgnoreCase);

    public ProcedureRepository(string documentPath, ConsoleLogger logger)
    {
        _documentPath = documentPath;
        _logger = logger;
    }

    public IReadOnlyCollection<Procedure> Procedures => _procedureIndex.Values;

    public void Load()
    {
        if (!File.Exists(_documentPath))
        {
            throw new FileNotFoundException($"Procedure knowledge base not found at '{_documentPath}'.");
        }

        try
        {
            var json = File.ReadAllText(_documentPath);
            var options = new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };
            var doc = JsonSerializer.Deserialize<ProcedureDocument>(json, options);
            if (doc is null)
            {
                throw new InvalidOperationException("Failed to deserialize procedure document.");
            }

            _procedureIndex.Clear();
            foreach (var procedure in doc.Procedures)
            {
                if (string.IsNullOrWhiteSpace(procedure.Id))
                {
                    _logger.Warn("Encountered procedure without an id – skipping.");
                    continue;
                }

                _procedureIndex[procedure.Id] = procedure;
            }

            _logger.Info($"Loaded {_procedureIndex.Count} procedures.");
        }
        catch (Exception ex)
        {
            throw new InvalidOperationException("Failed to load procedures.", ex);
        }
    }

    public Procedure? GetById(string procedureId)
    {
        if (string.IsNullOrWhiteSpace(procedureId))
        {
            return null;
        }

        return _procedureIndex.TryGetValue(procedureId, out var procedure) ? procedure : null;
    }

    public Procedure? FindByPhase(string phase)
    {
        if (string.IsNullOrWhiteSpace(phase))
        {
            return null;
        }

        return _procedureIndex.Values.FirstOrDefault(p => string.Equals(p.Phase, phase, StringComparison.OrdinalIgnoreCase));
    }
}
