# Orleans-based Autonomous Validation System Specification

## Overview
This specification outlines the architecture and design of an autonomous, Orleans-based system for validating Excel and PDF files.

## Objectives
- **Scalable and Robust**: Utilize Microsoft Orleans to enable a scalable and robust architecture.
- **Offline Capabilities**: Ensure the solution operates efficiently in offline or edge environments.
- **High Accuracy**: Maintain precision in validation through exact and semantic matches.

## System Architecture
The system is composed of several grains, each responsible for a particular task:

### Grains
1. **OrchestratorGrain**: 
   - Coordinates all other grains, handling task distribution and result aggregation.
   - Monitors the state of other grains and manages load balancing.

2. **PDFProcessingGrain**:
   - Extracts key-value pairs from PDF documents utilizing local models for image and text processing.
   - Integrates .NET libraries for PDF and image manipulation.

3. **ExcelProcessingGrain**:
   - Processes Excel files to extract and prepare data for validation.
   - Uses efficient .NET libraries for Excel integration.

4. **ValidationGrain**:
   - Performs validation of extracted data using both semantic embeddings and exact matching.
   - Integrates .NET-compatible models and libraries for embeddings.

## Technology Stack
- **Programming Language**: C#, .NET 6+
- **Framework**: Microsoft Orleans
- **Libraries**:
  - Image processing and PDF manipulation: `ImageSharp`, `PdfPig`
  - Excel handling: `EPPlus` or `ClosedXML`
  - Semantic embeddings: To be determined based on compatible libraries

## Deployment
- **Standalone**: Deployable without the need for Kubernetes, can run on a local environment with 8GB RAM.
- **Containerization**: Optional Docker configuration for deploying Orleans hosts.
- **Offline Operation**: Pre-load models and data to ensure functionality without internet connectivity.

## Next Steps
1. Research and select .NET-compatible machine learning and processing models.
2. Develop a prototype OrchestratorGrain to handle basic coordination.
3. Implement the core logic for PDF and Excel processing grains.
4. Validate the architecture with unit tests and performance benchmarks.

---
This document sets the foundation for developing the Orleans-based architecture, addressing the requirements previously identified in the Python-based POC. Further clarification and refinement will ensure alignment with system goals. Adjustments may be made based on ongoing requirements and technological evaluations.
