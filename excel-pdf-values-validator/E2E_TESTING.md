# E2E Integration Testing Setup

This document describes the complete End-to-End (E2E) integration testing setup for the Excel-PDF Values Validator application.

## Overview

The E2E testing setup includes:
- **Docker Compose** environment with full backend + frontend stack
- **Cypress** for browser automation and testing
- **Real API integration** testing with backend services
- **Comprehensive test scenarios** covering user workflows
- **CI/CD ready** configuration

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Cypress E2E   │────│  React Frontend │────│  FastAPI Backend│
│   Test Runner   │    │                 │    │                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                └─────────────────┬──────┘
                                                  │
                               ┌─────────────────────────────────┐
                               │                                 │
                               │        Support Services         │
                               │   ┌─────────┐  ┌─────────────┐  │
                               │   │ Redis   │  │ PostgreSQL  │  │
                               │   │         │  │ (pgvector)  │  │
                               │   └─────────┘  └─────────────┘  │
                               └─────────────────────────────────┘
```

## Files Structure

```
project/
├── docker-compose.test.yml          # Docker compose for E2E testing
├── scripts/
│   ├── run-e2e-tests.sh            # Automated E2E test runner
│   └── start-test-env.sh            # Manual testing environment
├── frontend/
│   ├── cypress.config.cjs           # Cypress configuration
│   ├── cypress/
│   │   ├── integration/
│   │   │   ├── sample_spec.js       # Original navigation tests
│   │   │   └── full_integration_spec.js  # Full stack integration tests
│   │   ├── support/
│   │   │   ├── e2e.js               # Global setup and commands
│   │   │   └── commands.js          # Custom Cypress commands
│   │   └── fixtures/
│   │       ├── sample.pdf           # Test PDF file
│   │       └── api-responses.json   # Mock API responses
│   └── package.json                 # Updated with E2E scripts
```

## Quick Start

### 1. Prerequisites

Make sure you have Docker and Docker Compose installed:
```bash
docker --version
docker-compose --version
```

### 2. Run Full E2E Tests (Automated)

```bash
# From project root
./scripts/run-e2e-tests.sh
```

This script will:
- Start all required services (PostgreSQL, Redis, Backend, Frontend)
- Wait for services to be healthy
- Run Cypress tests in headless mode
- Clean up containers after completion

### 3. Start Test Environment (Manual)

```bash
# Start services for manual testing
./scripts/start-test-env.sh

# Then in another terminal, run Cypress UI
cd frontend
npm run test:e2e
```

### 4. Available Commands

From the frontend directory:

```bash
# Start Cypress interactive mode
npm run test:e2e

# Run Cypress tests headlessly  
npm run test:e2e:headless

# Run full Docker E2E tests
npm run test:e2e:docker

# Start test environment
npm run test:integration

# Run all tests (unit + E2E)
npm run test:all
```

## Test Scenarios

### 1. API Integration Tests
- Backend health checks
- API endpoint connectivity
- Real data loading from backend

### 2. User Interface Tests
- Navigation between pages
- Form interactions
- File upload interface
- Responsive design

### 3. File Processing Flow
- File upload and validation
- Processing status updates
- Results display
- Error handling

### 4. Real-time Features
- WebSocket connectivity
- Live updates
- Progress tracking

### 5. Performance Tests
- Page load times
- API response times
- Memory usage

### 6. Cross-browser Tests
- Different viewport sizes
- Mobile responsiveness
- Browser compatibility

## Environment Configuration

The test environment uses separate containers and ports to avoid conflicts:

| Service | Port | Container | Database |
|---------|------|-----------|----------|
| Frontend | 3000 | frontend-test | - |
| Backend | 8000 | fastapi-backend-test | - |
| PostgreSQL | 5433 | pgvector-db-test | validation_agents_test |
| Redis | 6379 | redis-test | - |

## Environment Variables

Key environment variables for testing:

```bash
# Cypress
CYPRESS_baseUrl=http://frontend:3000
CYPRESS_apiUrl=http://backend:8000

# Backend
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/validation_agents_test
REDIS_URL=redis://redis:6379/0
ENVIRONMENT=test

# Frontend  
REACT_APP_API_URL=http://backend:8000
REACT_APP_ENVIRONMENT=test
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests
on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run E2E Tests
        run: |
          chmod +x ./scripts/run-e2e-tests.sh
          ./scripts/run-e2e-tests.sh
          
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: cypress-results
          path: frontend/cypress/videos/
```

## Custom Cypress Commands

The setup includes several custom commands:

```javascript
// File upload simulation
cy.uploadFile('sample.pdf', 'application/pdf');

// API health check
cy.checkApiHealth();

// Wait for app to load
cy.waitForAppLoad();

// Clear application data
cy.clearAllData();

// Network request stubbing
cy.stubApiCall('GET', '/api/tasks', mockResponse);
```

## Troubleshooting

### Common Issues

1. **Services not starting**: Check Docker daemon is running
   ```bash
   docker info
   ```

2. **Port conflicts**: Ensure ports 3000, 8000, 5433, 6379 are available
   ```bash
   lsof -i :3000
   ```

3. **Cypress tests timing out**: Increase timeout in cypress.config.cjs
   ```javascript
   defaultCommandTimeout: 15000
   ```

4. **Backend not healthy**: Check backend logs
   ```bash
   docker-compose -f docker-compose.test.yml logs backend
   ```

### Debug Commands

```bash
# Check service status
docker-compose -f docker-compose.test.yml ps

# View service logs
docker-compose -f docker-compose.test.yml logs [service]

# Access service container
docker-compose -f docker-compose.test.yml exec [service] sh

# Clean up everything
docker-compose -f docker-compose.test.yml down --volumes --remove-orphans
```

## Best Practices

1. **Test Isolation**: Each test should be independent and clean up after itself
2. **Data Management**: Use fixtures and factories for test data
3. **Wait Strategies**: Use proper waits instead of arbitrary timeouts
4. **Error Handling**: Test both success and failure scenarios  
5. **Performance**: Keep tests fast and focused
6. **Maintenance**: Update tests when features change

## Extending Tests

To add new test scenarios:

1. Create new spec files in `cypress/integration/`
2. Add fixtures in `cypress/fixtures/`
3. Create custom commands in `cypress/support/commands.js`
4. Update API mocks in `cypress/fixtures/api-responses.json`

## Monitoring and Reporting

- Cypress Dashboard integration for test results
- Video recording of failed tests
- Screenshot capture on failures
- Performance metrics collection
- Integration with monitoring tools

---

For more information, see the individual configuration files and the main project documentation.
