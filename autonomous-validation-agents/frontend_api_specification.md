# Frontend Web Application and API Endpoints Specification

## Overview

This specification defines the complete user-facing interface for the autonomous validation system, including a modern web application frontend and comprehensive REST API endpoints that integrate with the Orleans-based backend agents.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  React/Next.js Web App    │  Mobile App (Future)               │
├─────────────────────────────────────────────────────────────────┤
│                      API Gateway Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ASP.NET Core API        │  Authentication    │  Rate Limiting │
├─────────────────────────────────────────────────────────────────┤
│                    Orleans Backend Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  Orchestrator │ PDF Agent │ Excel Agent │ Validation Agent     │
├─────────────────────────────────────────────────────────────────┤
│              Python ML Services (gRPC)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Frontend Web Application

### Technology Stack
- **Framework**: React 18 with Next.js 14 (App Router)
- **UI Library**: Tailwind CSS + shadcn/ui components
- **State Management**: Zustand for client state, TanStack Query for server state
- **File Upload**: React Dropzone with progress tracking
- **Real-time Updates**: Server-Sent Events (SSE) for processing status
- **Charts & Visualization**: Recharts for validation results
- **TypeScript**: Full type safety throughout the application

### Key Features

#### 1. File Upload Interface
```typescript
interface FileUploadProps {
  onFilesSelected: (files: FileUploadRequest) => void;
  supportedFormats: string[];
  maxFileSize: number;
  processingStatus: ProcessingStatus;
}

interface FileUploadRequest {
  excelFile: File;
  pdfFile: File;
  processingOptions: ProcessingOptions;
}
```

**Features:**
- Drag-and-drop interface for Excel and PDF files
- Real-time file validation (format, size, content preview)
- Support for multiple file formats (.xlsx, .xls, .pdf)
- File preview with basic metadata display
- Processing options selection (memory mode, validation strictness)

#### 2. Processing Dashboard
```typescript
interface ProcessingDashboard {
  sessionId: string;
  currentStep: ProcessingStep;
  progress: ProcessingProgress;
  resourceUsage: ResourceMetrics;
  agentActivity: AgentActivityLog[];
}

enum ProcessingStep {
  FileAnalysis = "file-analysis",
  PDFExtraction = "pdf-extraction", 
  ExcelProcessing = "excel-processing",
  Validation = "validation",
  ReportGeneration = "report-generation",
  Complete = "complete"
}
```

**Features:**
- Real-time processing progress with step-by-step breakdown
- Live resource utilization monitoring (memory, CPU, active agents)
- Agent activity log showing which grains are active
- Estimated time remaining based on historical data
- Cancel/pause processing capabilities

#### 3. Validation Results Interface
```typescript
interface ValidationResultsView {
  validationSummary: ValidationSummary;
  parameterResults: ParameterValidationResult[];
  discrepancies: DiscrepancyReport[];
  recommendedActions: RecommendedAction[];
  exportOptions: ExportFormat[];
}

interface ParameterValidationResult {
  excelParameter: ExcelParameter;
  pdfValue: PDFValue;
  matchType: MatchType;
  confidenceScore: number;
  status: ValidationStatus;
  discrepancyDetails?: DiscrepancyDetail;
}
```

**Features:**
- Interactive validation results table with filtering and sorting
- Side-by-side comparison of Excel vs PDF values
- Confidence scoring with color-coded indicators
- Discrepancy highlighting with detailed explanations
- Batch validation actions (approve, reject, flag for review)
- Export results in multiple formats (Excel, PDF, JSON, CSV)

#### 4. System Monitoring Interface
```typescript
interface SystemMonitoringView {
  resourceStatus: ResourceStatus;
  agentMetrics: AgentMetrics[];
  performanceHistory: PerformanceHistoryPoint[];
  systemHealth: SystemHealthIndicator[];
}
```

**Features:**
- Real-time system resource monitoring
- Orleans grain activity visualization
- Memory usage trends and predictions
- Processing performance analytics
- System health indicators and alerts

#### 5. Configuration Management
```typescript
interface ConfigurationPanel {
  processingModes: ProcessingModeConfig[];
  validationSettings: ValidationSettings;
  systemLimits: SystemLimits;
  modelSettings: ModelConfiguration;
}
```

