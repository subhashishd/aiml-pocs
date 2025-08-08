# Technical Architecture: Orleans + Semantic Kernel Autonomous Validation System

## Architecture Overview

This document provides the detailed technical implementation strategy for the autonomous validation system using Microsoft Orleans, Semantic Kernel, and hybrid ML inference with Python microservices.

## Core Grain Definitions

### 1. OrchestratorGrain
```csharp
public interface IOrchestratorGrain : IGrainWithStringKey
{
    Task<ValidationResult> ProcessValidationRequestAsync(ValidationRequest request);
    Task<ResourceStatus> GetCurrentResourceStatusAsync();
    Task<bool> AdaptToResourceConstraintsAsync(MemoryThreshold threshold);
}

public class OrchestratorGrain : Grain, IOrchestratorGrain
{
    private readonly ISemanticKernel _kernel;
    private readonly IResourceManagerGrain _resourceManager;
    private readonly ILogger<OrchestratorGrain> _logger;
    
    // Memory-aware orchestration logic
    private async Task<ProcessingStrategy> DetermineProcessingStrategyAsync()
    {
        var resourceStatus = await _resourceManager.GetResourceStatusAsync();
        return resourceStatus.AvailableMemoryGB switch
        {
            >= 6 => ProcessingStrategy.FullCapability,
            >= 3 => ProcessingStrategy.Selective,
            >= 1 => ProcessingStrategy.Consolidated,
            _ => ProcessingStrategy.Minimal
        };
    }
}
```

### 2. ResourceManagerGrain
```csharp
public interface IResourceManagerGrain : IGrainWithIntegerKey
{
    Task<ResourceStatus> GetResourceStatusAsync();
    Task<bool> CanSpawnSubAgentAsync(AgentType agentType);
    Task RegisterGrainMemoryUsageAsync(string grainId, long memoryBytes);
    Task<ConsolidationRecommendation> GetConsolidationRecommendationAsync();
}

public class ResourceManagerGrain : Grain, IResourceManagerGrain
{
    private readonly MemoryMonitor _memoryMonitor;
    private readonly Dictionary<string, long> _grainMemoryUsage = new();
    private const long SAFETY_BUFFER_BYTES = 512 * 1024 * 1024; // 512MB buffer
    
    // Predictive memory allocation for sub-agents
    private readonly Dictionary<AgentType, long> _agentMemoryEstimates = new()
    {
        { AgentType.SemanticKernel, 200 * 1024 * 1024 }, // 200MB
        { AgentType.OCRProcessor, 150 * 1024 * 1024 },   // 150MB
        { AgentType.MultimodalProcessor, 300 * 1024 * 1024 }, // 300MB
        { AgentType.ValidationEngine, 100 * 1024 * 1024 }     // 100MB
    };
}
```

