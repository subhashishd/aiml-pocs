# Development Environment Setup for Orleans Autonomous Validation System

## macOS Development Environment Setup

### 1. Core Requirements

```bash
# Install .NET SDK (Latest LTS - .NET 8)
brew install dotnet

# Verify installation
dotnet --version  # Should show 8.x.x

# Install Docker for containerization
brew install --cask docker

# Install Git (if not already installed)
brew install git
```

### 2. IDE Options

#### Option A: Visual Studio Code (Recommended for beginners)
```bash
# Install VS Code
brew install --cask visual-studio-code

# Install essential extensions via command line
code --install-extension ms-dotnettools.csharp
code --install-extension ms-dotnettools.csdevkit
code --install-extension ms-vscode.vscode-json
code --install-extension ms-azuretools.vscode-docker
code --install-extension eamodio.gitlens
```

#### Option B: Windsurf (Recommended for AI-assisted development)
```bash
# Download from https://windsurf.codeium.com/
# Windsurf is VS Code-based with AI capabilities
# All the same extensions work, plus built-in AI assistance
```

#### Option C: JetBrains Rider (Professional choice)
```bash
# Download from https://www.jetbrains.com/rider/
# 30-day free trial, then subscription required
# Best for complex Orleans debugging and profiling
```

### 3. Additional Tools

```bash
# Install Ollama for local LLM support
brew install ollama

# Pull a lightweight model for development
ollama pull phi3:mini

# Install protobuf compiler for gRPC
brew install protobuf

# Install Python for ML service
brew install python@3.11
pip3 install grpcio grpcio-tools

# Install useful utilities
brew install htop        # System monitoring
brew install jq          # JSON processing
brew install tree        # Directory visualization
```

## Project Structure Setup

### 1. Create Solution Structure
```bash
# Navigate to your project directory
cd /Users/subhashishdas/aiml-pocs/autonomous-validation-agents

# Create .NET solution
dotnet new sln -n AutonomousValidation

# Create project structure
mkdir -p src/AutonomousValidation.Orleans
mkdir -p src/AutonomousValidation.Core
mkdir -p src/AutonomousValidation.API
mkdir -p src/AutonomousValidation.Tests
mkdir -p python-ml-service
mkdir -p deployment/docker
mkdir -p models/{minimal,full}

# Create Orleans host project
cd src/AutonomousValidation.Orleans
dotnet new console
dotnet add package Microsoft.Orleans.Server --version 8.0.0
dotnet add package Microsoft.Orleans.Clustering.Consul --version 8.0.0
dotnet add package Microsoft.SemanticKernel --version 1.0.1
dotnet add package Microsoft.ML.OnnxRuntime --version 1.16.3
dotnet add package Grpc.Net.Client --version 2.59.0

# Create Core library
cd ../AutonomousValidation.Core
dotnet new classlib
dotnet add package Microsoft.Orleans.Abstractions --version 8.0.0
dotnet add package Microsoft.Orleans.CodeGenerator.MSBuild --version 8.0.0

# Create API project
cd ../AutonomousValidation.API
dotnet new webapi
dotnet add package Microsoft.Orleans.Client --version 8.0.0
dotnet add package Swashbuckle.AspNetCore --version 6.5.0

# Create Test project
cd ../AutonomousValidation.Tests
dotnet new xunit
dotnet add package Microsoft.Orleans.TestingHost --version 8.0.0
dotnet add package Moq --version 4.20.69
dotnet add package FluentAssertions --version 6.12.0

# Add projects to solution
cd ../../..
dotnet sln add src/AutonomousValidation.Orleans/AutonomousValidation.Orleans.csproj
dotnet sln add src/AutonomousValidation.Core/AutonomousValidation.Core.csproj
dotnet sln add src/AutonomousValidation.API/AutonomousValidation.API.csproj
dotnet sln add src/AutonomousValidation.Tests/AutonomousValidation.Tests.csproj
```

### 2. IDE-Specific Configuration

#### For VS Code (.vscode/settings.json)
```json
{
    "dotnet.defaultSolution": "AutonomousValidation.sln",
    "omnisharp.enableEditorConfigSupport": true,
    "omnisharp.enableImportCompletion": true,
    "omnisharp.enableRoslynAnalyzers": true,
    "files.exclude": {
        "**/bin": true,
        "**/obj": true
    },
    "csharp.semanticHighlighting.enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll": true
    }
}
```

