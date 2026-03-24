from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    pages: int
    chunks_stored: int

class QueryRequest(BaseModel):
    query: str
    document_id: Optional[str] = None

class SourceChunk(BaseModel):
    content: str
    page: int
    document_id: str
    filename: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceChunk]