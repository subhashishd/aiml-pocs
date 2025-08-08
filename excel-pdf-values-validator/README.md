# Excel-PDF Values Validator

## Overview

The **Excel-PDF Values Validator** is an advanced AI-powered tool designed to validate numerical values extracted from Excel spreadsheets against parameter-value pairs found in PDF documents. The application uses local multimodal LLMs to visually analyze PDF layouts and extract key-value pairs, making it robust to various document formats and layouts.

## Key Features

- **Local Multimodal LLM Processing**: Uses BLIP vision-language models running locally for edge deployment to analyze PDF pages visually and extract parameter-value pairs regardless of layout
- **Layout-Agnostic Extraction**: Works with any PDF layout by leveraging visual understanding rather than relying on specific table structures
- **Excel Data Processing**: Extracts parameters and their values from Excel for comparison against PDF data
- **Hybrid Matching Strategy**: Combines exact text matching with semantic similarity for robust parameter identification
- **Exact Precision Validation**: Ensures scientific precision by using exact numerical comparisons for scientific calculations
- **Edge Deployment Ready**: All models run locally without internet dependency, perfect for secure edge environments
- **Dockerized Deployment**: Provides a containerized environment with pre-cached models for consistency across deployments

## Architecture

### Core Components

- **FastAPI**: Provides the API framework to handle file uploads and processing endpoints
- **Frontend**: Simple HTML/JavaScript interface for file upload and result display

### Processing Pipeline

1. **Multimodal PDF Processing**:
   - Converts PDF pages to images using PyMuPDF
   - Uses local BLIP (Bootstrapping Language-Image Pre-training) model to visually analyze each page
   - Extracts parameter-value pairs by "reading" the document like a human would
   - Falls back to OCR and traditional text extraction if vision model fails

2. **Excel Processing**:
   - Parses Excel files using openpyxl/pandas
   - Extracts parameter-value-unit triplets
   - Validates data structure and types

3. **Semantic Embedding & Storage**:
   - Creates embeddings using BGE-small-en-v1.5 sentence transformer
   - Stores in PostgreSQL with pgVector extension for similarity search
   - Maintains metadata about extraction method and source

4. **Hybrid Validation**:
   - **Step 1**: Exact text matching for parameter names
   - **Step 2**: Semantic similarity search for fuzzy matching
   - **Step 3**: Exact numerical comparison for scientific precision
   - Generates detailed validation reports with pass/fail status

### Local Model Stack (Edge-Ready)

- **Vision Model**: Salesforce/blip-image-captioning-base (~990MB)
- **Text Embedding**: BAAI/bge-small-en-v1.5 (~133MB)
- **OCR Fallback**: Tesseract (when available)
- **All models pre-cached in Docker image for offline operation**

### Database Schema

```sql
CREATE TABLE pdf_chunks (
    id SERIAL PRIMARY KEY,
    config_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(384),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Configuration Options

- `USE_MULTIMODAL_PDF=true/false`: Enable/disable multimodal processing
- `USE_LIGHTWEIGHT_MODEL=true/false`: Use smaller models for resource-constrained environments
- `TRANSFORMERS_OFFLINE=1`: Force offline model usage

## Deployment

1. **Docker Setup**:
   - Builds the application and sets up containers for the FastAPI application and PostgreSQL.
   - Uses volumes to store data and embeddings, enabling persistence across container restarts.

2. **Azure Pipelines**:
   - Configured to automate build and deployment processes.
   - Integrates with GitHub Container Registry to store Docker images.

3. **Local Development**:
   - Provides `docker-compose.dev.yml` for local development, including live-reload support for fast development cycles.

## Testing

- Comprehensive test suite available in the `tests` directory.
- Includes unit tests for core components and integration tests for the end-to-end workflow.
- Local and Docker-based testing options ensure reliability in both environments.

## Future Enhancements

- Enhance table extraction for more complex PDF layouts.
- Improve the semantic matching algorithm with advanced models.
- Expand support for more diverse document and data formats.

## Getting Started

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd excel-pdf-values-validator
   ```

2. **Build and Run Docker Containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**:
   - UI available at `http://localhost:8000`
   - API documentation at `http://localhost:8000/docs`

4. **Run Tests**:
   ```bash
   cd tests
   python run_tests.py
   ```

## Contributions

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

---

For more detailed documentation and setup instructions, please refer to the `docs/` directory or the online documentation at [Project Documentation](<document-link>).
