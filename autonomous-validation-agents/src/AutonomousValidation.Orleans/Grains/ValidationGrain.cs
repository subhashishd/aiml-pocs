using Orleans;
using Microsoft.Extensions.Logging;
using AutonomousValidation.Core.Interfaces;
using AutonomousValidation.Core.Models;
using AutonomousValidation.Core.Enums;

namespace AutonomousValidation.Orleans.Grains;

/// <summary>
/// Basic stub implementation of Validation Grain
/// </summary>
public class ValidationGrain : Grain, IValidationGrain
{
    private readonly ILogger<ValidationGrain> _logger;

    public ValidationGrain(ILogger<ValidationGrain> logger)
    {
        _logger = logger;
    }

    public Task<ValidationResult> ValidateAsync(
        List<ExcelParameter> excelParams, 
        List<KeyValuePair<string, object>> pdfKeyValues)
    {
        _logger.LogInformation("Validating {ExcelCount} Excel parameters against {PDFCount} PDF values",
            excelParams.Count, pdfKeyValues.Count);
        
        var results = new List<ParameterValidationResult>();
        
        foreach (var excelParam in excelParams)
        {
            var matchingPdfValue = pdfKeyValues.FirstOrDefault(kvp => 
                kvp.Key.Contains(excelParam.Name, StringComparison.OrdinalIgnoreCase));
            
            var isMatch = !matchingPdfValue.Equals(default(KeyValuePair<string, object>));
            
            results.Add(new ParameterValidationResult
            {
                ExcelParameter = excelParam,
                PDFValue = matchingPdfValue,
                MatchResult = new MatchingResult
                {
                    IsMatch = isMatch,
                    ConfidenceScore = isMatch ? 0.9 : 0.1,
                    StrategyUsed = MatchingStrategy.SemanticMatch,
                    Reasoning = isMatch ? "Parameter name found in PDF" : "No matching parameter found"
                },
                DataType = excelParam.EstimatedType
            });
        }
        
        var validationResult = new ValidationResult
        {
            RequestId = this.GetPrimaryKeyString(),
            Results = results,
            OverallScore = results.Count > 0 ? results.Average(r => r.MatchResult.ConfidenceScore) : 0,
            Summary = new ValidationSummary
            {
                TotalParameters = results.Count,
                MatchedParameters = results.Count(r => r.MatchResult.IsMatch),
                UnmatchedParameters = results.Count(r => !r.MatchResult.IsMatch),
                HighConfidenceMatches = results.Count(r => r.MatchResult.ConfidenceScore > 0.8),
                LowConfidenceMatches = results.Count(r => r.MatchResult.ConfidenceScore <= 0.8),
                AverageConfidenceScore = results.Count > 0 ? results.Average(r => r.MatchResult.ConfidenceScore) : 0
            },
            ProcessingMetadata = new ProcessingMetadata
            {
                ProcessingTime = TimeSpan.FromMilliseconds(200),
                StrategyUsed = ProcessingStrategy.Selective,
                StartTime = DateTime.UtcNow.AddMilliseconds(-200),
                EndTime = DateTime.UtcNow
            }
        };
        
        return Task.FromResult(validationResult);
    }

    public Task<MatchingResult> PerformSemanticMatchingAsync(string text1, string text2)
    {
        _logger.LogDebug("Performing semantic matching between '{Text1}' and '{Text2}'", text1, text2);
        
        // Simple semantic matching - can be enhanced with actual embedding models
        var similarity = CalculateSimpleSimilarity(text1, text2);
        
        var result = new MatchingResult
        {
            IsMatch = similarity > 0.7,
            ConfidenceScore = similarity,
            StrategyUsed = MatchingStrategy.SemanticMatch,
            Reasoning = $"Calculated similarity: {similarity:F2}"
        };
        
        return Task.FromResult(result);
    }

    public Task<MatchingResult> PerformExactMatchingAsync(object value1, object value2, DataType dataType)
    {
        _logger.LogDebug("Performing exact matching for {DataType}: '{Value1}' vs '{Value2}'", 
            dataType, value1, value2);
        
        bool isMatch = false;
        double confidence = 0.0;
        
        switch (dataType)
        {
            case DataType.Numerical:
                if (double.TryParse(value1?.ToString(), out var num1) && 
                    double.TryParse(value2?.ToString(), out var num2))
                {
                    isMatch = Math.Abs(num1 - num2) < 0.001; // Exact precision for scientific data
                    confidence = isMatch ? 1.0 : 0.0;
                }
                break;
            
            case DataType.Text:
                isMatch = string.Equals(value1?.ToString(), value2?.ToString(), StringComparison.OrdinalIgnoreCase);
                confidence = isMatch ? 1.0 : 0.0;
                break;
            
            default:
                isMatch = Equals(value1, value2);
                confidence = isMatch ? 1.0 : 0.0;
                break;
        }
        
        var result = new MatchingResult
        {
            IsMatch = isMatch,
            ConfidenceScore = confidence,
            StrategyUsed = MatchingStrategy.ExactMatch,
            Reasoning = $"Exact comparison for {dataType}: {isMatch}"
        };
        
        return Task.FromResult(result);
    }
    
    private static double CalculateSimpleSimilarity(string text1, string text2)
    {
        if (string.IsNullOrEmpty(text1) || string.IsNullOrEmpty(text2))
            return 0.0;
            
        // Simple Levenshtein-based similarity
        var maxLength = Math.Max(text1.Length, text2.Length);
        if (maxLength == 0) return 1.0;
        
        var distance = LevenshteinDistance(text1.ToLowerInvariant(), text2.ToLowerInvariant());
        return 1.0 - (double)distance / maxLength;
    }
    
    private static int LevenshteinDistance(string s1, string s2)
    {
        var matrix = new int[s1.Length + 1, s2.Length + 1];
        
        for (int i = 0; i <= s1.Length; i++)
            matrix[i, 0] = i;
        for (int j = 0; j <= s2.Length; j++)
            matrix[0, j] = j;
        
        for (int i = 1; i <= s1.Length; i++)
        {
            for (int j = 1; j <= s2.Length; j++)
            {
                int cost = s1[i - 1] == s2[j - 1] ? 0 : 1;
                matrix[i, j] = Math.Min(
                    Math.Min(matrix[i - 1, j] + 1, matrix[i, j - 1] + 1),
                    matrix[i - 1, j - 1] + cost);
            }
        }
        
        return matrix[s1.Length, s2.Length];
    }
}