### 3. PDFIntelligenceGrain
```csharp
public interface IPDFIntelligenceGrain : IGrainWithStringKey
{
    Task<PDFProcessingResult> ProcessPDFAsync(byte[] pdfData, ProcessingOptions options);
    Task<bool> AdaptToMemoryConstraintsAsync(MemoryThreshold threshold);
    Task<List<KeyValuePair<string, object>>> ExtractKeyValuePairsAsync(byte[] pdfData);
}

public class PDFIntelligenceGrain : Grain, IPDFIntelligenceGrain
{
    private readonly ISemanticKernel _kernel;
    private readonly IPythonMLServiceClient _pythonMLClient;
    private readonly IONNXModelService _onnxService;
    private readonly IResourceManagerGrain _resourceManager;
    
    private ProcessingCapability _currentCapability = ProcessingCapability.Full;
    
    public async Task<PDFProcessingResult> ProcessPDFAsync(byte[] pdfData, ProcessingOptions options)
    {
        var strategy = await DetermineProcessingApproachAsync();
        
        return strategy switch
        {
            ProcessingApproach.SemanticKernel => await ProcessWithSemanticKernelAsync(pdfData),
            ProcessingApproach.PythonML => await ProcessWithPythonMLAsync(pdfData),
            ProcessingApproach.ONNX => await ProcessWithONNXAsync(pdfData),
            ProcessingApproach.Traditional => await ProcessTraditionallyAsync(pdfData),
            _ => throw new InvalidOperationException("Unknown processing approach")
        };
    }
    
    private async Task<ProcessingApproach> DetermineProcessingApproachAsync()
    {
        var resourceStatus = await _resourceManager.GetResourceStatusAsync();
        
        // Memory-based decision tree
        if (resourceStatus.AvailableMemoryGB >= 2 && _kernel.IsInitialized)
            return ProcessingApproach.SemanticKernel;
        
        if (resourceStatus.AvailableMemoryGB >= 1 && await _pythonMLClient.IsAvailableAsync())
            return ProcessingApproach.PythonML;
        
        if (_onnxService.IsModelLoaded)
            return ProcessingApproach.ONNX;
        
        return ProcessingApproach.Traditional;
    }
    
    // Sub-agent spawning logic
    private async Task<MultimodalResult> ProcessWithSubAgentsAsync(byte[] pdfData)
    {
        var tasks = new List<Task>();
        
        if (await _resourceManager.CanSpawnSubAgentAsync(AgentType.OCRProcessor))
        {
            var ocrGrain = GrainFactory.GetGrain<IOCRProcessorGrain>(Guid.NewGuid().ToString());
            tasks.Add(ocrGrain.ExtractTextAsync(pdfData));
        }
        
        if (await _resourceManager.CanSpawnSubAgentAsync(AgentType.MultimodalProcessor))
        {
            var multimodalGrain = GrainFactory.GetGrain<IMultimodalProcessorGrain>(Guid.NewGuid().ToString());
            tasks.Add(multimodalGrain.ProcessVisualContentAsync(pdfData));
        }
        
        await Task.WhenAll(tasks);
        
        // Consolidate results
        return await ConsolidateResultsAsync(tasks);
    }
}
```

### 4. ExcelIntelligenceGrain
```csharp
public interface IExcelIntelligenceGrain : IGrainWithStringKey
{
    Task<ExcelProcessingResult> ProcessExcelAsync(byte[] excelData, ProcessingOptions options);
    Task<List<ExcelParameter>> ExtractParametersAsync(byte[] excelData);
    Task<bool> ConsolidateWithPDFGrainAsync(string pdfGrainId);
}

public class ExcelIntelligenceGrain : Grain, IExcelIntelligenceGrain
{
    private readonly ISemanticKernel _kernel;
    private readonly IExcelProcessingService _excelService;
    private readonly OutputCache<ExcelProcessingResult> _cache = new();
    
    // Memory-aware processing with capability consolidation
    public async Task<bool> ConsolidateWithPDFGrainAsync(string pdfGrainId)
    {
        var pdfGrain = GrainFactory.GetGrain<IPDFIntelligenceGrain>(pdfGrainId);
        
        // Transfer capabilities to PDF grain for unified document processing
        await pdfGrain.AbsorbExcelCapabilitiesAsync(this.GetPrimaryKeyString());
        
        // Graceful shutdown with state preservation
        await this.DeactivateOnIdleAsync();
        return true;
    }
}
```

