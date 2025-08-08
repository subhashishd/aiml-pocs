# Autonomous Agents Testing Infrastructure

This directory contains comprehensive tests for the autonomous agent system with integrated Prometheus metrics and Grafana dashboard support.

## 🧪 Test Suite Overview

The test suite verifies all core functionality of the autonomous agent system:

### Core Test Categories

1. **Memory Management Tests** (`test_memory_manager.py`, `test_memory_manager_simple.py`)
   - Memory usage monitoring and thresholds
   - Agent spawning decisions based on available resources
   - Consolidation strategy suggestions
   - Environment variable configuration

2. **Agent Task Tests** (`test_autonomous_agents_clean.py`)
   - Base agent functionality and initialization
   - Capability absorption and handling
   - Memory usage tracking
   - Telemetry collection

3. **Orchestrator Tests**
   - Distributed vs consolidated processing strategies
   - Task coordination and management
   - System status monitoring
   - Memory-aware decision making

4. **Intelligence Agent Tests**
   - PDF processing with memory-adaptive strategies
   - Excel data processing
   - Validation intelligence
   - Consolidated processing agents

## 🚀 Running Tests

### Quick Test Run

```bash
# Run all tests with automatic infrastructure setup
./scripts/run_all_tests.sh
```

### Manual Infrastructure Setup

1. **Start Redis for Celery testing:**
```bash
./scripts/start_test_infrastructure.sh
```

2. **Run tests with infrastructure:**
```bash
CELERY_BROKER_URL=redis://localhost:6380/0 \
CELERY_RESULT_BACKEND=redis://localhost:6380/0 \
CELERY_ALWAYS_EAGER=True \
python -m pytest tests/ -v
```

3. **Stop infrastructure:**
```bash
docker stop redis-test
```

### Running Specific Test Categories

```bash
# Memory management tests only
python -m pytest tests/unit/test_memory_manager*.py -v

# Agent functionality tests only  
python -m pytest tests/test_autonomous_agents_clean.py -v

# Run with coverage
python -m pytest tests/ --cov=app/autonomous_agents --cov-report=html
```

## 🏗️ Test Infrastructure

### Docker Components

- **Redis**: Message broker for Celery tasks (port 6380)
- **Test isolation**: Each test uses isolated fixtures and mocks

### Test Configuration

- **Celery**: Configured for eager execution in tests
- **Mocking**: Comprehensive service mocking for isolated testing
- **Fixtures**: Reusable test fixtures in `conftest.py`

## 📋 Test Fixtures

### Memory Management Fixtures

- `memory_manager`: Configured MemoryManager instance
- `temp_files`: Temporary PDF and Excel files for testing

### Service Mocks

- `mock_pdf_processor`: Mock PDF processing service
- `mock_excel_processor`: Mock Excel processing service  
- `mock_validation_service`: Mock validation service
- `setup_test_environment`: Auto-applied service import mocking

### Celery Configuration

- `celery_app`: Test Celery application
- `celery_worker`: Test Celery worker
- `redis_connection`: Redis connection for integration tests

## 🎯 Test Coverage

The test suite covers:

### ✅ Memory Management
- [x] Memory threshold detection (HIGH, MEDIUM, LOW, CRITICAL)
- [x] Agent spawning decisions based on available resources
- [x] Consolidation strategy recommendations
- [x] Agent registration/unregistration tracking
- [x] Environment-based configuration

### ✅ Agent Orchestration  
- [x] Distributed processing strategy (high memory)
- [x] Consolidated processing strategy (low memory)
- [x] Task coordination and result aggregation
- [x] System status monitoring
- [x] Error handling and recovery

### ✅ Intelligence Agents
- [x] PDF intelligence with memory-adaptive processing
- [x] Excel intelligence with data extraction
- [x] Validation intelligence with semantic matching
- [x] Consolidated processing for memory-constrained environments
- [x] Capability absorption and dynamic adaptation

### ✅ Monitoring & Metrics
- [x] Prometheus metrics collection
- [x] Telemetry data gathering
- [x] Memory usage tracking
- [x] Agent performance monitoring
- [x] System health indicators

### ✅ Infrastructure Integration
- [x] Docker-based testing infrastructure
- [x] Redis/Celery integration
- [x] Service import handling
- [x] Graceful fallback mechanisms

## 🐛 Troubleshooting

### Common Issues

1. **Docker not running**
   ```
   Solution: Start Docker Desktop/daemon before running tests
   ```

2. **Port 6380 in use**
   ```bash
   # Check what's using the port
   lsof -i :6380
   
   # Stop existing Redis test container
   docker stop redis-test
   ```

3. **Import errors**
   ```
   Solution: Tests use comprehensive mocking to handle missing dependencies
   Ensure PYTHONPATH includes the app directory
   ```

4. **Celery timeout errors**
   ```
   Solution: Tests use CELERY_ALWAYS_EAGER=True for synchronous execution
   Check Redis connectivity if using real broker
   ```

## 📈 Performance Expectations

- **Test execution time**: ~5-15 seconds
- **Infrastructure startup**: ~3-5 seconds  
- **Memory usage**: Minimal (mocked services)
- **Test isolation**: Each test is fully isolated

## 🔧 Test Customization

### Environment Variables

```bash
# Custom Redis configuration
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0

# Test behavior
CELERY_ALWAYS_EAGER=True  # Synchronous task execution
TESTING=True              # Enable test mode
MAX_MEMORY_GB=8.0         # Override memory limits
```

### Adding New Tests

1. **Create test file** in appropriate directory
2. **Use existing fixtures** from `conftest.py`  
3. **Follow naming convention**: `test_*.py`
4. **Add comprehensive mocking** for external dependencies
5. **Update test scripts** if needed

## 📚 Related Documentation

- [Autonomous Agents Architecture](../app/autonomous_agents/README.md)
- [Memory Management System](../app/autonomous_agents/memory_manager.py)
- [Prometheus Metrics](../monitoring/prometheus/)
- [Grafana Dashboards](../monitoring/grafana/)
- [Docker Infrastructure](../docker-compose.test.yml)
