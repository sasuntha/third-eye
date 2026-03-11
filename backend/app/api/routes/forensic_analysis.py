"""
Forensic Analysis API Routes
Provides endpoints for complete forensic blood pattern analysis
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import logging
from datetime import datetime
from pathlib import Path

from forensic_orchestrator import ForensicAnalysisOrchestrator
from pdf_report_generator import ForensicPDFReportGenerator

router = APIRouter(prefix="/api/forensic-analysis", tags=["Forensic Analysis"])
logger = logging.getLogger(__name__)

# Initialize orchestrator and PDF generator
# Model path - looks for model in backend/models directory
# Get the backend directory (3 levels up from this file)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(BACKEND_DIR, 'models', 'my_weapon_model_v2.h5')

try:
    orchestrator = ForensicAnalysisOrchestrator(weapon_model_path=MODEL_PATH)
    pdf_generator = ForensicPDFReportGenerator()
    logger.info("Forensic analysis system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize forensic analysis system: {str(e)}")
    orchestrator = None
    pdf_generator = None


@router.post("/analyze")
async def analyze_blood_pattern(
    file: UploadFile = File(..., description="Blood pattern image to analyze"),
    confidence_threshold: float = 65.0
):
    """
    Complete forensic analysis of blood pattern image.
    
    Pipeline:
    1. Resizes image to 512x512
    2. Runs blood detection (must pass threshold to continue)
    3. If blood detected: runs weapon classification
    4. If blood detected: runs string method analysis
    5. Returns comprehensive JSON results
    
    Args:
        file: Image file upload
        confidence_threshold: Minimum blood detection confidence to proceed (default: 65%)
        
    Returns:
        JSON with complete analysis results
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=500,
            detail="Forensic analysis system not initialized. Please check model configuration."
        )
    
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (jpeg, png, etc.)"
            )
        
        # Read image data
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        logger.info(f"Analyzing image: {file.filename}, size: {len(image_data)} bytes")
        
        # Run complete analysis
        result = orchestrator.analyze(
            image_bytes=image_data,
            confidence_threshold=confidence_threshold,
            generate_plots=True
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forensic analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze-and-report")
async def analyze_and_generate_report(
    file: UploadFile = File(..., description="Blood pattern image to analyze"),
    confidence_threshold: float = 65.0
):
    """
    Complete forensic analysis with PDF report generation.
    
    This endpoint:
    1. Runs complete forensic analysis
    2. Generates PDF report in memory
    3. Returns JSON results with base64-encoded PDF
    
    Args:
        file: Image file upload
        confidence_threshold: Minimum blood detection confidence (default: 65%)
        
    Returns:
        JSON with analysis results and base64-encoded PDF
    """
    if orchestrator is None or pdf_generator is None:
        raise HTTPException(
            status_code=500,
            detail="Forensic analysis system not initialized"
        )
    
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read image
        image_data = await file.read()
        
        logger.info(f"Analyzing and generating report for: {file.filename}")
        
        # Run analysis
        result = orchestrator.analyze(
            image_bytes=image_data,
            confidence_threshold=confidence_threshold,
            generate_plots=True
        )
        
        # Generate PDF report in memory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"forensic_report_{timestamp}.pdf"
        pdf_path = os.path.join("reports", pdf_filename)
        
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        pdf_generator.generate_pdf(result, pdf_path)
        
        # Read the PDF file and encode as base64
        import base64
        with open(pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Add PDF info to result
        result['pdf_report'] = {
            'filename': pdf_filename,
            'pdf_base64': pdf_base64,
            'size_bytes': len(pdf_bytes)
        }
        
        logger.info(f"Report generated: {pdf_path} ({len(pdf_bytes)} bytes)")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analysis and report generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/download-report/{filename}")
async def download_report(filename: str):
    """
    Download generated PDF report
    
    Args:
        filename: PDF report filename
        
    Returns:
        PDF file download
    """
    pdf_path = os.path.join("reports", filename)
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )
    
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy" if orchestrator is not None else "unhealthy",
        "orchestrator_loaded": orchestrator is not None,
        "pdf_generator_loaded": pdf_generator is not None,
        "model_path": MODEL_PATH,
        "model_exists": os.path.exists(MODEL_PATH)
    }
    
    if not status["model_exists"]:
        status["message"] = f"Model not found at {MODEL_PATH}. Please add weapon_classifier.h5 to backend/models/"
    
    return status


@router.get("/")
async def forensic_analysis_info():
    """Get information about forensic analysis capabilities"""
    return {
        "service": "Forensic Blood Pattern Analysis",
        "version": "1.0.0",
        "capabilities": {
            "blood_detection": "Detect and verify blood presence",
            "weapon_classification": "Classify weapon type (Gun vs Melee)",
            "origin_analysis": "Calculate point of origin using string method"
        },
        "endpoints": {
            "analyze": "POST /api/forensic-analysis/analyze - Run complete analysis",
            "analyze_and_report": "POST /api/forensic-analysis/analyze-and-report - Analysis + PDF report",
            "download_report": "GET /api/forensic-analysis/download-report/{filename} - Download PDF",
            "health": "GET /api/forensic-analysis/health - Check system status"
        },
        "requirements": {
            "image_format": "JPEG, PNG, BMP",
            "image_processing": "Auto-resized to 512x512 pixels",
            "blood_threshold": "65% confidence required to proceed"
        }
    }
