# Testing Strategy & Quality Assurance

## Overview

This document outlines the comprehensive testing and quality assurance strategy for the Autonomous Validation Agents project. We follow industry best practices with a zero-warnings policy and extensive automated testing.

## Quality Standards

### Code Quality Requirements

- **Zero Warnings Policy**: All builds must complete without warnings
- **80% Code Coverage**: Minimum threshold for unit and integration tests
- **Static Analysis**: SonarQube quality gates must pass
- **Security Scanning**: OWASP dependency check and container security scans
- **Performance Testing**: Load testing for Orleans grains under various conditions

### Code Analysis Tools

1. **Microsoft .NET Analyzers**: Comprehensive C# code analysis
2. **SonarQube**: Code quality, security vulnerabilities, code smells
3. **OWASP Dependency Check**: Known security vulnerabilities in dependencies
4. **Trivy**: Container image security scanning
5. **WhiteSource/Mend**: License compliance and security scanning

## Testing Pyramid

### Unit Tests (Foundation)
- **Location**: `tests/AutonomousValidation.Tests.Unit/`
- **Framework**: xUnit with FluentAssertions
- **Mocking**: Moq for dependencies
- **Coverage Target**: 90%+
- **Execution Time**: < 30 seconds total

#### Test Categories:
- Model validation and serialization
- Business logic in isolation
- Algorithm correctness
- Error handling paths
- Edge cases and boundary conditions

#### Example Structure:
```csharp
[Fact]
public void ValidationGrain_ValidateAsync_WithValidInput_ReturnsSuccessResult()
{
    // Arrange
    var grain = new ValidationGrain(_mockLogger.Object);
    var excelParameters = _fixture.CreateMany<ExcelParameter>(3).ToList();
    var pdfKeyValues = _fixture.CreateMany<KeyValuePair<string, object>>(3).ToList();

    // Act
    var result = await grain.ValidateAsync(excelParameters, pdfKeyValues);

    // Assert
    result.Should().NotBeNull();
    result.Results.Should().HaveCount(3);
    result.OverallScore.Should().BeGreaterThan(0);
}
```

### Integration Tests (Middle Layer)
- **Location**: `tests/AutonomousValidation.Tests.Integration/`
- **Framework**: xUnit with Orleans TestingHost
- **Coverage Target**: 70%+
- **Execution Time**: < 5 minutes total

#### Test Categories:
- Orleans grain interactions
- End-to-end workflows
- Resource management scenarios
- Container orchestration
- Database interactions (when applicable)

#### Example Structure:
```csharp
[Fact]
public async Task OrchestratorGrain_ProcessValidationRequest_IntegrationTest()
{
    // Arrange
    var request = new ValidationRequest
    {
        ExcelData = TestData.SampleExcelFile,
        PdfData = TestData.SamplePdfFile
    };

    // Act
    var orchestrator = _cluster.GrainFactory.GetGrain<IOrchestratorGrain>("test-session");
    var result = await orchestrator.ProcessValidationRequestAsync(request);

    // Assert
    result.Should().NotBeNull();
    result.Errors.Should().BeEmpty();
    result.Results.Should().NotBeEmpty();
}
```

### Performance Tests (Monitoring)
- **Framework**: NBomber for load testing
- **Scenarios**: 
  - Concurrent grain processing
  - Memory pressure scenarios
  - Network latency simulation
  - Resource exhaustion handling

## Test Configuration

### Unit Test Project Configuration

Key features enabled in `AutonomousValidation.Tests.Unit.csproj`:

- **Code Coverage**: Coverlet with multiple output formats
- **Test Framework**: xUnit with Visual Studio integration
- **Assertion Library**: FluentAssertions for readable tests
- **Mocking**: Moq for dependency isolation
- **Test Data**: AutoFixture and Bogus for realistic test data
- **Snapshot Testing**: Verify.Xunit for regression testing

### Integration Test Project Configuration

Key features in `AutonomousValidation.Tests.Integration.csproj`:

- **Orleans Testing**: TestingHost for Orleans cluster simulation
- **Containerization**: Testcontainers for infrastructure dependencies
- **Performance Testing**: NBomber for load testing
- **Extended Timeout**: 5-minute timeout for complex scenarios

## Running Tests

### Local Development

```bash
# Run all tests with coverage
dotnet test --collect:"XPlat Code Coverage" --settings coverlet.runsettings

# Run only unit tests
dotnet test tests/AutonomousValidation.Tests.Unit/

# Run only integration tests
dotnet test tests/AutonomousValidation.Tests.Integration/

# Run with specific verbosity
dotnet test --logger "console;verbosity=detailed"
```

