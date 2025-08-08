using Orleans;
using AutonomousValidation.Core.Models;

namespace AutonomousValidation.Orleans.Interfaces;

/// <summary>
/// Model manager grain interface for Hugging Face model lifecycle
/// </summary>
public interface IModelManagerGrain : IGrainWithStringKey
{
    /// <summary>
    /// Load ONNX model for inference
    /// </summary>
    Task<bool> LoadModelAsync(string modelPath, string modelType);
    
    /// <summary>
    /// Unload model to free memory
    /// </summary>
    Task<bool> UnloadModelAsync(string modelType);
    
    /// <summary>
    /// Check if model is loaded and ready
    /// </summary>
    Task<bool> IsModelLoadedAsync(string modelType);
    
    /// <summary>
    /// Get model memory usage
    /// </summary>
    Task<long> GetModelMemoryUsageAsync(string modelType);
    
    /// <summary>
    /// Perform inference using loaded model
    /// </summary>
    Task<InferenceResult> RunInferenceAsync(string modelType, InferenceInput input);
    
    /// <summary>
    /// Get available execution providers
    /// </summary>
    Task<List<string>> GetAvailableExecutionProvidersAsync();
    
    /// <summary>
    /// Switch execution provider (CPU, CoreML, etc.)
    /// </summary>
    Task<bool> SetExecutionProviderAsync(string provider);
}
