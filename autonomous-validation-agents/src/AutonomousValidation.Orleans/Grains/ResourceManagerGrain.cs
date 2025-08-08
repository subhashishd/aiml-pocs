using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;
using System.Diagnostics;

namespace AutonomousValidation.Orleans.Grains;

public class ResourceManagerGrain : Grain, IResourceManagerGrain
{
    private readonly ILogger<ResourceManagerGrain> _logger;
    private readonly Dictionary<string, GrainMemoryUsage> _grainMemoryUsage = new();
    private readonly Dictionary<AgentType, long> _agentMemoryEstimates;
    private readonly PerformanceCounter? _memoryCounter;
    
    // Configuration constants
    private const long SAFETY_BUFFER_BYTES = 512 * 1024 * 1024; // 512MB buffer
    private const double SAFETY_MARGIN = 0.15; // 15% safety buffer
    private const long DEFAULT_MAX_MEMORY = 8L * 1024 * 1024 * 1024; // 8GB default

    public ResourceManagerGrain(ILogger<ResourceManagerGrain> logger)
    {
        _logger = logger;
        
        // Initialize memory estimates for different agent types
        _agentMemoryEstimates = new Dictionary<AgentType, long>
        {
            { AgentType.SemanticKernel, 200 * 1024 * 1024 }, // 200MB
            { AgentType.OCRProcessor, 150 * 1024 * 1024 },   // 150MB
            { AgentType.MultimodalProcessor, 300 * 1024 * 1024 }, // 300MB
            { AgentType.ValidationEngine, 100 * 1024 * 1024 }     // 100MB
        };

        // Initialize performance counter for memory monitoring (Windows only)
        try
        {
            if (OperatingSystem.IsWindows())
            {
                _memoryCounter = new PerformanceCounter("Memory", "Available MBytes");
            }
            else
            {
                _logger.LogInformation("Performance counters not supported on this platform, will use GC estimates");
                _memoryCounter = null;
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to initialize memory performance counter, will use GC estimates");
            _memoryCounter = null;
        }
    }

    public Task<ResourceStatus> GetResourceStatusAsync()
    {
        var currentMemoryUsage = GetCurrentMemoryUsage();
        var availableMemory = GetAvailableMemory();
        var totalMemory = GetTotalSystemMemory();
        
        var memoryUsagePercent = (double)currentMemoryUsage / totalMemory * 100;
        var threshold = DetermineMemoryThreshold(availableMemory);
        
        var resourceStatus = new ResourceStatus
        {
            AvailableMemoryBytes = availableMemory,
            UsedMemoryBytes = currentMemoryUsage,
            TotalMemoryBytes = totalMemory,
            MemoryUsagePercentage = memoryUsagePercent,
            CurrentThreshold = threshold,
            ActiveGrainsCount = _grainMemoryUsage.Count,
            Timestamp = DateTime.UtcNow
        };

        _logger.LogDebug("Resource Status: {AvailableGB:F2}GB available, {UsedGB:F2}GB used, {Threshold}",
            resourceStatus.AvailableMemoryGB, resourceStatus.UsedMemoryBytes / (1024.0 * 1024.0 * 1024.0), threshold);

        return Task.FromResult(resourceStatus);
    }

    public Task<bool> CanSpawnSubAgentAsync(AgentType agentType)
    {
        var availableMemory = GetAvailableMemory();
        var requiredMemory = _agentMemoryEstimates.GetValueOrDefault(agentType, 100 * 1024 * 1024);
        var safeAvailable = availableMemory - SAFETY_BUFFER_BYTES;
        
        var canSpawn = safeAvailable >= requiredMemory;
        
        _logger.LogDebug("Can spawn {AgentType}: {CanSpawn} (Available: {AvailableMB}MB, Required: {RequiredMB}MB)",
            agentType, canSpawn, safeAvailable / (1024 * 1024), requiredMemory / (1024 * 1024));

        return Task.FromResult(canSpawn);
    }

    public Task RegisterGrainMemoryUsageAsync(string grainId, long memoryBytes)
    {
        _grainMemoryUsage[grainId] = new GrainMemoryUsage
        {
            GrainId = grainId,
            MemoryBytes = memoryBytes,
            LastUpdated = DateTime.UtcNow
        };

        _logger.LogTrace("Registered memory usage for grain {GrainId}: {MemoryMB}MB",
            grainId, memoryBytes / (1024 * 1024));

        return Task.CompletedTask;
    }

    public Task<ConsolidationRecommendation> GetConsolidationRecommendationAsync()
    {
        var availableMemory = GetAvailableMemory();
        var threshold = DetermineMemoryThreshold(availableMemory);
        
        var recommendation = new ConsolidationRecommendation
        {
            ShouldConsolidate = threshold <= MemoryThreshold.Low,
            AgentsToConsolidate = new List<AgentType> { AgentType.PDFIntelligence, AgentType.ExcelIntelligence },
            TargetAgent = AgentType.Orchestrator,
            Reasoning = $"Memory threshold is {threshold}, consolidation recommended",
            EstimatedMemorySavings = CalculateEstimatedSaving(threshold)
        };

        _logger.LogInformation("Consolidation recommendation: ShouldConsolidate={ShouldConsolidate} for threshold {Threshold}",
            recommendation.ShouldConsolidate, threshold);

        return Task.FromResult(recommendation);
    }

    public Task<MemoryStatus> GetMemoryStatusAsync()
    {
        var grainUsages = _grainMemoryUsage.Values.ToList();
        
        var status = new MemoryStatus
        {
            UsedMemoryBytes = GetCurrentMemoryUsage(),
            AvailableMemoryBytes = GetAvailableMemory(),
            Timestamp = DateTime.UtcNow,
            GrainUsages = grainUsages
        };

        return Task.FromResult(status);
    }

    public Task UpdateMemoryStatusAsync(MemoryStatus status)
    {
        _logger.LogDebug("Memory status updated: {UsedGB:F2}GB used, {AvailableGB:F2}GB available",
            status.UsedMemoryBytes / (1024.0 * 1024 * 1024),
            status.AvailableMemoryBytes / (1024.0 * 1024 * 1024));
            
        // Could store this for trending/analysis, but for now just log it
        return Task.CompletedTask;
    }

    #region Private Helper Methods

    private long GetCurrentMemoryUsage()
    {
        // Use GC to estimate current memory usage
        return GC.GetTotalMemory(false);
    }

    private long GetAvailableMemory()
    {
        if (_memoryCounter != null && OperatingSystem.IsWindows())
        {
            try
            {
                var availableMB = _memoryCounter.NextValue();
                return (long)(availableMB * 1024 * 1024); // Convert MB to bytes
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to read memory counter, falling back to GC estimate");
            }
        }

        // Fallback: estimate based on GC and default system memory
        var totalMemory = GetTotalSystemMemory();
        var usedMemory = GetCurrentMemoryUsage();
        return Math.Max(0, totalMemory - usedMemory);
    }

    private long GetTotalSystemMemory()
    {
        // For now, use a configurable default (should be read from environment/config)
        return Environment.GetEnvironmentVariable("MAX_MEMORY_GB") switch
        {
            string envVar when long.TryParse(envVar, out var gb) => gb * 1024 * 1024 * 1024,
            _ => DEFAULT_MAX_MEMORY
        };
    }

    private MemoryThreshold DetermineMemoryThreshold(long availableMemory)
    {
        var availableGB = (double)availableMemory / (1024 * 1024 * 1024);
        
        return availableGB switch
        {
            >= 6 => MemoryThreshold.High,
            >= 3 => MemoryThreshold.Medium,
            >= 1 => MemoryThreshold.Low,
            _ => MemoryThreshold.Critical
        };
    }

    private ConsolidationAction DetermineConsolidationAction(MemoryThreshold threshold)
    {
        return threshold switch
        {
            MemoryThreshold.Critical => ConsolidationAction.ImmediateConsolidation,
            MemoryThreshold.Low => ConsolidationAction.RecommendConsolidation,
            MemoryThreshold.Medium => ConsolidationAction.SelectiveConsolidation,
            MemoryThreshold.High => ConsolidationAction.NoAction,
            _ => ConsolidationAction.NoAction
        };
    }

    private List<string> IdentifyGrainsForConsolidation(MemoryThreshold threshold)
    {
        if (threshold >= MemoryThreshold.Medium)
            return new List<string>();

        // For low/critical memory, identify grains that can be consolidated
        // For now, return grains with highest memory usage
        return _grainMemoryUsage
            .OrderByDescending(kvp => kvp.Value.MemoryBytes)
            .Take(threshold == MemoryThreshold.Critical ? 3 : 1)
            .Select(kvp => kvp.Key)
            .ToList();
    }

    private long CalculateEstimatedSaving(MemoryThreshold threshold)
    {
        var grainsToConsolidate = IdentifyGrainsForConsolidation(threshold);
        
        return grainsToConsolidate
            .Where(grainId => _grainMemoryUsage.ContainsKey(grainId))
            .Sum(grainId => _grainMemoryUsage[grainId].MemoryBytes) / 2; // Estimate 50% saving
    }

    #endregion

    public override Task OnActivateAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("ResourceManagerGrain activated");
        
        // Register periodic memory monitoring
        this.RegisterGrainTimer(PerformPeriodicMemoryCheckAsync, 
                     new() { DueTime = TimeSpan.FromSeconds(30), Period = TimeSpan.FromSeconds(30), Interleave = true });
        
        return base.OnActivateAsync(cancellationToken);
    }

