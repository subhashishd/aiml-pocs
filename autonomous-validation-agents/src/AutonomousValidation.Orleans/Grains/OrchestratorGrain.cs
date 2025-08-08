using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Orleans.Grains;

/// <summary>
/// Simplified Orchestrator Grain implementation for Phase 1
/// </summary>
public class OrchestratorGrain : Grain, IOrchestratorGrain
{
    private readonly ILogger<OrchestratorGrain> _logger;
    private IResourceManagerGrain? _resourceManager;
    private IPDFIntelligenceGrain? _pdfGrain;
    private IExcelIntelligenceGrain? _excelGrain;
    private IValidationGrain? _validationGrain;
    
    // State fields for tracking processing
    private ValidationRequest? _currentRequest;
    private ProcessingMetadata? _processingMetadata;
    private readonly Dictionary<string, object> _processingContext = new();

    public OrchestratorGrain(ILogger<OrchestratorGrain> logger)
    {
        _logger = logger;
    }

    public async Task<ValidationResult> ProcessValidationRequestAsync(ValidationRequest request)
    {
        try
        {
            _logger.LogInformation("Starting validation request processing for session {RequestId}", request.RequestId);
            
            _currentRequest = request;
            _processingMetadata = new ProcessingMetadata
            {
                StartTime = DateTime.UtcNow,
                StrategyUsed = ProcessingStrategy.Selective
            };

            // Step 1: Initialize resource management and determine strategy
            var processingStrategy = await DetermineProcessingStrategyAsync();
            _logger.LogInformation("Determined processing strategy: {Strategy}", processingStrategy);

            // Step 2: Process files based on strategy
            var (pdfResults, excelResults) = await ProcessFilesAsync(request, processingStrategy);
            
            // Step 3: Perform validation
            var validationResults = await PerformValidationAsync(pdfResults, excelResults);

            // Step 4: Generate final results
            var finalResult = await GenerateFinalResultAsync(validationResults, request);

            _logger.LogInformation("Completed validation processing for session {RequestId} in {Duration}ms", 
                request.RequestId, (DateTime.UtcNow - _processingMetadata.StartTime).TotalMilliseconds);

            return finalResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing validation request for session {RequestId}", request.RequestId);
            
            return new ValidationResult
            {
                RequestId = request.RequestId,
                Errors = new List<string> { ex.Message },
                ProcessingMetadata = _processingMetadata ?? new ProcessingMetadata()
            };
        }
    }

    public async Task<ResourceStatus> GetCurrentResourceStatusAsync()
    {
        await EnsureResourceManagerAsync();
        return await _resourceManager!.GetResourceStatusAsync();
    }

    public async Task<bool> AdaptToResourceConstraintsAsync(MemoryThreshold threshold)
    {
        _logger.LogInformation("Adapting to resource constraints: {Threshold}", threshold);
        
        try
        {
            // Get consolidation recommendations
            await EnsureResourceManagerAsync();
            var recommendation = await _resourceManager!.GetConsolidationRecommendationAsync();
            
            // Apply consolidation based on threshold
            switch (threshold)
            {
                case MemoryThreshold.Critical:
                    await ApplyCriticalMemoryAdaptationAsync();
                    break;
                case MemoryThreshold.Low:
                    await ApplyLowMemoryAdaptationAsync();
                    break;
                case MemoryThreshold.Medium:
                    await ApplyMediumMemoryAdaptationAsync();
                    break;
                default:
                    _logger.LogDebug("No adaptation needed for threshold {Threshold}", threshold);
                    break;
            }

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to adapt to resource constraints");
            return false;
        }
    }

    public Task<string> GetProcessingStatusAsync()
    {
        var metadata = _processingMetadata ?? new ProcessingMetadata 
        { 
            StartTime = DateTime.UtcNow,
            StrategyUsed = ProcessingStrategy.Selective
        };
        
        var status = $"Session: {this.GetPrimaryKeyString()}, Strategy: {metadata.StrategyUsed}, Started: {metadata.StartTime:yyyy-MM-dd HH:mm:ss}";
        return Task.FromResult(status);
    }

