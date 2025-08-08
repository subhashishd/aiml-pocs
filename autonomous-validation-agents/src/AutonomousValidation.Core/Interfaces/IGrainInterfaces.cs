using Orleans;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Core.Interfaces;

/// <summary>
/// Main orchestrator grain interface
/// </summary>
public interface IOrchestratorGrain : IGrainWithStringKey
{
    /// <summary>
    /// Process a validation request
    /// </summary>
    Task<ValidationResult> ProcessValidationRequestAsync(ValidationRequest request);
    
    /// <summary>
    /// Get current resource status
    /// </summary>
    Task<ResourceStatus> GetCurrentResourceStatusAsync();
    
    /// <summary>
    /// Adapt to resource constraints
    /// </summary>
    Task<bool> AdaptToResourceConstraintsAsync(MemoryThreshold threshold);
    
    /// <summary>
    /// Get processing status
    /// </summary>
    Task<string> GetProcessingStatusAsync();
}

/// <summary>
/// Resource manager grain interface
/// </summary>
public interface IResourceManagerGrain : IGrainWithIntegerKey
{
    /// <summary>
    /// Get current resource status
    /// </summary>
    Task<ResourceStatus> GetResourceStatusAsync();
    
    /// <summary>
    /// Check if sub-agent can be spawned
    /// </summary>
    Task<bool> CanSpawnSubAgentAsync(AgentType agentType);
    
    /// <summary>
    /// Register grain memory usage
    /// </summary>
    Task RegisterGrainMemoryUsageAsync(string grainId, long memoryBytes);
    
    /// <summary>
    /// Get consolidation recommendation
    /// </summary>
    Task<ConsolidationRecommendation> GetConsolidationRecommendationAsync();
    
    /// <summary>
    /// Update memory status
    /// </summary>
    Task UpdateMemoryStatusAsync(MemoryStatus status);
}

/// <summary>
/// PDF intelligence grain interface
/// </summary>
public interface IPDFIntelligenceGrain : IGrainWithStringKey
{
    /// <summary>
    /// Process PDF document
    /// </summary>
    Task<PDFProcessingResult> ProcessPDFAsync(byte[] pdfData, ProcessingOptions options);
    
    /// <summary>
    /// Extract key-value pairs from PDF
    /// </summary>
    Task<List<KeyValuePair<string, object>>> ExtractKeyValuePairsAsync(byte[] pdfData);
    
    /// <summary>
    /// Adapt to memory constraints
    /// </summary>
    Task<bool> AdaptToMemoryConstraintsAsync(MemoryThreshold threshold);
    
    /// <summary>
    /// Absorb Excel capabilities for consolidation
    /// </summary>
    Task<bool> AbsorbExcelCapabilitiesAsync(string excelGrainId);
}

/// <summary>
/// Excel intelligence grain interface
/// </summary>
public interface IExcelIntelligenceGrain : IGrainWithStringKey
{
    /// <summary>
    /// Process Excel document
    /// </summary>
    Task<ExcelProcessingResult> ProcessExcelAsync(byte[] excelData, ProcessingOptions options);
    
    /// <summary>
    /// Extract parameters from Excel
    /// </summary>
    Task<List<ExcelParameter>> ExtractParametersAsync(byte[] excelData);
    
    /// <summary>
    /// Consolidate with PDF grain
    /// </summary>
    Task<bool> ConsolidateWithPDFGrainAsync(string pdfGrainId);
}

/// <summary>
/// Validation grain interface
/// </summary>
public interface IValidationGrain : IGrainWithStringKey
{
    /// <summary>
    /// Validate Excel parameters against PDF content
    /// </summary>
    Task<ValidationResult> ValidateAsync(List<ExcelParameter> excelParams, 
                                        List<KeyValuePair<string, object>> pdfKeyValues);
    
    /// <summary>
    /// Perform semantic matching
    /// </summary>
    Task<MatchingResult> PerformSemanticMatchingAsync(string text1, string text2);
    
    /// <summary>
    /// Perform exact matching
    /// </summary>
    Task<MatchingResult> PerformExactMatchingAsync(object value1, object value2, DataType dataType);
}

/// <summary>
/// Sub-agent interface for OCR processing
/// </summary>
public interface IOCRProcessorGrain : IGrainWithStringKey
{
    /// <summary>
    /// Extract text from PDF using OCR
    /// </summary>
    Task<List<string>> ExtractTextAsync(byte[] pdfData);
}

/// <summary>
/// Sub-agent interface for multimodal processing
/// </summary>
public interface IMultimodalProcessorGrain : IGrainWithStringKey
{
    /// <summary>
    /// Process visual content from PDF
    /// </summary>
    Task<List<KeyValuePair<string, object>>> ProcessVisualContentAsync(byte[] pdfData);
}

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

/// <summary>
/// Base interface for adaptive grains
/// </summary>
public interface IAdaptiveGrain
{
    /// <summary>
    /// Adapt grain behavior to memory constraints
    /// </summary>
    Task<bool> AdaptToMemoryConstraintsAsync(MemoryThreshold threshold);
}
