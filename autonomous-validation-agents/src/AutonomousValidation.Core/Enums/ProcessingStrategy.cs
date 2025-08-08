namespace AutonomousValidation.Core.Enums;

/// <summary>
/// Defines different processing strategies based on available resources
/// </summary>
public enum ProcessingStrategy
{
    /// <summary>
    /// Minimal processing with basic functionality only
    /// </summary>
    Minimal = 0,
    
    /// <summary>
    /// Consolidated processing with merged agent capabilities
    /// </summary>
    Consolidated = 1,
    
    /// <summary>
    /// Selective processing with some sub-agent delegation
    /// </summary>
    Selective = 2,
    
    /// <summary>
    /// Full capability processing with all sub-agents
    /// </summary>
    FullCapability = 3
}

/// <summary>
/// Defines different processing approaches for ML inference
/// </summary>
public enum ProcessingApproach
{
    /// <summary>
    /// Traditional text-based processing without ML
    /// </summary>
    Traditional = 0,
    
    /// <summary>
    /// ONNX model inference in .NET
    /// </summary>
    ONNX = 1,
    
    /// <summary>
    /// Python ML service via gRPC
    /// </summary>
    PythonML = 2,
    
    /// <summary>
    /// Semantic Kernel orchestrated processing
    /// </summary>
    SemanticKernel = 3
}

/// <summary>
/// Defines data types for intelligent matching strategy selection
/// </summary>
public enum DataType
{
    /// <summary>
    /// Unknown or unclassified data type
    /// </summary>
    Unknown = 0,
    
    /// <summary>
    /// Numerical values (integers, floats)
    /// </summary>
    Numerical = 1,
    
    /// <summary>
    /// Currency values
    /// </summary>
    Currency = 2,
    
    /// <summary>
    /// Measurements and quantities
    /// </summary>
    Measurement = 3,
    
    /// <summary>
    /// Date and time values
    /// </summary>
    DateTime = 4,
    
    /// <summary>
    /// Text descriptions
    /// </summary>
    Text = 5,
    
    /// <summary>
    /// Long form descriptions
    /// </summary>
    Description = 6,
    
    /// <summary>
    /// Categorical labels
    /// </summary>
    Categorical = 7,
    
    /// <summary>
    /// Identifier values
    /// </summary>
    Identifier = 8
}

/// <summary>
/// Defines agent types for resource management
/// </summary>
public enum AgentType
{
    /// <summary>
    /// Main orchestrator agent
    /// </summary>
    Orchestrator = 0,
    
    /// <summary>
    /// Resource manager agent
    /// </summary>
    ResourceManager = 1,
    
    /// <summary>
    /// PDF intelligence agent
    /// </summary>
    PDFIntelligence = 2,
    
    /// <summary>
    /// Excel intelligence agent
    /// </summary>
    ExcelIntelligence = 3,
    
    /// <summary>
    /// Validation agent
    /// </summary>
    Validation = 4,
    
    /// <summary>
    /// OCR processor sub-agent
    /// </summary>
    OCRProcessor = 5,
    
    /// <summary>
    /// Multimodal processor sub-agent
    /// </summary>
    MultimodalProcessor = 6,
    
    /// <summary>
    /// Semantic kernel agent
    /// </summary>
    SemanticKernel = 7,
    
    /// <summary>
    /// Validation engine sub-agent
    /// </summary>
    ValidationEngine = 8
}

/// <summary>
/// Defines consolidation actions for memory management
/// </summary>
public enum ConsolidationAction
{
    /// <summary>
    /// No action needed
    /// </summary>
    NoAction = 0,
    
    /// <summary>
    /// Selective consolidation of some agents
    /// </summary>
    SelectiveConsolidation = 1,
    
    /// <summary>
    /// Recommend consolidation
    /// </summary>
    RecommendConsolidation = 2,
    
    /// <summary>
    /// Immediate consolidation required
    /// </summary>
    ImmediateConsolidation = 3
}

/// <summary>
/// Defines processing steps in the validation workflow
/// </summary>
public enum ProcessingStep
{
    /// <summary>
    /// No processing active
    /// </summary>
    Idle = 0,
    
    /// <summary>
    /// Analyzing uploaded files
    /// </summary>
    FileAnalysis = 1,
    
    /// <summary>
    /// Extracting data from PDF
    /// </summary>
    PDFExtraction = 2,
    
    /// <summary>
    /// Processing Excel data
    /// </summary>
    ExcelProcessing = 3,
    
    /// <summary>
    /// Performing validation
    /// </summary>
    Validation = 4,
    
    /// <summary>
    /// Generating final report
    /// </summary>
    ReportGeneration = 5,
    
    /// <summary>
    /// Processing complete
    /// </summary>
    Complete = 6
}

/// <summary>
/// Defines memory usage modes
/// </summary>
public enum MemoryMode
{
    /// <summary>
    /// Low memory mode with minimal features
    /// </summary>
    Low = 0,
    
    /// <summary>
    /// Medium memory mode with balanced features
    /// </summary>
    Medium = 1,
    
    /// <summary>
    /// High memory mode with full features
    /// </summary>
    High = 2
}
