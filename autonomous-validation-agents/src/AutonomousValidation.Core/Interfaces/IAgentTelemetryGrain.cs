using Orleans;
using AutonomousValidation.Core.Models;

namespace AutonomousValidation.Core.Interfaces;

/// <summary>
/// Interface for collecting and analyzing agent telemetry data
/// This is our foundation for agent evaluation - starting with basic telemetry collection
/// </summary>
public interface IAgentTelemetryGrain : IGrainWithStringKey
{
    /// <summary>
    /// Record a decision made by the agent
    /// </summary>
    Task RecordDecisionAsync(AgentDecision decision);
    
    /// <summary>
    /// Record a performance metric
    /// </summary>
    Task RecordPerformanceMetricAsync(PerformanceMetric metric);
    
    /// <summary>
    /// Record resource usage snapshot
    /// </summary>
    Task RecordResourceUsageAsync(ResourceUsageSnapshot usage);
    
    /// <summary>
    /// Record an adaptation event
    /// </summary>
    Task RecordAdaptationEventAsync(AdaptationEvent adaptation);
    
    /// <summary>
    /// Get behavior profile for a specific time period
    /// </summary>
    Task<AgentBehaviorProfile> GetBehaviorProfileAsync(TimeSpan period);
    
    /// <summary>
    /// Get recent decisions within a time period
    /// </summary>
    Task<List<AgentDecision>> GetRecentDecisionsAsync(TimeSpan period);
    
    /// <summary>
    /// Get recent performance metrics within a time period
    /// </summary>
    Task<List<PerformanceMetric>> GetRecentMetricsAsync(TimeSpan period);
    
    /// <summary>
    /// Get basic statistics for the agent
    /// </summary>
    Task<BasicAgentStats> GetBasicStatsAsync();
}
