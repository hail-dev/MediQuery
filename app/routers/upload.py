from fastapi import APIRouter, UploadFile, File, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.services.ingestion import ingest_document
from app.models.schemas import UploadResponse
from app.core.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@router.post('/upload', response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    api_key: str = Security(verify_api_key)
):
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    # Validate file size (10MB max)
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")
    
    try:
        result = ingest_document(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    return UploadResponse(
        message="Document uploaded and indexed successfully.",
        document_id=result["document_id"],
        filename=result["filename"],
        pages=result["pages"],
        chunks_stored=result["chunks_stored"]
    )