using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Orleans.Grains;

/// <summary>
/// Basic telemetry grain for collecting agent performance metrics and decisions
/// This is the foundation for agent evaluation - starting simple with telemetry collection
/// </summary>
public class AgentTelemetryGrain : Grain, IAgentTelemetryGrain
{
    private readonly ILogger<AgentTelemetryGrain> _logger;
    private readonly List<AgentDecision> _decisions = new();
    private readonly List<PerformanceMetric> _metrics = new();
    private readonly List<ResourceUsageSnapshot> _resourceSnapshots = new();
    private readonly List<AdaptationEvent> _adaptationEvents = new();
    
    // Simple in-memory storage for now - can be enhanced with persistent storage later
    private readonly Dictionary<string, object> _telemetryData = new();
    
    // Configuration
    private const int MAX_STORED_ITEMS = 1000; // Limit memory usage
    private const int CLEANUP_BATCH_SIZE = 100;

    public AgentTelemetryGrain(ILogger<AgentTelemetryGrain> logger)
    {
        _logger = logger;
    }

    public Task RecordDecisionAsync(AgentDecision decision)
    {
        try
        {
            _decisions.Add(decision);
            
            // Simple cleanup to prevent memory issues
            if (_decisions.Count > MAX_STORED_ITEMS)
            {
                _decisions.RemoveRange(0, CLEANUP_BATCH_SIZE);
                _logger.LogDebug("Cleaned up old decisions for agent {AgentId}", decision.AgentId);
            }
            
            _logger.LogTrace("Recorded decision for agent {AgentId}: {DecisionType} with confidence {Confidence}",
                decision.AgentId, decision.DecisionType, decision.ConfidenceScore);
            
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording agent decision");
            return Task.CompletedTask;
        }
    }

    public Task RecordPerformanceMetricAsync(PerformanceMetric metric)
    {
        try
        {
            _metrics.Add(metric);
            
            // Simple cleanup
            if (_metrics.Count > MAX_STORED_ITEMS)
            {
                _metrics.RemoveRange(0, CLEANUP_BATCH_SIZE);
                _logger.LogDebug("Cleaned up old metrics for agent {AgentId}", metric.AgentId);
            }
            
            _logger.LogTrace("Recorded performance metric for agent {AgentId}: {MetricType} = {Value}",
                metric.AgentId, metric.MetricType, metric.Value);
            
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording performance metric");
            return Task.CompletedTask;
        }
    }

    public Task RecordResourceUsageAsync(ResourceUsageSnapshot usage)
    {
        try
        {
            _resourceSnapshots.Add(usage);
            
            // Simple cleanup
            if (_resourceSnapshots.Count > MAX_STORED_ITEMS)
            {
                _resourceSnapshots.RemoveRange(0, CLEANUP_BATCH_SIZE);
                _logger.LogDebug("Cleaned up old resource snapshots for agent {AgentId}", usage.AgentId);
            }
            
            _logger.LogTrace("Recorded resource usage for agent {AgentId}: {MemoryMB}MB memory, {CPUPercent}% CPU",
                usage.AgentId, usage.MemoryUsageMB, usage.CPUUsagePercent);
            
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording resource usage");
            return Task.CompletedTask;
        }
    }

    public Task RecordAdaptationEventAsync(AdaptationEvent adaptation)
    {
        try
        {
            _adaptationEvents.Add(adaptation);
            
            // Simple cleanup
            if (_adaptationEvents.Count > MAX_STORED_ITEMS)
            {
                _adaptationEvents.RemoveRange(0, CLEANUP_BATCH_SIZE);
                _logger.LogDebug("Cleaned up old adaptation events for agent {AgentId}", adaptation.AgentId);
            }
            
            _logger.LogInformation("Recorded adaptation event for agent {AgentId}: {EventType} -> {NewStrategy}",
                adaptation.AgentId, adaptation.EventType, adaptation.NewStrategy);
            
            return Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording adaptation event");
            return Task.CompletedTask;
        }
    }

