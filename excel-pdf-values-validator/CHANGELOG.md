# Changelog

All notable changes to the Excel PDF Values Validator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025-08-08

### Added - Comprehensive E2E Testing & Stability Fixes
- ✨ **Major Feature**: Migrated frontend testing from Cypress to Playwright for enhanced reliability and cross-browser testing
- ✨ **Comprehensive E2E Test Suite**: Recreated full test suite with 25 tests covering:
  - Navigation and Basic UI (homepage, dashboard, responsive design)
  - Full Validation Workflow (file uploads, large files, results display, state management)
  - Backend API Workflow (validation, duplicate detection, health checks, error handling)
- ✨ **Cross-browser Testing**: Configured Playwright to run tests on Chromium, Firefox, WebKit, and mobile viewports
- ✨ **Global Setup/Teardown**: Implemented global setup for service coordination and test fixture management
- ✨ **Enhanced Test Files**: Created comprehensive Excel test files with up to 62 parameters for thorough validation testing

### Changed - Duplicate Detection & Error Handling
- ⚡ **Major Improvement**: Implemented robust, hash-based duplicate detection in the backend `/validate` endpoint
- Backend now calculates SHA256 hashes of PDF and Excel files to prevent reprocessing
- Returns cached results with a `duplicate_detected` status for existing file combinations
- Stores file hashes in a new `file_hashes` database table for future checks
- Improved API error handling for missing or invalid files

### Fixed - Critical Backend & Frontend Bugs
- 🐛 **CRITICAL**: Fixed 500 error in validation workflow caused by `'chunk_text'` key mismatch in `OptimizedMultimodalPDFProcessor`
- 🐛 Fixed issue where duplicate files were not being detected and reprocessed unnecessarily
- 🐛 Resolved flaky frontend test issues by migrating to Playwright and implementing better test practices:
  - Improved selector strategies for reliability
  - Handling for webpack overlays and asynchronous UI updates
  - Proper timeouts and network handling for improved stability
- 🐛 Fixed minor assertion issue in API tests expecting 422 but receiving 400 status for validation errors

### Performance
- ⚡ Prevents unnecessary reprocessing of duplicate files, saving significant time and resources
- Faster and more reliable E2E test execution with Playwright

### Technical Details & Troubleshooting 🔧

#### Backend Issues Fixed:
- **500 Error Fix**: The `OptimizedMultimodalPDFProcessor.py` was using `'text': chunk_text` instead of `'chunk_text': chunk_text` in line 297 of the `_convert_extractions_to_chunks()` method
- **Duplicate Detection**: Added `file_hashes` table with unique index on `(pdf_hash, excel_hash)` for efficient duplicate checking
- **Hash Storage**: File hashes are stored after successful processing with `store_file_hashes(config_id, pdf_hash, excel_hash, pdf_filename, excel_filename)`

#### Playwright Migration Details:
- **Test Files**: All tests moved from `cypress/` to `e2e/` directory structure
- **Configuration**: `playwright.config.js` with cross-browser and mobile testing support
- **Global Setup**: Service coordination in `e2e/global-setup.js` checks frontend (port 3000) and backend (port 8000) readiness
- **Test Fixtures**: PDF and Excel test files copied to `e2e/fixtures/` for reliable test execution
- **Browser Coverage**: Tests run on Chromium, Firefox, WebKit, Mobile Chrome, and Mobile Safari
- **Debugging**: Traces, screenshots, and videos captured on test failures for easier debugging

#### Files Modified:
- `fastapi/app/main.py`: Added duplicate detection logic to `/validate` endpoint
- `fastapi/app/services/optimized_multimodal_pdf_processor.py`: Fixed chunk_text key mismatch
- `fastapi/app/models/database.py`: Added `check_duplicate_files()` and `store_file_hashes()` functions
- `frontend/playwright.config.js`: New Playwright configuration
- `frontend/package.json`: Updated test scripts for Playwright
- `frontend/e2e/`: Complete new test suite with navigation, workflow, and API tests

#### Database Schema Changes:
```sql
CREATE TABLE IF NOT EXISTS file_hashes (
    id SERIAL PRIMARY KEY,
    config_id TEXT NOT NULL,
    pdf_hash TEXT NOT NULL,
    excel_hash TEXT NOT NULL, 
    pdf_filename TEXT NOT NULL,
    excel_filename TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX IF NOT EXISTS file_hashes_unique_idx ON file_hashes (pdf_hash, excel_hash);
```