**Features:**
- Processing mode selection (High/Medium/Low memory)
- Validation strictness configuration
- File processing limits and timeouts
- Model selection and configuration options

### User Experience Flow

#### 1. Initial Upload Flow
```
Upload Files → File Validation → Processing Options → Start Processing
     ↓              ↓                    ↓               ↓
File Preview   Format Check    Memory Mode Selection   Agent Spawning
Size Check     Content Scan    Strictness Level        Resource Allocation
```

#### 2. Processing Flow with Real-time Updates
```
File Analysis → PDF Processing → Excel Processing → Validation → Results
      ↓              ↓              ↓               ↓         ↓
  SSE Updates    Agent Activity   Parameter Extraction   Matching   Report
  Progress Bar   Memory Usage     Quality Checks        Scoring    Export
```

#### 3. Results Review Flow
```
Summary View → Detailed Results → Discrepancy Review → Actions → Export
     ↓              ↓                    ↓            ↓        ↓
Overview Stats   Parameter-by-Parameter   Manual Review    Approve   PDF/Excel
Match Rate      Confidence Scores         Flag Issues      Reject    JSON/CSV
```

## REST API Endpoints

### Base Configuration
- **Base URL**: `https://api.validation.local` (development) / `https://api.yourdomain.com` (production)
- **API Version**: v1
- **Authentication**: JWT tokens with role-based access
- **Rate Limiting**: 100 requests/minute per user, 1000 requests/minute per API key
- **Content-Type**: `application/json` for requests, various for file uploads

### Core API Endpoints

#### 1. File Upload and Processing

```http
POST /api/v1/validation/upload
Content-Type: multipart/form-data
Authorization: Bearer {jwt_token}

# Request
{
  "excelFile": [binary],
  "pdfFile": [binary],
  "processingOptions": {
    "memoryMode": "medium",
    "validationStrictness": "high",
    "enableMultimodal": true,
    "processingTimeout": 300
  }
}

# Response
{
  "sessionId": "uuid-v4",
  "status": "processing",
  "estimatedDuration": 45,
  "resourcesAllocated": {
    "memoryMB": 512,
    "activeAgents": ["orchestrator", "pdf-intelligence", "excel-intelligence"]
  }
}
```

#### 2. Processing Status and Real-time Updates

```http
GET /api/v1/validation/{sessionId}/status
Authorization: Bearer {jwt_token}

# Response
{
  "sessionId": "uuid-v4",
  "status": "processing",
  "currentStep": "pdf-extraction",
  "progress": {
    "percentage": 35,
    "currentOperation": "Extracting key-value pairs from PDF page 3 of 5",
    "stepsCompleted": 2,
    "totalSteps": 5
  },
  "resourceUsage": {
    "memoryUsageMB": 487,
    "memoryLimitMB": 1024,
    "activeAgents": 3,
    "processingTimeElapsed": 23
  },
  "agentActivity": [
    {
      "agentType": "pdf-intelligence",
      "status": "active",
      "currentTask": "multimodal-extraction",
      "memoryUsage": 245
    }
  ]
}
```

#### 3. Server-Sent Events for Real-time Updates

```http
GET /api/v1/validation/{sessionId}/events
Authorization: Bearer {jwt_token}
Accept: text/event-stream

# Event Stream
event: progress
data: {"percentage": 40, "step": "pdf-extraction", "message": "Processing page 4 of 5"}

event: agent-spawned  
data: {"agentType": "validation", "memoryAllocated": 128, "estimatedDuration": 15}

event: validation-complete
data: {"status": "completed", "totalMatches": 45, "discrepancies": 3, "processingTime": 67}
```

#### 4. Validation Results