    #region Private Methods

    private async Task<ProcessingStrategy> DetermineProcessingStrategyAsync()
    {
        await EnsureResourceManagerAsync();
        var resourceStatus = await _resourceManager!.GetResourceStatusAsync();
        
        var strategy = resourceStatus.CurrentThreshold switch
        {
            MemoryThreshold.High => ProcessingStrategy.FullCapability,
            MemoryThreshold.Medium => ProcessingStrategy.Selective,
            MemoryThreshold.Low => ProcessingStrategy.Consolidated,
            MemoryThreshold.Critical => ProcessingStrategy.Minimal,
            _ => ProcessingStrategy.Selective
        };

        // Store strategy in processing context
        _processingContext["ProcessingStrategy"] = strategy;
        _processingContext["MemoryThreshold"] = resourceStatus.CurrentThreshold;
        
        return strategy;
    }

    private async Task<(PDFProcessingResult pdfResults, ExcelProcessingResult excelResults)> ProcessFilesAsync(
        ValidationRequest request, 
        ProcessingStrategy strategy)
    {
        _logger.LogDebug("Processing files with strategy: {Strategy}", strategy);
        
        UpdateProcessingStep(ProcessingStep.PDFExtraction);
        
        // Use the request's processing options or create new ones
        var processingOptions = request.Options;

        Task<PDFProcessingResult> pdfTask;
        Task<ExcelProcessingResult> excelTask;

        if (strategy == ProcessingStrategy.Consolidated || strategy == ProcessingStrategy.Minimal)
        {
            // Process sequentially to save memory
            _logger.LogDebug("Processing files sequentially due to memory constraints");
            
            var pdfResults = await ProcessPDFAsync(request.PdfData, processingOptions);
            
            UpdateProcessingStep(ProcessingStep.ExcelProcessing);
            var excelResults = await ProcessExcelAsync(request.ExcelData, processingOptions);
            
            return (pdfResults, excelResults);
        }
        else
        {
            // Process in parallel for better performance
            _logger.LogDebug("Processing files in parallel");
            
            pdfTask = ProcessPDFAsync(request.PdfData, processingOptions);
            excelTask = ProcessExcelAsync(request.ExcelData, processingOptions);
            
            UpdateProcessingStep(ProcessingStep.ExcelProcessing);
            
            await Task.WhenAll(pdfTask, excelTask);
            return (await pdfTask, await excelTask);
        }
    }

    private async Task<PDFProcessingResult> ProcessPDFAsync(byte[] pdfData, ProcessingOptions options)
    {
        await EnsurePDFGrainAsync();
        
        try
        {
            var result = await _pdfGrain!.ProcessPDFAsync(pdfData, options);
            
            // Register memory usage with resource manager
            await RegisterGrainMemoryUsageAsync("pdf-intelligence", EstimateGrainMemoryUsage(result));
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing PDF");
            return new PDFProcessingResult
            {
                Errors = new List<string> { ex.Message },
                Metadata = new ProcessingMetadata
                {
                    StartTime = DateTime.UtcNow,
                    EndTime = DateTime.UtcNow,
                    StrategyUsed = ProcessingStrategy.Selective
                }
            };
        }
    }

    private async Task<ExcelProcessingResult> ProcessExcelAsync(byte[] excelData, ProcessingOptions options)
    {
        await EnsureExcelGrainAsync();
        
        try
        {
            var result = await _excelGrain!.ProcessExcelAsync(excelData, options);
            
            // Register memory usage with resource manager
            await RegisterGrainMemoryUsageAsync("excel-intelligence", EstimateGrainMemoryUsage(result));
            
            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing Excel");
            return new ExcelProcessingResult
            {
                Errors = new List<string> { ex.Message },
                Metadata = new ProcessingMetadata
                {
                    StartTime = DateTime.UtcNow,
                    EndTime = DateTime.UtcNow,
                    StrategyUsed = ProcessingStrategy.Selective
                }
            };
        }
    }

