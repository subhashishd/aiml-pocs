# Changelog

All notable changes to the Excel PDF Values Validator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive model caching system for ML models
- Pre-download script for ML models (`scripts/download_models.py`)
- Model validation in Docker entrypoint
- Enhanced E2E testing with cached models
- Model caching documentation (`MODEL_CACHING_SUMMARY.md`)
- Complete Jest test setup for frontend components
- React Testing Library integration
- Cypress E2E testing configuration
- Comprehensive frontend test coverage for App, Layout, Analytics, Dashboard, and Upload components

### Changed
- **BREAKING**: Restructured project layout - moved frontend from `fastapi/frontend` to root `frontend/`
- Updated Dockerfile to use cached models instead of downloading during build
- Modified Docker entrypoint to validate cached models and handle missing dependencies
- Improved backend test organization - moved tests to `fastapi/tests/`
- Enhanced backend test robustness with proper import guards and skip conditions
- Updated frontend dependencies and resolved deprecated packages
- Fixed styled-components prop forwarding to prevent React warnings
- Migrated frontend testing from Mocha/Chai to Jest/React Testing Library

### Fixed
- Missing `psycopg2-binary` dependency in requirements.txt
- Docker container startup issues with missing dependencies
- Frontend test configuration conflicts (duplicate Jest configs)
- React Router nesting issues in component tests
- Styled-components DOM prop warnings
- Import errors in backend integration tests
- Test file organization and import paths

### Removed
- Mocha and Chai test dependencies from frontend
- Unnecessary cache and build artifacts cleanup
- Duplicate Jest configuration files

### Performance
- **Major improvement**: Docker build time reduced from ~15 minutes to ~2 minutes with model caching
- **Major improvement**: Container startup time reduced from ~3 minutes to ~30 seconds
- Eliminated redundant model downloads during development cycles
- Optimized ML model loading with persistent cache

### Technical Details
- Model cache location: `/app/models` (136M total size)
- Cached models: BLIP, Sentence Transformers, tokenizers
- E2E tests now use cached models for consistent performance
- Frontend test environment properly configured with TypeScript support
- Backend tests organized with proper pytest structure
- All containers now use read-only model cache mounts for security

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