### 5. ValidationGrain
```csharp
public interface IValidationGrain : IGrainWithStringKey
{
    Task<ValidationResult> ValidateAsync(List<ExcelParameter> excelParams, 
                                        List<KeyValuePair<string, object>> pdfKeyValues);
    Task<MatchingResult> PerformSemanticMatchingAsync(string text1, string text2);
    Task<MatchingResult> PerformExactMatchingAsync(object value1, object value2, DataType dataType);
}

public class ValidationGrain : Grain, IValidationGrain
{
    private readonly ISemanticKernel _kernel;
    private readonly ISentenceTransformerService _embeddingService;
    private readonly IDataTypeClassifier _dataTypeClassifier;
    
    public async Task<ValidationResult> ValidateAsync(
        List<ExcelParameter> excelParams, 
        List<KeyValuePair<string, object>> pdfKeyValues)
    {
        var validationResults = new List<ParameterValidationResult>();
        
        foreach (var excelParam in excelParams)
        {
            var matchingPdfValue = await FindBestMatchAsync(excelParam, pdfKeyValues);
            
            if (matchingPdfValue != null)
            {
                var dataType = await _dataTypeClassifier.ClassifyAsync(excelParam.Value);
                
                var result = dataType switch
                {
                    DataType.Numerical or DataType.Currency or DataType.Measurement 
                        => await PerformExactMatchingAsync(excelParam.Value, matchingPdfValue.Value, dataType),
                    DataType.Text or DataType.Description 
                        => await PerformSemanticMatchingAsync(excelParam.Value.ToString(), matchingPdfValue.Value.ToString()),
                    _ => await PerformHybridMatchingAsync(excelParam.Value, matchingPdfValue.Value)
                };
                
                validationResults.Add(new ParameterValidationResult
                {
                    ExcelParameter = excelParam,
                    PDFValue = matchingPdfValue,
                    MatchResult = result,
                    DataType = dataType
                });
            }
        }
        
        return new ValidationResult
        {
            Results = validationResults,
            OverallScore = CalculateOverallScore(validationResults),
            ProcessingMetadata = await GetProcessingMetadataAsync()
        };
    }
    
    // Intelligent data type classification and matching strategy selection
    private async Task<KeyValuePair<string, object>?> FindBestMatchAsync(
        ExcelParameter excelParam, 
        List<KeyValuePair<string, object>> pdfKeyValues)
    {
        // Use Semantic Kernel for intelligent matching
        var prompt = $"""
            Find the best match for Excel parameter '{excelParam.Name}' with value '{excelParam.Value}'
            from the following PDF key-value pairs:
            {string.Join("\n", pdfKeyValues.Select(kv => $"- {kv.Key}: {kv.Value}"))}
            
            Consider semantic similarity, data type compatibility, and contextual relevance.
            Return the key that best matches, or 'NO_MATCH' if no suitable match exists.
            """;
            
        var result = await _kernel.InvokePromptAsync(prompt);
        
        // Parse result and return matching PDF key-value pair
        return ParseMatchingResult(result.ToString(), pdfKeyValues);
    }
}
```

## Semantic Kernel Integration Patterns

### 1. SK Agent Configuration
```csharp
public class SemanticKernelConfiguration
{
    public static ISemanticKernel CreateKernel(MemoryThreshold memoryThreshold)
    {
        var builder = Kernel.CreateBuilder();
        
        return memoryThreshold switch
        {
            MemoryThreshold.High => ConfigureHighMemoryKernel(builder),
            MemoryThreshold.Medium => ConfigureMediumMemoryKernel(builder),
            MemoryThreshold.Low => ConfigureLowMemoryKernel(builder),
            _ => ConfigureMinimalKernel(builder)
        };
    }
    
    private static ISemanticKernel ConfigureHighMemoryKernel(IKernelBuilder builder)
    {
        // Full capabilities with local LLM models
        builder.AddOllamaTextGeneration("llama3.1", "http://localhost:11434");
        builder.Plugins.AddFromType<PDFAnalysisPlugin>();
        builder.Plugins.AddFromType<ExcelAnalysisPlugin>();
        builder.Plugins.AddFromType<ValidationPlugin>();
        
        return builder.Build();
    }
    
    private static ISemanticKernel ConfigureLowMemoryKernel(IKernelBuilder builder)
    {
        // Minimal configuration with ONNX models only
        builder.AddOnnxRuntimeGenAI("phi-3-mini", "./models/phi-3-mini.onnx");
        builder.Plugins.AddFromType<BasicValidationPlugin>();
        
        return builder.Build();
    }
}
```

### 2. SK Plugin Definitions
```csharp
[Description("Analyzes PDF content and extracts key-value pairs using multimodal understanding")]
public class PDFAnalysisPlugin
{
    [KernelFunction, Description("Extract structured data from PDF")]
    public async Task<List<KeyValuePair<string, object>>> ExtractKeyValuePairsAsync(
        [Description("PDF content as base64")] string pdfBase64,
        [Description("Extraction strategy")] ExtractionStrategy strategy = ExtractionStrategy.Comprehensive)
    {
        // Implementation using BLIP models, OCR, and structured extraction
        return await PerformMultimodalExtractionAsync(pdfBase64, strategy);
    }
    
    [KernelFunction, Description("Classify data types in extracted content")]
    public async Task<DataType> ClassifyDataTypeAsync(
        [Description("Value to classify")] object value,
        [Description("Context from surrounding text")] string context = "")
    {
        // Intelligent data type classification
        return await PerformDataTypeClassificationAsync(value, context);
    }
}

[Description("Performs intelligent validation with exact and semantic matching")]
public class ValidationPlugin
{
    [KernelFunction, Description("Validate Excel parameter against PDF content")]
    public async Task<ValidationResult> ValidateParameterAsync(
        [Description("Excel parameter name")] string paramName,
        [Description("Excel parameter value")] object paramValue,
        [Description("PDF key-value pairs as JSON")] string pdfContentJson)
    {
        // Comprehensive validation logic
        return await PerformIntelligentValidationAsync(paramName, paramValue, pdfContentJson);
    }
}
```