    public Task<AgentBehaviorProfile> GetBehaviorProfileAsync(TimeSpan period)
    {
        try
        {
            var cutoffTime = DateTime.UtcNow - period;
            var agentId = this.GetPrimaryKeyString();
            
            // Filter data within the time period
            var recentDecisions = _decisions.Where(d => d.Timestamp >= cutoffTime).ToList();
            var recentMetrics = _metrics.Where(m => m.Timestamp >= cutoffTime).ToList();
            var recentSnapshots = _resourceSnapshots.Where(s => s.Timestamp >= cutoffTime).ToList();
            var recentAdaptations = _adaptationEvents.Where(a => a.Timestamp >= cutoffTime).ToList();
            
            // Build basic behavior profile
            var profile = new AgentBehaviorProfile
            {
                AgentId = agentId,
                AnalysisPeriod = period,
                TotalDecisions = recentDecisions.Count,
                AverageDecisionConfidence = recentDecisions.Any() ? recentDecisions.Average(d => d.ConfidenceScore) : 0,
                TotalMetrics = recentMetrics.Count,
                TotalAdaptations = recentAdaptations.Count,
                AverageMemoryUsageMB = recentSnapshots.Any() ? recentSnapshots.Average(s => s.MemoryUsageMB) : 0,
                AverageCPUUsagePercent = recentSnapshots.Any() ? recentSnapshots.Average(s => s.CPUUsagePercent) : 0,
                ProfileGeneratedAt = DateTime.UtcNow
            };
            
            // Add decision type breakdown
            profile.DecisionTypeBreakdown = recentDecisions
                .GroupBy(d => d.DecisionType)
                .ToDictionary(g => g.Key, g => g.Count());
            
            // Add metric type breakdown
            profile.MetricTypeBreakdown = recentMetrics
                .GroupBy(m => m.MetricType)
                .ToDictionary(g => g.Key, g => g.Average(m => m.Value));
            
            _logger.LogDebug("Generated behavior profile for agent {AgentId}: {Decisions} decisions, {Metrics} metrics over {Period}",
                agentId, profile.TotalDecisions, profile.TotalMetrics, period);
            
            return Task.FromResult(profile);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating behavior profile");
            return Task.FromResult(new AgentBehaviorProfile 
            { 
                AgentId = this.GetPrimaryKeyString(),
                AnalysisPeriod = period,
                ProfileGeneratedAt = DateTime.UtcNow
            });
        }
    }

    #region Basic Analytics Methods

    public Task<List<AgentDecision>> GetRecentDecisionsAsync(TimeSpan period)
    {
        var cutoffTime = DateTime.UtcNow - period;
        var recentDecisions = _decisions.Where(d => d.Timestamp >= cutoffTime).ToList();
        return Task.FromResult(recentDecisions);
    }

    public Task<List<PerformanceMetric>> GetRecentMetricsAsync(TimeSpan period)
    {
        var cutoffTime = DateTime.UtcNow - period;
        var recentMetrics = _metrics.Where(m => m.Timestamp >= cutoffTime).ToList();
        return Task.FromResult(recentMetrics);
    }

    public Task<BasicAgentStats> GetBasicStatsAsync()
    {
        var stats = new BasicAgentStats
        {
            AgentId = this.GetPrimaryKeyString(),
            TotalDecisions = _decisions.Count,
            TotalMetrics = _metrics.Count,
            TotalResourceSnapshots = _resourceSnapshots.Count,
            TotalAdaptations = _adaptationEvents.Count,
            LastDecisionTime = _decisions.LastOrDefault()?.Timestamp,
            LastMetricTime = _metrics.LastOrDefault()?.Timestamp,
            AverageDecisionConfidence = _decisions.Any() ? _decisions.Average(d => d.ConfidenceScore) : 0,
            CurrentMemoryUsageMB = _resourceSnapshots.LastOrDefault()?.MemoryUsageMB ?? 0,
            StatsGeneratedAt = DateTime.UtcNow
        };
        
        return Task.FromResult(stats);
    }

    #endregion

    public override Task OnActivateAsync(CancellationToken cancellationToken)
    {
        var agentId = this.GetPrimaryKeyString();
        _logger.LogInformation("AgentTelemetryGrain activated for agent {AgentId}", agentId);
        
        // Register periodic cleanup timer
        this.RegisterGrainTimer(PerformPeriodicCleanupAsync, 
                     new() { DueTime = TimeSpan.FromMinutes(5), Period = TimeSpan.FromMinutes(5), Interleave = true });
        
        return base.OnActivateAsync(cancellationToken);
    }

    private Task PerformPeriodicCleanupAsync()
    {
        try
        {
            var cutoffTime = DateTime.UtcNow - TimeSpan.FromHours(24); // Keep 24 hours of data
            var agentId = this.GetPrimaryKeyString();
            
            // Clean old data
            var removedDecisions = _decisions.RemoveAll(d => d.Timestamp < cutoffTime);
            var removedMetrics = _metrics.RemoveAll(m => m.Timestamp < cutoffTime);
            var removedSnapshots = _resourceSnapshots.RemoveAll(s => s.Timestamp < cutoffTime);
            var removedAdaptations = _adaptationEvents.RemoveAll(a => a.Timestamp < cutoffTime);
            
            if (removedDecisions > 0 || removedMetrics > 0 || removedSnapshots > 0 || removedAdaptations > 0)
            {
                _logger.LogDebug("Periodic cleanup for agent {AgentId}: removed {Decisions} decisions, {Metrics} metrics, {Snapshots} snapshots, {Adaptations} adaptations",
                    agentId, removedDecisions, removedMetrics, removedSnapshots, removedAdaptations);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during periodic cleanup");
        }
        
        return Task.CompletedTask;
    }

    public override Task OnDeactivateAsync(DeactivationReason reason, CancellationToken cancellationToken)
    {
        var agentId = this.GetPrimaryKeyString();
        _logger.LogInformation("AgentTelemetryGrain deactivated for agent {AgentId}: {Reason}", agentId, reason);
        
        // Log final stats before deactivation
        _logger.LogInformation("Final telemetry stats for agent {AgentId}: {Decisions} decisions, {Metrics} metrics, {Snapshots} snapshots",
            agentId, _decisions.Count, _metrics.Count, _resourceSnapshots.Count);
        
        return base.OnDeactivateAsync(reason, cancellationToken);
    }
}