### Coverage Reports

```bash
# Generate HTML coverage report
dotnet tool install -g dotnet-reportgenerator-globaltool
reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage-report -reporttypes:Html

# View coverage in browser
open coverage-report/index.html
```

### Performance Testing

```bash
# Run performance tests
dotnet run --project tests/AutonomousValidation.Tests.Performance/

# Run with specific scenario
dotnet run --project tests/AutonomousValidation.Tests.Performance/ -- --scenario ConcurrentValidation
```

## CI/CD Integration

### Azure DevOps Pipeline

The pipeline includes comprehensive quality gates:

1. **Build Validation**: Zero warnings policy enforced
2. **Unit Tests**: 80% coverage threshold
3. **Integration Tests**: End-to-end scenario validation
4. **Static Analysis**: SonarQube quality gate
5. **Security Scanning**: OWASP and container security
6. **Performance Testing**: Baseline performance verification

### Quality Gates

Tests must pass the following gates to proceed:

- **Code Coverage**: ≥80% line coverage, ≥70% branch coverage
- **SonarQube**: Quality gate passed (A rating)
- **Security**: No high/critical vulnerabilities
- **Performance**: Response time within acceptable limits
- **Memory**: No memory leaks detected

## Test Data Management

### Test Data Strategy

1. **Unit Tests**: Use AutoFixture for randomized data
2. **Integration Tests**: Use Bogus for realistic fake data
3. **Performance Tests**: Use representative data sets
4. **Security Tests**: Include edge cases and malicious inputs

### Sample Data

```csharp
// AutoFixture configuration
var fixture = new Fixture();
fixture.Customize<ValidationRequest>(c => c
    .With(x => x.ExcelData, TestData.SampleExcelBytes)
    .With(x => x.PdfData, TestData.SamplePdfBytes));

// Bogus configuration
var faker = new Faker<ExcelParameter>()
    .RuleFor(x => x.Name, f => f.Lorem.Word())
    .RuleFor(x => x.Value, f => f.Random.Double(0, 1000))
    .RuleFor(x => x.EstimatedType, f => f.PickRandom<DataType>());
```

## Best Practices

### Test Naming Convention

```csharp
[MethodUnderTest]_[Scenario]_[ExpectedResult]

// Examples:
ValidateAsync_WithValidParameters_ReturnsSuccessResult
ProcessValidationRequestAsync_UnderMemoryPressure_HandlesGracefulDegradation
GetResourceStatusAsync_WhenCriticalMemory_ReturnsCorrectThreshold
```

### Test Organization

- Group related tests in nested classes
- Use descriptive test class names
- Implement IClassFixture for shared setup
- Use IAsyncLifetime for async setup/cleanup

### Assertion Guidelines

```csharp
// Good: Descriptive and specific
result.Should().NotBeNull("validation result should always be returned");
result.Results.Should().HaveCount(expectedCount, "each parameter should have a result");
result.OverallScore.Should().BeInRange(0.0, 1.0, "score should be normalized");

// Bad: Generic assertions without context
result.Should().NotBeNull();
Assert.True(result.Results.Count > 0);
```

## Troubleshooting

### Common Issues

1. **Orleans Cluster Startup**: Allow sufficient time for cluster formation
2. **Memory Tests**: Run in isolated process to avoid interference
3. **Timing Issues**: Use appropriate timeouts and retry policies
4. **Container Dependencies**: Ensure Docker is running for integration tests

### Debug Configuration

```xml
<!-- Add to test projects for debugging -->
<PropertyGroup Condition="'$(Configuration)' == 'Debug'">
  <DefineConstants>DEBUG;TRACE</DefineConstants>
  <DebugType>full</DebugType>
</PropertyGroup>
```

## Metrics and Reporting

### Key Metrics Tracked

- **Code Coverage**: Line, branch, and method coverage
- **Test Execution Time**: Performance regression detection
- **Flaky Test Rate**: Test reliability monitoring
- **Defect Escape Rate**: Quality of testing effectiveness

### Reporting Dashboard

All metrics are integrated into:
- Azure DevOps dashboards
- SonarQube project overview
- Custom quality reports generated per build

## Continuous Improvement

### Review Process

- Weekly test review meetings
- Monthly quality metrics analysis
- Quarterly testing strategy review
- Annual tool and framework evaluation

### Quality Evolution

- Gradual increase in coverage requirements
- Introduction of mutation testing
- Enhanced performance benchmarking
- Advanced security testing scenarios