    private async Task<ValidationResult> PerformValidationAsync(
        PDFProcessingResult pdfResults, 
        ExcelProcessingResult excelResults)
    {
        UpdateProcessingStep(ProcessingStep.Validation);
        
        await EnsureValidationGrainAsync();
        
        if (pdfResults.Errors.Any() || excelResults.Errors.Any())
        {
            var allErrors = new List<string>();
            allErrors.AddRange(pdfResults.Errors);
            allErrors.AddRange(excelResults.Errors);
            
            return new ValidationResult
            {
                RequestId = _currentRequest?.RequestId ?? "",
                Errors = allErrors,
                ProcessingMetadata = _processingMetadata ?? new ProcessingMetadata()
            };
        }

        try
        {
            var validationResult = await _validationGrain!.ValidateAsync(
                excelResults.Parameters, 
                pdfResults.KeyValuePairs);
            
            // Register validation grain memory usage
            await RegisterGrainMemoryUsageAsync("validation", EstimateValidationMemoryUsage(validationResult));
            
            return validationResult;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during validation");
            return new ValidationResult
            {
                RequestId = _currentRequest?.RequestId ?? "",
                Errors = new List<string> { ex.Message },
                ProcessingMetadata = _processingMetadata ?? new ProcessingMetadata()
            };
        }
    }

    private Task<ValidationResult> GenerateFinalResultAsync(
        ValidationResult validationResult, 
        ValidationRequest originalRequest)
    {
        UpdateProcessingStep(ProcessingStep.ReportGeneration);
        
        // Create enhanced processing metadata
        var enhancedMetadata = new ProcessingMetadata
        {
            StartTime = _processingMetadata?.StartTime ?? DateTime.UtcNow,
            EndTime = DateTime.UtcNow,
            StrategyUsed = _processingMetadata?.StrategyUsed ?? ProcessingStrategy.Selective,
            ApproachUsed = _processingMetadata?.ApproachUsed ?? ProcessingApproach.SemanticKernel,
            ProcessingTime = DateTime.UtcNow - (_processingMetadata?.StartTime ?? DateTime.UtcNow),
            AgentsInvolved = _processingMetadata?.AgentsInvolved ?? new List<AgentType>(),
            AdditionalMetrics = _processingMetadata?.AdditionalMetrics ?? new Dictionary<string, object>()
        };
        
        validationResult = validationResult with { ProcessingMetadata = enhancedMetadata };
        
        // Processing context information is already included in enhanced metadata
        
        _logger.LogInformation("Generated final result for session {RequestId}: {SuccessCount}/{TotalCount} matches", 
            originalRequest.RequestId, 
            validationResult.Results?.Count(r => r.MatchResult.IsMatch),
            validationResult.Results?.Count);
        
        return Task.FromResult(validationResult);
    }

    private void UpdateProcessingStep(ProcessingStep step)
    {
        // ProcessingStep tracking for logging only
        _logger.LogDebug("Processing step updated to: {Step}", step);
    }

    private static MemoryMode ConvertStrategyToMemoryMode(ProcessingStrategy strategy)
    {
        return strategy switch
        {
            ProcessingStrategy.FullCapability => MemoryMode.High,
            ProcessingStrategy.Selective => MemoryMode.Medium,
            ProcessingStrategy.Consolidated => MemoryMode.Low,
            ProcessingStrategy.Minimal => MemoryMode.Low,
            _ => MemoryMode.Medium
        };
    }

    #endregion

    #region Resource Adaptation Methods

    private async Task ApplyCriticalMemoryAdaptationAsync()
    {
        _logger.LogWarning("Applying critical memory adaptation - consolidating all agents");
        
        // In critical memory, orchestrator handles everything internally
        _pdfGrain = null;
        _excelGrain = null;
        _validationGrain = null;
        
        // Force garbage collection
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();
        
        await RegisterGrainMemoryUsageAsync("orchestrator", GC.GetTotalMemory(false));
    }