```http
GET /api/v1/validation/{sessionId}/results
Authorization: Bearer {jwt_token}

# Response
{
  "sessionId": "uuid-v4",
  "validationSummary": {
    "totalParameters": 48,
    "exactMatches": 42,
    "semanticMatches": 3,
    "discrepancies": 3,
    "overallScore": 0.94,
    "processingTime": 67,
    "confidenceLevel": "high"
  },
  "results": [
    {
      "parameterId": "param-001",
      "excelParameter": {
        "name": "Supplier Name",
        "value": "ABC Industrial Corp",
        "location": "Sheet1!B5",
        "dataType": "text"
      },
      "pdfValue": {
        "value": "ABC Industrial Corporation", 
        "confidence": 0.95,
        "source": "page-1-region-3",
        "extractionMethod": "multimodal"
      },
      "matchResult": {
        "matchType": "semantic",
        "score": 0.89,
        "status": "match",
        "explanation": "Semantically equivalent company names with common abbreviation"
      }
    }
  ],
  "discrepancies": [
    {
      "parameterId": "param-023",
      "type": "value-mismatch",
      "severity": "high",
      "description": "Quantity values differ significantly",
      "excelValue": "1000",
      "pdfValue": "100", 
      "recommendedAction": "manual-review"
    }
  ]
}
```

#### 5. Export and Reporting

```http
GET /api/v1/validation/{sessionId}/export
Authorization: Bearer {jwt_token}
Accept: application/json

Query Parameters:
- format: pdf|excel|csv|json
- includeRawData: true|false
- includeDiscrepancies: true|false
- template: summary|detailed|audit

# Response (for JSON format)
{
  "exportId": "export-uuid",
  "downloadUrl": "/api/v1/downloads/{exportId}",
  "expiresAt": "2024-01-15T10:30:00Z",
  "format": "json",
  "size": 1024576
}
```

#### 6. System Monitoring and Health

```http
GET /api/v1/system/health
Authorization: Bearer {jwt_token}

# Response
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600,
  "services": {
    "orleans": {
      "status": "healthy",
      "activeSilos": 2,
      "activeGrains": 15
    },
    "pythonML": {
      "status": "healthy",
      "instances": 1,
      "averageResponseTime": 245
    },
    "database": {
      "status": "healthy",
      "connectionPool": "optimal"
    }
  },
  "resourceUsage": {
    "memoryUsagePercent": 65,
    "cpuUsagePercent": 23,
    "diskUsagePercent": 45
  }
}
```

#### 7. User Management and Authentication

```http
POST /api/v1/auth/login
Content-Type: application/json

# Request
{
  "email": "user@company.com",
  "password": "secure_password"
}

# Response
{
  "accessToken": "jwt-access-token",
  "refreshToken": "jwt-refresh-token",
  "user": {
    "id": "user-uuid",
    "email": "user@company.com",
    "role": "validator",
    "permissions": ["upload", "validate", "export"]
  },
  "expiresIn": 3600
}
```

#### 8. Historical Data and Analytics

```http
GET /api/v1/analytics/processing-history
Authorization: Bearer {jwt_token}

Query Parameters:
- timeRange: 1d|7d|30d|90d
- groupBy: hour|day|week
- includeResourceMetrics: true|false

# Response
{
  "timeRange": "7d",
  "totalSessions": 156,
  "averageProcessingTime": 43.2,
  "averageAccuracy": 0.91,
  "resourceUtilization": {
    "averageMemoryMB": 678,
    "peakMemoryMB": 1203,
    "averageCPUPercent": 34
  },
  "processingTrends": [
    {
      "timestamp": "2024-01-14T00:00:00Z",
      "sessionsCount": 23,
      "averageTime": 41.5,
      "accuracyRate": 0.93
    }
  ]
}
```

### Error Handling and Status Codes

#### Standard HTTP Status Codes
- `200 OK` - Successful request
- `201 Created` - Resource created successfully  
- `202 Accepted` - Request accepted for processing
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (duplicate upload)
- `413 Payload Too Large` - File size exceeds limits
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - System overloaded