    private async Task PerformPeriodicMemoryCheckAsync()
    {
        try
        {
            var resourceStatus = await GetResourceStatusAsync();
            
            // Log memory pressure warnings
            if (resourceStatus.CurrentThreshold <= MemoryThreshold.Low)
            {
                _logger.LogWarning("Memory pressure detected: {AvailableGB:F2}GB available, threshold: {Threshold}",
                    resourceStatus.AvailableMemoryGB, resourceStatus.CurrentThreshold);
            }

            // Cleanup stale grain memory entries (older than 5 minutes)
            var staleEntries = _grainMemoryUsage
                .Where(kvp => DateTime.UtcNow - kvp.Value.LastUpdated > TimeSpan.FromMinutes(5))
                .Select(kvp => kvp.Key)
                .ToList();

            foreach (var staleGrainId in staleEntries)
            {
                _grainMemoryUsage.Remove(staleGrainId);
                _logger.LogTrace("Removed stale memory entry for grain {GrainId}", staleGrainId);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during periodic memory check");
        }
    }

    public override Task OnDeactivateAsync(DeactivationReason reason, CancellationToken cancellationToken)
    {
        _logger.LogInformation("ResourceManagerGrain deactivated: {Reason}", reason);
        _memoryCounter?.Dispose();
        return base.OnDeactivateAsync(reason, cancellationToken);
    }
}