    private async Task ApplyLowMemoryAdaptationAsync()
    {
        _logger.LogInformation("Applying low memory adaptation - selective grain consolidation");
        
        // Keep only essential grains active
        await EnsureResourceManagerAsync();
        var recommendation = await _resourceManager!.GetConsolidationRecommendationAsync();
        
        if (recommendation.AgentsToConsolidate.Contains(AgentType.PDFIntelligence))
        {
            _pdfGrain = null;
        }
        
        // Trigger garbage collection
        GC.Collect();
    }

    private async Task ApplyMediumMemoryAdaptationAsync()
    {
        _logger.LogDebug("Applying medium memory adaptation - optimizing grain usage");
        
        // Just ensure we're not using more grains than necessary
        await RegisterGrainMemoryUsageAsync("orchestrator", GC.GetTotalMemory(false));
    }

    #endregion

    #region Grain Management

    private Task EnsureResourceManagerAsync()
    {
        _resourceManager ??= GrainFactory.GetGrain<IResourceManagerGrain>(0);
        return Task.CompletedTask;
    }

    private Task EnsurePDFGrainAsync()
    {
        if (_pdfGrain == null)
        {
            var sessionId = _currentRequest?.RequestId ?? this.GetPrimaryKeyString();
            _pdfGrain = GrainFactory.GetGrain<IPDFIntelligenceGrain>(sessionId);
        }
        return Task.CompletedTask;
    }

    private Task EnsureExcelGrainAsync()
    {
        if (_excelGrain == null)
        {
            var sessionId = _currentRequest?.RequestId ?? this.GetPrimaryKeyString();
            _excelGrain = GrainFactory.GetGrain<IExcelIntelligenceGrain>(sessionId);
        }
        return Task.CompletedTask;
    }

    private Task EnsureValidationGrainAsync()
    {
        if (_validationGrain == null)
        {
            var sessionId = _currentRequest?.RequestId ?? this.GetPrimaryKeyString();
            _validationGrain = GrainFactory.GetGrain<IValidationGrain>(sessionId);
        }
        return Task.CompletedTask;
    }

    private async Task RegisterGrainMemoryUsageAsync(string grainType, long memoryBytes)
    {
        await EnsureResourceManagerAsync();
        var grainId = $"{grainType}-{this.GetPrimaryKeyString()}";
        await _resourceManager!.RegisterGrainMemoryUsageAsync(grainId, memoryBytes);
    }

    #endregion

    #region Memory Estimation Helpers

    private static long EstimateGrainMemoryUsage(PDFProcessingResult result)
    {
        // Rough estimation based on result data size
        var baseSize = 50 * 1024 * 1024; // 50MB base
        var dataSize = result.KeyValuePairs?.Sum(kvp => kvp.Key.Length + kvp.Value?.ToString()?.Length ?? 0) ?? 0;
        return baseSize + (dataSize * 10); // Assume 10x overhead
    }

    private static long EstimateGrainMemoryUsage(ExcelProcessingResult result)
    {
        var baseSize = 30 * 1024 * 1024; // 30MB base
        var dataSize = result.Parameters?.Sum(p => p.Name.Length + p.Value?.ToString()?.Length ?? 0) ?? 0;
        return baseSize + (dataSize * 5); // Assume 5x overhead
    }

    private static long EstimateValidationMemoryUsage(ValidationResult result)
    {
        var baseSize = 20 * 1024 * 1024; // 20MB base
        var resultSize = result.Results?.Count * 1024 ?? 0; // Assume 1KB per result
        return baseSize + resultSize;
    }

    #endregion

    public override Task OnActivateAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("OrchestratorGrain activated for session {SessionId}", this.GetPrimaryKeyString());
        return base.OnActivateAsync(cancellationToken);
    }

    public override Task OnDeactivateAsync(DeactivationReason reason, CancellationToken cancellationToken)
    {
        _logger.LogInformation("OrchestratorGrain deactivated for session {SessionId}: {Reason}", 
            this.GetPrimaryKeyString(), reason);
        return base.OnDeactivateAsync(reason, cancellationToken);
    }
}
