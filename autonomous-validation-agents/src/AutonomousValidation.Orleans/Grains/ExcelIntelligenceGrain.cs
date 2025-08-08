using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Orleans.Grains;

/// <summary>
/// Basic stub implementation of Excel Intelligence Grain
/// </summary>
public class ExcelIntelligenceGrain : Grain, IExcelIntelligenceGrain
{
    private readonly ILogger<ExcelIntelligenceGrain> _logger;

    public ExcelIntelligenceGrain(ILogger<ExcelIntelligenceGrain> logger)
    {
        _logger = logger;
    }

    public Task<ExcelProcessingResult> ProcessExcelAsync(byte[] excelData, ProcessingOptions options)
    {
        _logger.LogInformation("Processing Excel with {Size} bytes", excelData.Length);
        
        var result = new ExcelProcessingResult
        {
            Parameters = new List<ExcelParameter>
            {
                new() { Name = "Temperature", Value = "25.3", EstimatedType = DataType.Numerical, CellReference = "A1" },
                new() { Name = "Pressure", Value = "1013.25", EstimatedType = DataType.Numerical, CellReference = "A2" },
                new() { Name = "Humidity", Value = "65", EstimatedType = DataType.Numerical, CellReference = "A3" }
            },
            Metadata = new ProcessingMetadata
            {
                ProcessingTime = TimeSpan.FromMilliseconds(300),
                StrategyUsed = ProcessingStrategy.Selective,
                StartTime = DateTime.UtcNow.AddMilliseconds(-300),
                EndTime = DateTime.UtcNow
            }
        };
        
        return Task.FromResult(result);
    }

    public Task<List<ExcelParameter>> ExtractParametersAsync(byte[] excelData)
    {
        _logger.LogDebug("Extracting parameters from Excel");
        
        var parameters = new List<ExcelParameter>
        {
            new() { Name = "Temperature", Value = "25.3", EstimatedType = DataType.Numerical, CellReference = "A1" },
            new() { Name = "Pressure", Value = "1013.25", EstimatedType = DataType.Numerical, CellReference = "A2" },
            new() { Name = "Humidity", Value = "65", EstimatedType = DataType.Numerical, CellReference = "A3" }
        };
        
        return Task.FromResult(parameters);
    }

    public Task<bool> ConsolidateWithPDFGrainAsync(string pdfGrainId)
    {
        _logger.LogInformation("Consolidating with PDF grain {GrainId}", pdfGrainId);
        return Task.FromResult(true);
    }
}