## Multi-Environment Deployment Configuration

### 1. Development Environment (MacBook 8GB)
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  orleans-host:
    build:
      context: .
      dockerfile: Dockerfile.dev
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - MEMORY_THRESHOLD=Low
      - SK_MODEL_PATH=/app/models/minimal
      - USE_PYTHON_ML=false
      - OLLAMA_ENDPOINT=http://host.docker.internal:11434
    volumes:
      - ./models/minimal:/app/models/minimal:ro
    ports:
      - "8080:80"
    mem_limit: 2g
    
  python-ml-service:
    build:
      context: ./python-ml-service
      dockerfile: Dockerfile
    environment:
      - MODEL_CACHE_DIR=/app/cache
      - USE_LIGHTWEIGHT_MODELS=true
    volumes:
      - ./model-cache:/app/cache:rw
    ports:
      - "8090:8000"
    mem_limit: 1g
    profiles: ["full"]  # Only start with 'full' profile
```

### 2. Production Environment (Oracle VM 24GB)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  orleans-silo-1:
    build:
      context: .
      dockerfile: Dockerfile.prod
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - MEMORY_THRESHOLD=High
      - SK_MODEL_PATH=/app/models/full
      - USE_PYTHON_ML=true
      - OLLAMA_ENDPOINT=http://ollama:11434
      - ORLEANS_CLUSTERING=Consul
      - CONSUL_ENDPOINT=http://consul:8500
    volumes:
      - ./models/full:/app/models/full:ro
      - orleans-data:/app/data
    ports:
      - "8080:80"
      - "11111:11111"
    mem_limit: 8g
    
  orleans-silo-2:
    extends: orleans-silo-1
    ports:
      - "8081:80"
      - "11112:11111"
      
  python-ml-service:
    build:
      context: ./python-ml-service
      dockerfile: Dockerfile.prod
    environment:
      - MODEL_CACHE_DIR=/app/cache
      - USE_FULL_MODELS=true
      - ENABLE_GPU=true
    volumes:
      - ./model-cache:/app/cache:rw
    ports:
      - "8090:8000"
    mem_limit: 4g
    deploy:
      replicas: 2
      
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    mem_limit: 6g
    
  consul:
    image: consul:latest
    ports:
      - "8500:8500"
    volumes:
      - consul-data:/consul/data

volumes:
  orleans-data:
  ollama-data:
  consul-data:
```

### 3. Multi-Stage Dockerfile
```dockerfile
# Dockerfile.dev
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["AutonomousValidation.Orleans/AutonomousValidation.Orleans.csproj", "AutonomousValidation.Orleans/"]
COPY ["AutonomousValidation.Core/AutonomousValidation.Core.csproj", "AutonomousValidation.Core/"]
RUN dotnet restore "AutonomousValidation.Orleans/AutonomousValidation.Orleans.csproj"

COPY . .
WORKDIR "/src/AutonomousValidation.Orleans"
RUN dotnet build "AutonomousValidation.Orleans.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "AutonomousValidation.Orleans.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Install minimal models for development
RUN mkdir -p /app/models/minimal
COPY ./models/minimal/ /app/models/minimal/

# Environment-specific configuration
ENV DOTNET_ENVIRONMENT=Development
ENV MEMORY_THRESHOLD=Low

ENTRYPOINT ["dotnet", "AutonomousValidation.Orleans.dll"]
```

## Python ML Service Integration

### 1. gRPC Service Definition
```protobuf
// ml_service.proto
syntax = "proto3";

package ml_service;

service MLInferenceService {
    rpc ProcessPDF(PDFProcessingRequest) returns (PDFProcessingResponse);
    rpc ExtractKeyValues(KeyValueExtractionRequest) returns (KeyValueExtractionResponse);
    rpc PerformSemanticMatching(SemanticMatchingRequest) returns (SemanticMatchingResponse);
    rpc ClassifyDataType(DataTypeClassificationRequest) returns (DataTypeClassificationResponse);
}

message PDFProcessingRequest {
    bytes pdf_data = 1;
    ProcessingOptions options = 2;
}

message PDFProcessingResponse {
    repeated KeyValuePair key_values = 1;
    ProcessingMetadata metadata = 2;
}
```

