using Microsoft.AspNetCore.Mvc;
using Orleans;
using AutonomousValidation.Orleans.Interfaces;
using AutonomousValidation.Core.Models;

namespace AutonomousValidation.Orleans.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ModelsController : ControllerBase
{
    private readonly IClusterClient _clusterClient;
    private readonly ILogger<ModelsController> _logger;

    public ModelsController(IClusterClient clusterClient, ILogger<ModelsController> logger)
    {
        _clusterClient = clusterClient;
        _logger = logger;
    }

    /// <summary>
    /// Get the status of all models
    /// </summary>
    [HttpGet("status")]
    public async Task<ActionResult<object>> GetModelStatusAsync()
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            
            var models = new[] { "table-structure-recognition", "table-detection" };
            var modelStatus = new Dictionary<string, object>();
            
            foreach (var modelType in models)
            {
                var isLoaded = await modelManager.IsModelLoadedAsync(modelType);
                var memoryUsage = isLoaded ? await modelManager.GetModelMemoryUsageAsync(modelType) : 0;
                
                modelStatus[modelType] = new
                {
                    loaded = isLoaded,
                    memoryUsageBytes = memoryUsage,
                    memoryUsageMB = Math.Round(memoryUsage / (1024.0 * 1024.0), 2)
                };
            }

            var providers = await modelManager.GetAvailableExecutionProvidersAsync();

            return Ok(new
            {
                models = modelStatus,
                availableExecutionProviders = providers,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get model status");
            return StatusCode(500, new { error = "Failed to get model status", message = ex.Message });
        }
    }

    /// <summary>
    /// Load a specific model
    /// </summary>
    [HttpPost("{modelType}/load")]
    public async Task<ActionResult<object>> LoadModelAsync(string modelType)
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            
            // Construct model path based on our known structure
            var modelPath = $"/models/huggingface/{modelType}/model.onnx";
            
            var success = await modelManager.LoadModelAsync(modelPath, modelType);
            
            if (success)
            {
                var memoryUsage = await modelManager.GetModelMemoryUsageAsync(modelType);
                return Ok(new
                {
                    success = true,
                    message = $"Model '{modelType}' loaded successfully",
                    modelPath = modelPath,
                    memoryUsageBytes = memoryUsage,
                    memoryUsageMB = Math.Round(memoryUsage / (1024.0 * 1024.0), 2),
                    timestamp = DateTime.UtcNow
                });
            }
            else
            {
                return BadRequest(new
                {
                    success = false,
                    message = $"Failed to load model '{modelType}'"
                });
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load model {ModelType}", modelType);
            return StatusCode(500, new { error = "Failed to load model", message = ex.Message });
        }
    }

    /// <summary>
    /// Unload a specific model
    /// </summary>
    [HttpPost("{modelType}/unload")]
    public async Task<ActionResult<object>> UnloadModelAsync(string modelType)
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            var success = await modelManager.UnloadModelAsync(modelType);
            
            return Ok(new
            {
                success = success,
                message = success 
                    ? $"Model '{modelType}' unloaded successfully"
                    : $"Model '{modelType}' was not loaded",
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to unload model {ModelType}", modelType);
            return StatusCode(500, new { error = "Failed to unload model", message = ex.Message });
        }
    }

    /// <summary>
    /// Run inference on a specific model
    /// </summary>
    [HttpPost("{modelType}/inference")]
    public async Task<ActionResult<object>> RunInferenceAsync(string modelType, [FromBody] object? inputData = null)
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            
            // For now, create a dummy input since we don't have real image processing yet
            // Create a mock image byte array (800x600x3 = 1,440,000 bytes for RGB image)
            var mockImageData = new byte[800 * 600 * 3];
            // Fill with some mock data to simulate an image
            for (int i = 0; i < mockImageData.Length; i++)
            {
                mockImageData[i] = (byte)(i % 256);
            }
            
            var input = new InferenceInput
            {
                InputType = "table_image",
                Data = mockImageData,
                Dimensions = new int[] { 800, 600, 3 },
                Metadata = new Dictionary<string, string>
                {
                    ["width"] = "800",
                    ["height"] = "600",
                    ["channels"] = "3",
                    ["format"] = "RGB",
                    ["mock_input"] = "true",
                    ["user_input"] = inputData?.ToString() ?? "sample_table_image"
                }
            };

            var result = await modelManager.RunInferenceAsync(modelType, input);
            
            return Ok(new
            {
                success = result.Success,
                modelType = modelType,
                processingTimeMs = result.ProcessingTimeMs,
                memoryUsageBytes = result.MemoryUsageBytes,
                memoryUsageMB = Math.Round(result.MemoryUsageBytes / (1024.0 * 1024.0), 2),
                outputs = result.Outputs,
                confidence = result.Confidence,
                errorMessage = result.ErrorMessage,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to run inference on model {ModelType}", modelType);
            return StatusCode(500, new { error = "Failed to run inference", message = ex.Message });
        }
    }

    /// <summary>
    /// Load all available models
    /// </summary>
    [HttpPost("load-all")]
    public async Task<ActionResult<object>> LoadAllModelsAsync()
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            var models = new[] { "table-structure-recognition", "table-detection" };
            var results = new Dictionary<string, object>();
            
            foreach (var modelType in models)
            {
                var modelPath = $"/models/huggingface/{modelType}/model.onnx";
                var success = await modelManager.LoadModelAsync(modelPath, modelType);
                
                results[modelType] = new
                {
                    success = success,
                    path = modelPath
                };
            }
            
            return Ok(new
            {
                message = "Bulk model loading completed",
                results = results,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to load all models");
            return StatusCode(500, new { error = "Failed to load all models", message = ex.Message });
        }
    }

    /// <summary>
    /// Get available execution providers
    /// </summary>
    [HttpGet("execution-providers")]
    public async Task<ActionResult<object>> GetExecutionProvidersAsync()
    {
        try
        {
            var modelManager = _clusterClient.GetGrain<IModelManagerGrain>("model-manager");
            var providers = await modelManager.GetAvailableExecutionProvidersAsync();
            
            return Ok(new
            {
                providers = providers,
                timestamp = DateTime.UtcNow
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to get execution providers");
            return StatusCode(500, new { error = "Failed to get execution providers", message = ex.Message });
        }
    }
}