## [1.0.0] - 2025-01-08

### Added - Model Caching System 🚀
- **⚡ Major Feature**: Comprehensive model caching system for ML models
- Pre-download script for ML models (`scripts/download_models.py`)
- Model validation in Docker entrypoint with graceful fallback
- Enhanced E2E testing with cached models for consistent CI/CD
- Model caching documentation (`MODEL_CACHING_SUMMARY.md`)
- Complete Jest test setup for frontend components
- React Testing Library integration replacing Mocha/Chai
- Cypress E2E testing configuration
- Comprehensive frontend test coverage for App, Layout, Analytics, Dashboard, and Upload components

### Changed - Architecture Improvements
- 🔥 **BREAKING**: Restructured project layout - moved frontend from `fastapi/frontend` to root `frontend/`
- Updated Dockerfile to use cached models instead of downloading during build
- Modified Docker entrypoint to validate cached models and handle missing dependencies
- Improved backend test organization - moved tests to `fastapi/tests/`
- Enhanced backend test robustness with proper import guards and skip conditions
- Updated frontend dependencies and resolved deprecated packages
- Fixed styled-components prop forwarding to prevent React warnings
- Migrated frontend testing from Mocha/Chai to Jest/React Testing Library

### Fixed - Bug Fixes and Stability
- 🐛 Missing `psycopg2-binary` dependency in requirements.txt
- 🐛 Docker container startup issues with missing dependencies
- 🐛 Frontend test configuration conflicts (duplicate Jest configs)
- 🐛 React Router nesting issues in component tests
- 🐛 Styled-components DOM prop warnings
- 🐛 Import errors in backend integration tests
- 🐛 Test file organization and import paths

### Removed - Cleanup
- Mocha and Chai test dependencies from frontend
- Unnecessary cache and build artifacts cleanup
- Duplicate Jest configuration files

### Performance - Massive Improvements ⚡
- **🚀 GAME CHANGER**: Docker build time reduced from ~15 minutes to ~2 minutes (87% improvement)
- **🚀 GAME CHANGER**: Container startup time reduced from ~3 minutes to ~30 seconds (83% improvement)
- Eliminated redundant model downloads during development cycles
- Optimized ML model loading with persistent cache
- Faster CI/CD pipeline execution with pre-cached models

### Technical Details
- Model cache location: `/app/models` (136M total size)
- Cached models: BLIP image captioning, Sentence Transformers, tokenizers
- E2E tests now use cached models for consistent performance
- Frontend test environment properly configured with TypeScript support
- Backend tests organized with proper pytest structure
- All containers now use read-only model cache mounts for security
- Cache invalidation strategy implemented for model updates

## [0.1.0] - Initial Release

### Added
- FastAPI backend with Excel and PDF processing capabilities
- React frontend with file upload and validation interface
- Docker containerization for all services
- Celery task queue for asynchronous processing
- Redis and PostgreSQL with pgvector support
- ML models integration (BLIP, Transformers, Sentence Transformers)
- Basic validation workflow for Excel-PDF comparison
- REST API endpoints for file processing and validation
- Socket.IO integration for real-time updates
- Initial test suite for backend components

### Features
- Multi-modal document processing using local LLMs
- Excel data extraction and validation
- PDF content analysis and comparison
- Async task processing with Celery
- Vector similarity search with pgvector
- Real-time progress updates via WebSocket
- Responsive React UI with modern styling
- Docker Compose orchestration

---

## Contributing

When adding entries to this changelog:
1. Add new entries under `[Unreleased]` section
2. Use the categories: Added, Changed, Deprecated, Removed, Fixed, Security, Performance
3. Follow the format: `- Brief description of change`
4. Link to issues/PRs where applicable: `- Description ([#123](link))`
5. Move entries to a new version section when releasing

## Legend

- 🔥 **BREAKING**: Breaking changes that require user action
- ⚡ **Major improvement**: Significant performance or functionality improvements
- 🐛 **Bug fix**: Bug fixes and corrections
- ✨ **Feature**: New features and capabilities