#### Custom Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "File validation failed",
    "details": {
      "field": "excelFile",
      "reason": "Unsupported file format",
      "supportedFormats": [".xlsx", ".xls"]
    },
    "timestamp": "2024-01-14T10:30:00Z",
    "requestId": "req-uuid"
  }
}
```

## Frontend Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router
│   │   ├── (dashboard)/
│   │   │   ├── upload/
│   │   │   │   └── page.tsx          # File upload interface
│   │   │   ├── processing/
│   │   │   │   └── [sessionId]/
│   │   │   │       └── page.tsx      # Processing dashboard
│   │   │   ├── results/
│   │   │   │   └── [sessionId]/
│   │   │   │       └── page.tsx      # Validation results
│   │   │   └── monitoring/
│   │   │       └── page.tsx          # System monitoring
│   │   ├── api/                      # API routes (if needed)
│   │   ├── globals.css
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   ├── upload/
│   │   │   ├── FileUploader.tsx
│   │   │   ├── FilePreview.tsx
│   │   │   └── ProcessingOptions.tsx
│   │   ├── processing/
│   │   │   ├── ProgressTracker.tsx
│   │   │   ├── AgentMonitor.tsx
│   │   │   └── ResourceUsage.tsx
│   │   ├── results/
│   │   │   ├── ValidationTable.tsx
│   │   │   ├── DiscrepancyView.tsx
│   │   │   └── ExportOptions.tsx
│   │   └── monitoring/
│   │       ├── SystemHealth.tsx
│   │       └── PerformanceCharts.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts             # API client configuration
│   │   │   ├── validation.ts         # Validation API calls
│   │   │   └── monitoring.ts         # Monitoring API calls
│   │   ├── types/
│   │   │   ├── api.ts                # API type definitions
│   │   │   ├── validation.ts         # Validation types
│   │   │   └── monitoring.ts         # Monitoring types
│   │   ├── stores/
│   │   │   ├── upload.ts             # Upload state management
│   │   │   ├── validation.ts         # Validation state
│   │   │   └── system.ts             # System monitoring state
│   │   └── utils/
│   │       ├── formatting.ts
│   │       ├── validation.ts
│   │       └── constants.ts
│   ├── hooks/
│   │   ├── useFileUpload.ts
│   │   ├── useValidationResults.ts
│   │   ├── useServerSentEvents.ts
│   │   └── useSystemMonitoring.ts
│   └── styles/
├── public/
│   ├── icons/
│   └── images/
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## Development and Deployment

### Development Environment
```bash
# Frontend development server
cd frontend
npm run dev # Runs on http://localhost:3000

# API development (ASP.NET Core)
cd src/AutonomousValidation.API
dotnet run # Runs on https://localhost:5001

# Orleans backend
cd src/AutonomousValidation.Orleans  
dotnet run # Runs Orleans silo

# Python ML service
cd python-ml-service
python -m grpc_server # Runs on localhost:50051
```

### Production Deployment with Docker
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NEXT_PUBLIC_API_URL=http://api:80
    ports:
      - "3000:3000"
    depends_on:
      - api
      
  api:
    build:
      context: ./src/AutonomousValidation.API
      dockerfile: Dockerfile
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - Orleans__ClusteringProvider=Consul
    ports:
      - "80:80"
    depends_on:
      - orleans-silo
      
  orleans-silo:
    build:
      context: ./src/AutonomousValidation.Orleans
      dockerfile: Dockerfile
    environment:
      - MEMORY_THRESHOLD=High
      - CONSUL_ENDPOINT=http://consul:8500
    depends_on:
      - consul
      - python-ml
      
  python-ml:
    build:
      context: ./python-ml-service
      dockerfile: Dockerfile
    ports:
      - "50051:50051"
      
  consul:
    image: consul:latest
    ports:
      - "8500:8500"
      
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - frontend
      - api
```

## Security Considerations

### Authentication and Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (Admin, Validator, Viewer)
- API key authentication for programmatic access
- Session management with secure cookie settings

### Data Security
- File encryption in transit and at rest
- Secure file upload with virus scanning
- Data retention policies and automatic cleanup
- GDPR compliance for data processing

### API Security
- Rate limiting to prevent abuse
- Request validation and sanitization
- CORS configuration for cross-origin requests
- SSL/TLS encryption for all communications

## Performance Optimization

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization and caching
- Bundle size optimization
- Service worker for offline capabilities

### API Optimization  
- Response caching with Redis
- Database query optimization
- Connection pooling
- Compression for large responses

### Real-time Features
- WebSocket fallback for SSE
- Connection management and reconnection
- Efficient event streaming
- Client-side caching of real-time data

This comprehensive specification provides a complete blueprint for implementing the frontend web application and API endpoints that will serve as the user interface for the autonomous validation system. The design emphasizes real-time feedback, intuitive user experience, and seamless integration with the Orleans-based backend agents.
