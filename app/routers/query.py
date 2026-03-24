from fastapi import APIRouter, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from app.services.retrieval import answer_question
from app.models.schemas import QueryRequest, QueryResponse, SourceChunk
from app.core.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@router.post('/query', response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    api_key: str = Security(verify_api_key)
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        result = answer_question(request.question, request.document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed {str(e)}")
    
    return QueryResponse(
        question=request.question,
        answer=result["answer"],
        sources=[SourceChunk(**s) for s in result["sources"]]
    )