# Autonomous Agent System for Excel-PDF Validation

## 🎯 Overview

This is a comprehensive autonomous agent system built on top of the Excel-PDF Values Validator. The system provides intelligent, memory-aware document processing using Celery-based autonomous agents that adapt to system resources and automatically optimize processing strategies.

## 🏗️ Architecture

### Core Components

1. **Memory Manager** (`memory_manager.py`)
   - Real-time memory monitoring
   - Agent spawning decisions
   - Resource optimization strategies
   - Memory threshold management

2. **Adaptive Agent Orchestrator** (`orchestrator.py`)
   - Task distribution and management
   - Execution strategy selection (distributed vs consolidated)
   - Agent lifecycle management
   - System status monitoring

3. **Intelligent Agents** (`intelligent_agents.py`)
   - PDF Intelligence Agent (multimodal processing)
   - Excel Intelligence Agent (data extraction)
   - Validation Intelligence Agent (semantic matching)
   - Consolidated Processing Agent (resource-constrained mode)

4. **Memory Monitor Service** (`memory_monitor.py`)
   - Continuous system monitoring
   - Telemetry collection
   - Automatic action triggering
   - Health status reporting

5. **Base Agent Framework** (`base_agent.py`)
   - Common agent functionality
   - Telemetry collection
   - Capability absorption
   - Memory-aware execution

## 🚀 Features

### Autonomous Intelligence
- **Memory-Aware Processing**: Automatically selects optimal processing strategy based on available memory
- **Dynamic Agent Spawning**: Spawns specialized agents when resources allow, consolidates when constrained
- **Adaptive Capability Absorption**: Agents can absorb capabilities from other agents during memory pressure
- **Self-Monitoring**: Continuous health monitoring with automatic corrective actions

### Processing Modes
1. **Distributed Mode** (High Memory): Separate agents for PDF, Excel, and validation
2. **Consolidated Mode** (Low Memory): Single agent handles all processing
3. **Minimal Mode** (Critical Memory): Basic processing only

### Memory Management
- **Real-time Monitoring**: Continuous memory usage tracking
- **Threshold-based Actions**: Automatic consolidation based on memory thresholds
- **Garbage Collection**: Automatic memory cleanup when needed
- **Resource Optimization**: Dynamic model loading/unloading

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Redis (for Celery)
- 8GB+ RAM recommended

### Setup

1. **Clone and navigate to directory**
   ```bash
   cd fastapi/
   ```

2. **Install dependencies** (for local testing)
   ```bash
   pip install -r requirements.txt
   ```

3. **Run comprehensive tests**
   ```bash
   python run_tests.py
   ```

4. **Docker deployment**
   ```bash
   ./test_docker.sh
   ```

## 🔧 Configuration

### Environment Variables

```env
# Memory Management
MAX_MEMORY_GB=8.0
MEMORY_SAFETY_MARGIN=0.15
MEMORY_CHECK_INTERVAL=30
MEMORY_WARNING_THRESHOLD=80
MEMORY_CRITICAL_THRESHOLD=90

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Processing Configuration
USE_MULTIMODAL_PDF=true
USE_OPTIMIZED_MULTIMODAL=true
```

### Memory Thresholds

- **HIGH** (>6GB): Full agent ecosystem with specialized agents
- **MEDIUM** (3-6GB): Core agents with selective sub-agents
- **LOW** (1-3GB): Consolidated processing mode
- **CRITICAL** (<1GB): Minimal orchestrator-only mode

## 🏃 Usage

### Docker Deployment (Recommended)

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Monitor services**
   ```bash
   docker-compose logs -f
   ```

3. **Access services**
   - FastAPI: http://localhost:8000
   - Flower (monitoring): http://localhost:5555 (with --profile monitoring)

### Local Development

1. **Start Redis**
   ```bash
   redis-server
   ```

2. **Start Celery Worker**
   ```bash
   celery -A autonomous_agents.worker worker --loglevel=info
   ```

3. **Start Celery Beat**
   ```bash
   celery -A autonomous_agents.worker beat --loglevel=info
   ```

