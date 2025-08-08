using Microsoft.AspNetCore.Mvc;
using Orleans;
using AutonomousValidation.Orleans.Interfaces;

namespace AutonomousValidation.Orleans.Controllers;

[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    private readonly IClusterClient _clusterClient;
    private readonly ILogger<HealthController> _logger;

    public HealthController(IClusterClient clusterClient, ILogger<HealthController> logger)
    {
        _clusterClient = clusterClient;
        _logger = logger;
    }

    /// <summary>
    /// Basic health check endpoint
    /// </summary>
    [HttpGet]
    public ActionResult<object> GetHealth()
    {
        return Ok(new
        {
            status = "healthy",
            service = "autonomous-validation-orleans",
            timestamp = DateTime.UtcNow,
            version = "1.0.0"
        });
    }

    /// <summary>
    /// Detailed health check including Orleans cluster and model status
    /// </summary>
    [HttpGet("detailed")]
    public async Task<ActionResult<object>> GetDetailedHealthAsync()
    {
        try
        {
            var healthStatus = new
            {
                status = "healthy",
                service = "autonomous-validation-orleans",
                timestamp = DateTime.UtcNow,
                version = "1.0.0",
                components = new Dictionary<string, object>()
            };

            // Check Orleans cluster connectivity
            try
            {
                var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
                var providers = await modelManager.GetAvailableExecutionProvidersAsync();
                
                healthStatus.components["orleans_cluster"] = new
                {
                    status = "healthy",
                    available_execution_providers = providers
                };
            }
            catch (Exception ex)
            {
                healthStatus.components["orleans_cluster"] = new
                {
                    status = "unhealthy",
                    error = ex.Message
                };
            }

            // Check model availability
            try
            {
                var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
                var models = new[] { "table-structure-recognition", "table-detection" };
                var modelHealth = new Dictionary<string, object>();
                
                foreach (var modelType in models)
                {
                    var isLoaded = await modelManager.IsModelLoadedAsync(modelType);
                    var memoryUsage = isLoaded ? await modelManager.GetModelMemoryUsageAsync(modelType) : 0;
                    
                    modelHealth[modelType] = new
                    {
                        loaded = isLoaded,
                        memoryUsageMB = Math.Round(memoryUsage / (1024.0 * 1024.0), 2),
                        status = isLoaded ? "ready" : "not_loaded"
                    };
                }
                
                healthStatus.components["models"] = new
                {
                    status = "healthy",
                    details = modelHealth
                };
            }
            catch (Exception ex)
            {
                healthStatus.components["models"] = new
                {
                    status = "unhealthy",
                    error = ex.Message
                };
            }

            // Check system resources (basic)
            var process = System.Diagnostics.Process.GetCurrentProcess();
            healthStatus.components["system"] = new
            {
                status = "healthy",
                process_memory_mb = Math.Round(process.WorkingSet64 / (1024.0 * 1024.0), 2),
                threads = process.Threads.Count,
                uptime_seconds = (DateTime.Now - process.StartTime).TotalSeconds
            };

            return Ok(healthStatus);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Health check failed");
            return StatusCode(500, new
            {
                status = "unhealthy",
                service = "autonomous-validation-orleans",
                timestamp = DateTime.UtcNow,
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Readiness check - indicates if the service is ready to handle requests
    /// </summary>
    [HttpGet("ready")]
    public async Task<ActionResult<object>> GetReadinessAsync()
    {
        try
        {
            // Test Orleans cluster connectivity
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            await modelManager.GetAvailableExecutionProvidersAsync();
            
            return Ok(new
            {
                status = "ready",
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Readiness check failed");
            return StatusCode(503, new
            {
                status = "not_ready",
                timestamp = DateTime.UtcNow,
                error = ex.Message
            });
        }
    }

    /// <summary>
    /// Liveness check - indicates if the service is alive
    /// </summary>
    [HttpGet("live")]
    public ActionResult<object> GetLiveness()
    {
        return Ok(new
        {
            status = "alive",
            timestamp = DateTime.UtcNow
        });
    }
}
