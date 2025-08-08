from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from .services.pdf_processor import PDFProcessor
from .services.local_multimodal_pdf_processor import LocalMultimodalPDFProcessor
from .services.optimized_multimodal_pdf_processor import OptimizedMultimodalPDFProcessor
from .services.excel_processor import ExcelProcessor
from .services.embedding_service import EmbeddingService
from .services.validation_service import ValidationService
from .models.database import init_db
from .utils.model_init import initialize_models

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Excel-PDF Values Validator", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services based on configuration
use_multimodal = os.getenv('USE_MULTIMODAL_PDF', 'false').lower() == 'true'
use_optimized = os.getenv('USE_OPTIMIZED_MULTIMODAL', 'true').lower() == 'true'

if use_multimodal:
    if use_optimized:
        logger.info("Using optimized multimodal PDF processor")
        pdf_processor = OptimizedMultimodalPDFProcessor()
    else:
        logger.info("Using standard multimodal PDF processor")
        pdf_processor = LocalMultimodalPDFProcessor()
else:
    logger.info("Using traditional PDF processor")
    pdf_processor = PDFProcessor()

excel_processor = ExcelProcessor()
embedding_service = EmbeddingService()
validation_service = ValidationService()

@app.on_event("startup")
async def startup_event():
    """Initialize database and models on startup"""
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize and warm up models
    model_init_success = initialize_models()
    if model_init_success:
        logger.info("Models initialized successfully")
    else:
        logger.warning("Model initialization failed, but continuing...")
    
    logger.info("Application started successfully")

@app.get("/")
async def root():
    """API root endpoint"""
    return {"message": "Excel-PDF Values Validator API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"message": "Excel-PDF Values Validator API is running"}

@app.get("/memory-stats")
async def get_memory_stats():
    """Get current memory usage statistics"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    stats = {
        "process_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
        "process_memory_percent": round(process.memory_percent(), 2),
        "system_memory_available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
        "processor_type": "optimized" if use_optimized and use_multimodal else ("multimodal" if use_multimodal else "traditional")
    }
    
    # Add model-specific stats if using optimized processor
    if hasattr(pdf_processor, 'get_memory_stats'):
        model_stats = pdf_processor.get_memory_stats()
        stats.update({"model_stats": model_stats})
    
    return stats

@app.post("/create-embeddings")
async def create_embeddings(pdf_file: UploadFile = File(...)):
    """
    Create embeddings from PDF file and store in database
    """
    try:
        logger.info(f"Processing PDF file: {pdf_file.filename}")
        
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await pdf_file.read()
            temp_file.write(content)
            temp_pdf_path = temp_file.name
        
        try:
            # Process PDF and extract parameter-value pairs
            chunks = pdf_processor.process_pdf(temp_pdf_path, pdf_file.filename)
            
            if not chunks:
                raise HTTPException(status_code=400, detail="No parameter-value pairs found in PDF")
            
            # Create embeddings and store in database
            config_id = await embedding_service.create_embeddings(
                chunks=chunks,
                filename=pdf_file.filename,
                pdf_path=temp_pdf_path
            )
            
            logger.info(f"Successfully created embeddings for {pdf_file.filename} with config_id: {config_id}")
            
            return {
                "status": "success",
                "message": f"Successfully processed {len(chunks)} chunks from {pdf_file.filename}",
                "config_id": config_id,
                "chunks_processed": len(chunks)
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/validate")
async def validate_values(
    pdf_file: UploadFile = File(...),
    excel_file: UploadFile = File(...)
):
    """
    Validate Excel values against PDF content using semantic matching
    """
    try:
        logger.info(f"Validating Excel: {excel_file.filename} against PDF: {pdf_file.filename}")
        
        # Validate file types
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="PDF file must have .pdf extension")
        if not excel_file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Excel file must have .xlsx or .xls extension")
        
        # Save uploaded files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            pdf_content = await pdf_file.read()
            temp_pdf.write(pdf_content)
            temp_pdf_path = temp_pdf.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_excel:
            excel_content = await excel_file.read()
            temp_excel.write(excel_content)
            temp_excel_path = temp_excel.name
        
        try:
            # Process files
            pdf_chunks = pdf_processor.process_pdf(temp_pdf_path, pdf_file.filename)
            excel_data = excel_processor.process_excel(temp_excel_path)
            
            if not pdf_chunks:
                raise HTTPException(status_code=400, detail="No parameter-value pairs found in PDF")
            if not excel_data:
                raise HTTPException(status_code=400, detail="No parameter-value pairs found in Excel")
            
            # Create temporary embeddings for this validation
            config_id = await embedding_service.create_embeddings(
                chunks=pdf_chunks,
                filename=pdf_file.filename,
                pdf_path=temp_pdf_path
            )
            
            # Perform validation
            validation_result = await validation_service.validate_values(
                excel_data=excel_data,
                config_id=config_id,
                pdf_filename=pdf_file.filename,
                excel_filename=excel_file.filename
            )
            
            # Generate result file
            result_filename = f"validation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            result_path = f"/app/data/{result_filename}"
            
            # Ensure data directory exists
            os.makedirs("/app/data", exist_ok=True)
            
            with open(result_path, 'w') as f:
                f.write(validation_result['report_text'])
            
            return {
                "status": "success",
                "report_text": validation_result['report_text'],
                "summary": validation_result['summary'],
                "result_file": result_filename
            }
            
        finally:
            # Clean up temporary files
            for temp_path in [temp_pdf_path, temp_excel_path]:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during validation: {str(e)}")

# ===============================
# DASHBOARD ENDPOINTS
# ===============================

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    import psutil
    
    # Mock data for now - can be enhanced with real stats later
    stats = {
        "total_tasks": 0,
        "completed_tasks": 0,
        "pending_tasks": 0,
        "failed_tasks": 0,
        "success_rate": 100.0,
        "avg_processing_time": 0,
        "memory_usage": {
            "used_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2),
            "available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
            "percentage": psutil.virtual_memory().percent
        },
        "system_health": "healthy"
    }
    return stats

# ===============================
# TASK ENDPOINTS
# ===============================

@app.get("/tasks/recent")
async def get_recent_tasks(limit: int = 5):
    """Get recent tasks"""
    # Mock data for now - can be enhanced with real task tracking later
    return {
        "tasks": [],
        "total": 0,
        "message": "No recent tasks found"
    }

# ===============================
# FILE UPLOAD ENDPOINTS
# ===============================

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file for processing"""
    try:
        # Check if filename exists
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
            
        # Validate file type
        allowed_extensions = ['.pdf', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "/app/data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File uploaded successfully: {safe_filename}")
        
        return {
            "status": "success",
            "message": f"File {file.filename} uploaded successfully",
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_size": len(content),
            "file_type": file_extension,
            "upload_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/download/{filename}")
async def download_result(filename: str):
    """
    Download validation result file
    """
    file_path = f"/app/data/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='text/plain'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
