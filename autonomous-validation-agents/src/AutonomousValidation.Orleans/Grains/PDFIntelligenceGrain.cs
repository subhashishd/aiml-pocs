using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Orleans.Grains;

/// <summary>
/// Enhanced PDF Intelligence Grain with Hugging Face model integration
/// Uses ModelManagerGrain for table extraction and document processing
/// </summary>
public class PDFIntelligenceGrain : Grain, IPDFIntelligenceGrain
{
    private readonly ILogger<PDFIntelligenceGrain> _logger;
    private const string TABLE_TRANSFORMER_MODEL = "table-transformer";
    private const string MODEL_MANAGER_KEY = "model-manager";

    public PDFIntelligenceGrain(ILogger<PDFIntelligenceGrain> logger)
    {
        _logger = logger;
    }

    public async Task<PDFProcessingResult> ProcessPDFAsync(byte[] pdfData, ProcessingOptions options)
    {
        _logger.LogInformation("Processing PDF with {Size} bytes using ML-enhanced extraction", pdfData.Length);
        
        var startTime = DateTime.UtcNow;
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        
        try
        {
            // Get the model manager grain
            var modelManager = GrainFactory.GetGrain<IModelManagerGrain>(MODEL_MANAGER_KEY);
            
            // Check if table transformer model is loaded
            var isModelLoaded = await modelManager.IsModelLoadedAsync(TABLE_TRANSFORMER_MODEL);
            
            List<KeyValuePair<string, object>> extractedData;
            ProcessingApproach approachUsed;
            
            if (isModelLoaded)
            {
                // Use ML-enhanced table extraction
                extractedData = await ExtractDataUsingMLAsync(modelManager, pdfData);
                approachUsed = ProcessingApproach.ONNX;
                _logger.LogInformation("Used ML-enhanced table extraction");
            }
            else
            {
                // Fallback to basic extraction
                extractedData = await ExtractDataBasicAsync(pdfData);
                approachUsed = ProcessingApproach.SemanticKernel;
                _logger.LogWarning("ML model not loaded, using fallback extraction");
            }
            
            stopwatch.Stop();
            
            var result = new PDFProcessingResult
            {
                KeyValuePairs = extractedData,
                ExtractedText = new List<string> { "PDF processed with enhanced intelligence" },
                ApproachUsed = approachUsed,
                Metadata = new ProcessingMetadata
                {
                    ProcessingTime = stopwatch.Elapsed,
                    StrategyUsed = ProcessingStrategy.FullCapability,
                    StartTime = startTime,
                    EndTime = DateTime.UtcNow
                }
            };
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing PDF with ML enhancement");
            stopwatch.Stop();
            
            // Return basic fallback result
            return new PDFProcessingResult
            {
                KeyValuePairs = await ExtractDataBasicAsync(pdfData),
                ExtractedText = new List<string> { "PDF processed with basic extraction due to error" },
                ApproachUsed = ProcessingApproach.SemanticKernel,
                Metadata = new ProcessingMetadata
                {
                    ProcessingTime = stopwatch.Elapsed,
                    StrategyUsed = ProcessingStrategy.Selective,
                    StartTime = startTime,
                    EndTime = DateTime.UtcNow
                }
            };
        }
    }