#### For VS Code (.vscode/launch.json)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Orleans Host",
            "type": "coreclr",
            "request": "launch",
            "preLaunchTask": "build",
            "program": "${workspaceFolder}/src/AutonomousValidation.Orleans/bin/Debug/net8.0/AutonomousValidation.Orleans.dll",
            "args": [],
            "cwd": "${workspaceFolder}/src/AutonomousValidation.Orleans",
            "console": "internalConsole",
            "stopAtEntry": false
        },
        {
            "name": "API",
            "type": "coreclr",
            "request": "launch",
            "preLaunchTask": "build",
            "program": "${workspaceFolder}/src/AutonomousValidation.API/bin/Debug/net8.0/AutonomousValidation.API.dll",
            "args": [],
            "cwd": "${workspaceFolder}/src/AutonomousValidation.API",
            "console": "internalConsole",
            "stopAtEntry": false,
            "env": {
                "ASPNETCORE_ENVIRONMENT": "Development"
            }
        }
    ]
}
```

#### For VS Code (.vscode/tasks.json)
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "build",
            "command": "dotnet",
            "type": "process",
            "args": [
                "build",
                "${workspaceFolder}/AutonomousValidation.sln",
                "/property:GenerateFullPaths=true",
                "/consoleloggerparameters:NoSummary"
            ],
            "problemMatcher": "$msCompile"
        },
        {
            "label": "test",
            "command": "dotnet",
            "type": "process",
            "args": [
                "test",
                "${workspaceFolder}/AutonomousValidation.sln",
                "--logger",
                "trx",
                "--results-directory",
                "${workspaceFolder}/TestResults"
            ],
            "problemMatcher": "$msCompile"
        }
    ]
}
```

### 3. Development Workflow

#### Daily Development Commands
```bash
# Build solution
dotnet build

# Run tests
dotnet test

# Run Orleans host
cd src/AutonomousValidation.Orleans
dotnet run

# Run API (in another terminal)
cd src/AutonomousValidation.API
dotnet run

# Format code
dotnet format

# Create new grain
dotnet new interface -n IMyGrain -o Interfaces
dotnet new class -n MyGrain -o Grains
```

#### Docker Development
```bash
# Build development image
docker build -f deployment/docker/Dockerfile.dev -t autonomous-validation:dev .

# Run with docker-compose
docker-compose -f deployment/docker/docker-compose.dev.yml up

# View logs
docker-compose -f deployment/docker/docker-compose.dev.yml logs -f orleans-host
```

## Windsurf-Specific Features

### AI-Assisted Development with Windsurf

1. **Grain Generation**: Ask Windsurf AI to generate Orleans grains based on specifications
2. **Code Completion**: Smart completion for Orleans patterns and Semantic Kernel integration
3. **Bug Detection**: AI can spot common Orleans pitfalls (grain lifecycle, serialization issues)
4. **Architecture Questions**: Ask about Orleans best practices directly in the IDE

#### Example Windsurf AI Prompts:
```
"Generate an Orleans grain that processes PDF files with memory monitoring"
"Create a Semantic Kernel plugin for Excel analysis"
"Implement a resource manager grain with memory thresholds"
"Add gRPC client for Python ML service integration"
```

## Troubleshooting Common Issues

### .NET SDK Issues
```bash
# If dotnet command not found
echo 'export PATH="$PATH:/usr/local/share/dotnet"' >> ~/.zshrc
source ~/.zshrc

# Clear NuGet cache if package restore fails
dotnet nuget locals all --clear
```

### Orleans Development Issues
- **Grain Serialization**: Ensure all grain method parameters/returns are serializable
- **Grain Identity**: Use proper grain key types (string, GUID, etc.)
- **Clustering**: For development, use localhost clustering initially

### VS Code Issues
```bash
# Restart OmniSharp server
Cmd+Shift+P -> "OmniSharp: Restart OmniSharp"

# Clear VS Code workspace cache
rm -rf .vscode/
```

## Performance Monitoring

### macOS-specific Tools
```bash
# Monitor memory usage
top -pid $(pgrep -f "AutonomousValidation.Orleans")

# Monitor Docker containers
docker stats

# Profile .NET applications
dotnet-trace collect -p $(pgrep -f "AutonomousValidation.Orleans")
```

This development environment will provide you with everything needed to build, debug, and deploy the Orleans-based autonomous validation system on your MacBook.
