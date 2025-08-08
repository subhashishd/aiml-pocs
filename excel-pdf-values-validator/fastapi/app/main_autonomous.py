"""
FastAPI Application with Autonomous Agent Integration.

This version uses autonomous agents for processing instead of direct service calls.
Provides memory-aware, adaptive processing capabilities.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any
import asyncio

from autonomous_agents.orchestrator import orchestrator
from autonomous_agents.metrics import metrics, collector
from models.database import init_db
from utils.model_init import initialize_models

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autonomous Excel-PDF Values Validator", 
    version="2.0.0",
    description="AI-powered validation system with autonomous agent orchestration and memory management"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and models on startup"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Initialize and warm up models
        model_init_success = initialize_models()
        if model_init_success:
            logger.info("Models initialized successfully")
        else:
            logger.warning("Model initialization failed, but continuing...")
        
        logger.info("Autonomous agent system started successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't fail startup, just log the error


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Autonomous Excel-PDF Values Validator API", 
        "version": "2.0.0",
        "features": ["autonomous_agents", "memory_management", "adaptive_processing"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with autonomous agent status"""
    try:
        system_status = orchestrator.get_system_status()
        return {
            "status": "healthy",
            "message": "Autonomous agent system is operational",
            "system_status": system_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"System error: {e}"
            }
        )


@app.get("/system-status")
async def get_system_status():
    """Get detailed system status including memory and agent information"""
    try:
        return orchestrator.get_system_status()
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system status: {e}")


@app.get("/memory-stats")
async def get_memory_stats():
    """Get current memory usage statistics"""
    try:
        stats = orchestrator.memory_manager.get_current_stats()
        strategy = orchestrator.memory_manager.suggest_consolidation_strategy()
        
        return {
            "memory_stats": {
                "total_gb": stats.total_gb,
                "available_gb": stats.available_gb,
                "used_percent": stats.used_percent,
                "threshold_level": stats.threshold_level.name,
                "can_spawn_agents": stats.can_spawn_agents,
                "recommended_agent_count": stats.recommended_agent_count
            },
            "consolidation_strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting memory stats: {e}")


@app.post("/validate-autonomous")
async def validate_values_autonomous(
    pdf_file: UploadFile = File(...),
    excel_file: UploadFile = File(...)
):
    """
    Validate Excel values against PDF content using autonomous agents.
    
    This endpoint uses the autonomous agent orchestrator to determine
    the optimal processing strategy based on current memory availability.
    """
    try:
        logger.info(f"Autonomous validation request - PDF: {pdf_file.filename}, Excel: {excel_file.filename}")
        
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
            # Get initial system status
            initial_status = orchestrator.get_system_status()
            logger.info(f"Initial system status: Memory={initial_status['memory_stats']['available_gb']:.1f}GB, Threshold={initial_status['memory_stats']['threshold_level']}")
            
            # Process using autonomous agents
            result = orchestrator.process_validation_request(
                pdf_path=temp_pdf_path,
                excel_path=temp_excel_path,
                pdf_filename=pdf_file.filename,
                excel_filename=excel_file.filename
            )
            
            # Get final system status
            final_status = orchestrator.get_system_status()
            
            # Prepare response
            response = {
                "status": "success",
                "message": f"Validation completed using {result['execution_mode']} processing",
                "pdf_filename": pdf_file.filename,
                "excel_filename": excel_file.filename,
                "execution_mode": result["execution_mode"],
                "processing_results": result,
                "system_status": {
                    "initial": initial_status,
                    "final": final_status
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Autonomous validation completed successfully - Mode: {result['execution_mode']}")
            return response
            
        finally:
            # Clean up temporary files
            try:
                if os.path.exists(temp_pdf_path):
                    os.unlink(temp_pdf_path)
                if os.path.exists(temp_excel_path):
                    os.unlink(temp_excel_path)
            except Exception as cleanup_error:
                logger.warning(f"Error cleaning up temporary files: {cleanup_error}")
                
    except Exception as e:
        logger.error(f"Error in autonomous validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@app.post("/validate")
async def validate_values_legacy(
    pdf_file: UploadFile = File(...),
    excel_file: UploadFile = File(...)
):
    """
    Legacy validation endpoint that redirects to autonomous processing.
    Maintained for backward compatibility.
    """
    logger.info("Legacy validation endpoint called, redirecting to autonomous processing")
    return await validate_values_autonomous(pdf_file, excel_file)


@app.post("/create-embeddings-autonomous")
async def create_embeddings_autonomous(pdf_file: UploadFile = File(...)):
    """
    Create embeddings from PDF file using autonomous agents.
    Uses memory-aware processing strategy.
    """
    try:
        logger.info(f"Autonomous embedding creation for: {pdf_file.filename}")
        
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await pdf_file.read()
            temp_file.write(content)
            temp_pdf_path = temp_file.name
        
        try:
            # Get system status
            initial_status = orchestrator.get_system_status()
            
            # Use PDF intelligence agent for processing
            from autonomous_agents.intelligent_agents import pdf_intelligence_task
            
            pdf_task = pdf_intelligence_task.delay(temp_pdf_path, pdf_file.filename)
            result = pdf_task.get(timeout=300)
            
            # Create embeddings using the validation agent
            from autonomous_agents.intelligent_agents import validation_intelligence_task
            from services.embedding_service import EmbeddingService
            
            embedding_service = EmbeddingService()
            config_id = await embedding_service.create_embeddings(
                chunks=result['chunks'],
                filename=pdf_file.filename,
                pdf_path=temp_pdf_path
            )
            
            response = {
                "status": "success",
                "message": f"Successfully processed {result['chunk_count']} chunks from {pdf_file.filename}",
                "config_id": config_id,
                "chunks_processed": result['chunk_count'],
                "processor_type": result['processor_type'],
                "memory_usage_mb": result['memory_usage_mb'],
                "system_status": initial_status
            }
            
            logger.info(f"Autonomous embedding creation completed - Config ID: {config_id}")
            return response
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
                
    except Exception as e:
        logger.error(f"Error in autonomous embedding creation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/agent-telemetry")
async def get_agent_telemetry():
    """
    Get telemetry data from autonomous agents.
    """
    try:
        # This would typically read from a telemetry database
        # For now, return current system status
        return {
            "status": "success",
            "current_system_status": orchestrator.get_system_status(),
            "message": "Telemetry endpoint - implement detailed telemetry storage for production"
        }
    except Exception as e:
        logger.error(f"Error getting agent telemetry: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting telemetry: {e}")


@app.post("/force-consolidation")
async def force_consolidation():
    """
    Force agent consolidation for testing purposes.
    """
    try:
        strategy = orchestrator.memory_manager.suggest_consolidation_strategy()
        return {
            "status": "success",
            "message": "Consolidation strategy analysis completed",
            "strategy": strategy
        }
    except Exception as e:
        logger.error(f"Error in force consolidation: {e}")
        raise HTTPException(status_code=500, detail=f"Error in consolidation: {e}")


@app.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Prometheus metrics endpoint.
    Returns metrics in Prometheus format for scraping.
    """
    try:
        # Update metrics before returning
        metrics.update_system_metrics()
        
        # Get orchestrator metrics
        status = orchestrator.get_system_status()
        if 'memory_stats' in status:
            memory_stats = status['memory_stats']
            metrics.record_memory_threshold(memory_stats['threshold_level'])
        
        metrics.update_agent_metrics(orchestrator.active_tasks)
        
        # Return Prometheus format
        return metrics.get_metrics()
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return f"# Error getting metrics: {e}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
