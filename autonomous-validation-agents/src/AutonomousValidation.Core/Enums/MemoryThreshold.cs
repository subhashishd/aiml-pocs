namespace AutonomousValidation.Core.Enums;

/// <summary>
/// Represents different memory threshold levels for adaptive resource management
/// </summary>
public enum MemoryThreshold
{
    /// <summary>
    /// Critical memory level (&lt;1GB available) - Single orchestrator with sequential processing
    /// </summary>
    Critical = 0,
    
    /// <summary>
    /// Low memory level (1-3GB available) - Consolidated agents with minimal sub-agents
    /// </summary>
    Low = 1,
    
    /// <summary>
    /// Medium memory level (3-6GB available) - Core agents with selective sub-agent spawning
    /// </summary>
    Medium = 2,
    
    /// <summary>
    /// High memory level (&gt;6GB available) - Full agent ecosystem with sub-agents
    /// </summary>
    High = 3
}