4. **Start FastAPI**
   ```bash
   uvicorn main_autonomous:app --reload
   ```

## 📋 API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - System health check
- `GET /system-status` - Detailed system status
- `GET /memory-stats` - Memory usage statistics

### Processing Endpoints

- `POST /validate-autonomous` - Autonomous validation (new)
- `POST /validate` - Legacy validation (redirects to autonomous)
- `POST /create-embeddings-autonomous` - Memory-aware embedding creation

### Monitoring Endpoints

- `GET /agent-telemetry` - Agent performance data
- `POST /force-consolidation` - Force consolidation analysis

## 🧪 Testing

### Comprehensive Test Suite

```bash
# Run all tests
python run_tests.py

# Run specific test categories
pytest tests/test_autonomous_agents.py -v

# Test with Docker
./test_docker.sh
```

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Cross-component functionality
3. **Memory Management Tests**: Resource handling validation
4. **Agent Orchestration Tests**: Task distribution verification
5. **System Integration Tests**: End-to-end validation
6. **Docker Configuration Tests**: Container setup validation

## 📊 Monitoring & Analytics

### 🎯 Complete Monitoring Stack

The system includes a comprehensive monitoring and telemetry analysis platform:

**Core Components:**
- **Prometheus**: Metrics collection and time-series database
- **Grafana**: Interactive dashboards and visualizations
- **Telemetry Analyzer**: Intelligent alerting and trend analysis
- **Flower**: Celery task monitoring
- **cAdvisor**: Container metrics
- **Node Exporter**: System metrics

### 🚀 Quick Start Monitoring

```bash
# Start complete monitoring stack
./start_monitoring.sh

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin123)
# Prometheus: http://localhost:9090
# Flower: http://localhost:5555
```

### 📈 Available Dashboards

**Grafana Dashboards:**
- **System Overview**: Memory, CPU, and threshold monitoring
- **Agent Activity**: Active agents and processing modes
- **Task Performance**: Execution rates, duration, and failures
- **Processing Quality**: PDF/Excel volume and validation accuracy
- **Consolidation Events**: Memory pressure responses

### 📊 Key Metrics Tracked

**System Metrics:**
- Memory usage (total, available, percentage)
- CPU utilization
- Memory threshold levels (CRITICAL/LOW/MEDIUM/HIGH)
- Processing modes (minimal/consolidated/distributed)

**Agent Metrics:**
- Active agent counts by type
- Task execution rates and duration
- Memory usage per agent
- Task failure rates
- Agent spawn success/failure rates

**Performance Metrics:**
- PDF processing chunk counts
- Excel processing row counts
- Validation accuracy percentages
- Consolidation event frequency

### 🔔 Intelligent Alerting

**Automated Alerts:**
- **Critical Memory Usage** (>95%): Immediate consolidation recommended
- **High Task Failure Rate** (>10%): System health degradation
- **Extended Task Duration** (>10min): Performance bottlenecks
- **Frequent Consolidations**: Potential memory leaks
- **System Instability**: Rapid threshold changes

**Alert Severity Levels:**
- 🔴 **CRITICAL**: Immediate action required
- 🟡 **WARNING**: Monitor and plan action
- 🔵 **INFO**: Informational notices

### 📊 Telemetry Analysis Features

**Trend Detection:**
- Memory usage patterns over time
- Task load forecasting (24-hour predictions)
- Performance degradation detection
- Anomaly identification

**Health Scoring:**
- Overall system health score (0-100)
- Component-specific health status
- Trend-based recommendations

### 📱 Monitoring Endpoints

```bash
# System status
curl http://localhost:8000/system-status

# Memory statistics
curl http://localhost:8000/memory-stats

# Prometheus metrics
curl http://localhost:8000/metrics

# Agent telemetry
curl http://localhost:8000/agent-telemetry

# Health check
curl http://localhost:8000/health
```

### 🔧 Advanced Analytics

**Trend Analysis API:**
```python
# Analyze memory usage trends
analysis = telemetry_analyzer.perform_trend_analysis(
    metric_name="memory_usage_percent", 
    days_back=7
)

print(f"Trend: {analysis.direction}")
print(f"24h Forecast: {analysis.forecast_24h}")
print(f"Confidence: {analysis.confidence:.2f}")
```

