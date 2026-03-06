from fastapi import FastAPI
from app.routers import upload, query

app = FastAPI(
    title="MediQuery",
    description="AI-powered Healthcare Document Q&A using RAG",
    version="1.0.0"
)

app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(query.router, prefix="/api/v1", tags=["Query"])

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "MediQuery API is running"}