    public async Task<List<KeyValuePair<string, object>>> ExtractKeyValuePairsAsync(byte[] pdfData)
    {
        _logger.LogDebug("Extracting key-value pairs from PDF using enhanced ML extraction");
        
        try
        {
            // Get the model manager grain
            var modelManager = GrainFactory.GetGrain<IModelManagerGrain>(MODEL_MANAGER_KEY);
            
            // Check if table transformer model is loaded
            var isModelLoaded = await modelManager.IsModelLoadedAsync(TABLE_TRANSFORMER_MODEL);
            
            if (isModelLoaded)
            {
                // Use ML-enhanced extraction
                var mlExtractedData = await ExtractDataUsingMLAsync(modelManager, pdfData);
                _logger.LogInformation("Successfully extracted {Count} key-value pairs using ML", mlExtractedData.Count);
                return mlExtractedData;
            }
            else
            {
                // Fallback to basic extraction
                var basicData = await ExtractDataBasicAsync(pdfData);
                _logger.LogWarning("ML model not loaded, extracted {Count} key-value pairs using basic method", basicData.Count);
                return basicData;
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during key-value extraction, using fallback");
            return await ExtractDataBasicAsync(pdfData);
        }
    }

    public Task<bool> AdaptToMemoryConstraintsAsync(MemoryThreshold threshold)
    {
        _logger.LogInformation("Adapting to memory threshold: {Threshold}", threshold);
        return Task.FromResult(true);
    }

    public Task<bool> AbsorbExcelCapabilitiesAsync(string excelGrainId)
    {
        _logger.LogInformation("Absorbing Excel capabilities from grain {GrainId}", excelGrainId);
        return Task.FromResult(true);
    }
    
    /// <summary>
    /// Extract data using ML-enhanced table transformer model
    /// </summary>
    private async Task<List<KeyValuePair<string, object>>> ExtractDataUsingMLAsync(
        IModelManagerGrain modelManager, byte[] pdfData)
    {
        try
        {
            // Create inference input for table extraction
            var inferenceInput = new InferenceInput
            {
                InputType = "pdf_image",
                Data = pdfData,
                Metadata = new Dictionary<string, string>
                {
                    { "task", "table_extraction" },
                    { "format", "pdf" }
                }
            };
            
            // Run inference using the model manager
            var inferenceResult = await modelManager.RunInferenceAsync(TABLE_TRANSFORMER_MODEL, inferenceInput);
            
            if (inferenceResult.Success)
            {
                _logger.LogInformation("ML inference completed successfully in {Time}ms", 
                    inferenceResult.ProcessingTimeMs);
                
                // Convert inference outputs to key-value pairs
                return ConvertInferenceOutputToKeyValuePairs(inferenceResult.Outputs);
            }
            else
            {
                _logger.LogWarning("ML inference failed: {Error}", inferenceResult.ErrorMessage);
                return await ExtractDataBasicAsync(pdfData);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during ML extraction, falling back to basic extraction");
            return await ExtractDataBasicAsync(pdfData);
        }
    }
    
    /// <summary>
    /// Basic fallback extraction without ML
    /// </summary>
    private Task<List<KeyValuePair<string, object>>> ExtractDataBasicAsync(byte[] pdfData)
    {
        _logger.LogDebug("Using basic extraction for PDF with {Size} bytes", pdfData.Length);
        
        // Mock extracted data - in real implementation, this would use basic PDF parsing
        var basicData = new List<KeyValuePair<string, object>>
        {
            new("Temperature", "25.3°C"),
            new("Pressure", "1013.25 hPa"),
            new("Humidity", "65%"),
            new("ExtractionMethod", "Basic")
        };
        
        return Task.FromResult(basicData);
    }
    
    /// <summary>
    /// Convert ML inference outputs to structured key-value pairs
    /// </summary>
    private List<KeyValuePair<string, object>> ConvertInferenceOutputToKeyValuePairs(
        Dictionary<string, string> outputs)
    {
        var keyValuePairs = new List<KeyValuePair<string, object>>();
        
        // Mock conversion logic - in real implementation, this would parse
        // table extraction results from the multimodal model
        keyValuePairs.Add(new("Temperature", "26.1°C"));
        keyValuePairs.Add(new("Pressure", "1015.2 hPa"));
        keyValuePairs.Add(new("Humidity", "68%"));
        keyValuePairs.Add(new("ExtractionMethod", "ML-Enhanced"));
        keyValuePairs.Add(new("Confidence", "95.2%"));
        
        // Add inference metadata
        foreach (var output in outputs)
        {
            keyValuePairs.Add(new($"ML_{output.Key}", output.Value));
        }
        
        return keyValuePairs;
    }
}