**Custom Alert Configuration:**
```python
# Customize alert thresholds
thresholds = {
    'memory_usage_critical': 95.0,
    'memory_usage_warning': 85.0,
    'task_failure_rate_critical': 10.0,
    'avg_task_duration_warning': 300.0
}
```

## 🔍 Memory Management Deep Dive

### Threshold Levels

1. **HIGH (>6GB available)**
   - Spawn specialized agents
   - Use optimized multimodal processing
   - Full feature availability

2. **MEDIUM (3-6GB available)**
   - Moderate consolidation
   - Standard multimodal processing
   - Selective feature availability

3. **LOW (1-3GB available)**
   - Aggressive consolidation
   - Basic processing mode
   - Sequential processing only

4. **CRITICAL (<1GB available)**
   - Minimal mode
   - Single orchestrator
   - Emergency memory cleanup

### Automatic Actions

- **Memory Pressure Detection**: Continuous monitoring
- **Garbage Collection**: Automatic cleanup when needed
- **Model Unloading**: Dynamic model management
- **Agent Consolidation**: Automatic capability merging

## 🛠️ Development

### Adding New Agents

1. **Create Agent Class**
   ```python
   class CustomIntelligenceAgent(AdaptiveAgentTask):
       agent_type = "custom_intelligence"
       base_capabilities = [
           AgentCapability("custom_processing", 512)
       ]
       
       def execute_main_logic(self, *args, **kwargs):
           # Implementation here
           pass
   ```

2. **Register Celery Task**
   ```python
   @shared_task(bind=True, base=CustomIntelligenceAgent)
   def custom_intelligence_task(self, *args, **kwargs):
       return self.run(*args, **kwargs)
   ```

3. **Update Orchestrator**
   - Add to task routing
   - Update consolidation strategies

### Memory Optimization

- **Lazy Loading**: Initialize services only when needed
- **Resource Cleanup**: Proper cleanup in finally blocks
- **Model Caching**: Efficient model management
- **Batch Processing**: Optimize batch sizes based on memory

## 📈 Performance

### Benchmarks

- **High Memory**: 5-8 concurrent agents, full multimodal processing
- **Medium Memory**: 3-5 agents, standard processing
- **Low Memory**: 1-2 agents, basic processing
- **Memory Adaptation**: <5 second adaptation time

### Optimization Tips

1. **Monitor Memory Usage**: Use `/memory-stats` endpoint
2. **Adjust Thresholds**: Configure based on your hardware
3. **Batch Size Tuning**: Optimize for your memory constraints
4. **Model Selection**: Choose appropriate processing modes

## 🐛 Troubleshooting

### Common Issues

1. **Memory Pressure**
   - Check `/memory-stats`
   - Review consolidation suggestions
   - Consider increasing memory limits

2. **Agent Failures**
   - Check Celery worker logs
   - Verify Redis connectivity
   - Review task timeouts

3. **Docker Issues**
   - Ensure Docker has sufficient memory
   - Check service health with `docker-compose ps`
   - Review logs with `docker-compose logs`

### Debug Commands

```bash
# Check system status
curl http://localhost:8000/system-status

# Monitor Celery
celery -A autonomous_agents.worker inspect active

# Check Docker resources
docker stats

# View logs
docker-compose logs -f celery-worker
```

## 🚀 Deployment

### Production Checklist

- [ ] Configure memory thresholds for your hardware
- [ ] Set up external monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup and recovery
- [ ] Performance testing completed
- [ ] Security review completed

### Scaling

- **Horizontal**: Add more worker nodes
- **Vertical**: Increase memory per node
- **Load Balancing**: Distribute requests across instances
- **Queue Management**: Optimize Celery queue configuration

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create GitHub issues for bugs
- Check logs and monitoring dashboards
- Review troubleshooting section
- Use debug endpoints for diagnostics

---

**Ready for Production**: This autonomous agent system provides enterprise-grade intelligent document processing with adaptive resource management and comprehensive monitoring capabilities.