### 2. .NET gRPC Client
```csharp
public class PythonMLServiceClient : IPythonMLServiceClient
{
    private readonly MLInferenceService.MLInferenceServiceClient _client;
    private readonly ILogger<PythonMLServiceClient> _logger;
    
    public async Task<List<KeyValuePair<string, object>>> ProcessPDFAsync(
        byte[] pdfData, 
        ProcessingOptions options)
    {
        try
        {
            var request = new PDFProcessingRequest
            {
                PdfData = Google.Protobuf.ByteString.CopyFrom(pdfData),
                Options = MapToProtoOptions(options)
            };
            
            var response = await _client.ProcessPDFAsync(request);
            return MapFromProtoResponse(response);
        }
        catch (RpcException ex) when (ex.StatusCode == StatusCode.Unavailable)
        {
            _logger.LogWarning("Python ML service unavailable, falling back to ONNX models");
            throw new MLServiceUnavailableException("Python ML service is not available", ex);
        }
    }
}
```

## Resource Management and Monitoring

### 1. Memory Monitoring Service
```csharp
public class MemoryMonitoringService : BackgroundService
{
    private readonly IResourceManagerGrain _resourceManager;
    private readonly ILogger<MemoryMonitoringService> _logger;
    private readonly PerformanceCounter _memoryCounter;
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            var currentMemoryUsage = GC.GetTotalMemory(false);
            var availableMemory = GetAvailableMemory();
            
            await _resourceManager.UpdateMemoryStatusAsync(new MemoryStatus
            {
                UsedMemoryBytes = currentMemoryUsage,
                AvailableMemoryBytes = availableMemory,
                Timestamp = DateTime.UtcNow
            });
            
            // Check for memory pressure and trigger adaptations
            if (availableMemory < MEMORY_PRESSURE_THRESHOLD)
            {
                await TriggerMemoryPressureAdaptationAsync();
            }
            
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
        }
    }
    
    private async Task TriggerMemoryPressureAdaptationAsync()
    {
        var activeGrains = await GetActiveGrainsAsync();
        
        foreach (var grain in activeGrains)
        {
            if (grain is IAdaptiveGrain adaptiveGrain)
            {
                await adaptiveGrain.AdaptToMemoryConstraintsAsync(MemoryThreshold.Low);
            }
        }
        
        // Force garbage collection
        GC.Collect();
        GC.WaitForPendingFinalizers();
        GC.Collect();
    }
}
```

### 2. Dynamic Model Management
```csharp
public class ModelManager : IModelManager
{
    private readonly ConcurrentDictionary<string, IModel> _loadedModels = new();
    private readonly IMemoryMonitor _memoryMonitor;
    private readonly ModelConfiguration _config;
    
    public async Task<TModel> GetModelAsync<TModel>(string modelId) where TModel : class, IModel
    {
        if (_loadedModels.TryGetValue(modelId, out var existingModel))
        {
            return (TModel)existingModel;
        }
        
        // Check memory availability before loading
        var modelMemoryRequirement = _config.GetModelMemoryRequirement(modelId);
        if (!await _memoryMonitor.CanAllocateAsync(modelMemoryRequirement))
        {
            await UnloadLeastRecentlyUsedModelAsync();
        }
        
        var model = await LoadModelAsync<TModel>(modelId);
        _loadedModels.TryAdd(modelId, model);
        
        return model;
    }
    
    public async Task UnloadModelAsync(string modelId)
    {
        if (_loadedModels.TryRemove(modelId, out var model))
        {
            if (model is IDisposable disposable)
            {
                disposable.Dispose();
            }
            
            // Force garbage collection to free memory immediately
            GC.Collect();
            await Task.Delay(100); // Allow GC to complete
        }
    }
}
```

This technical architecture provides a comprehensive implementation strategy that combines the power of Orleans distributed computing, Semantic Kernel AI orchestration, and hybrid ML inference while maintaining adaptive memory management for deployment across different resource environments.
