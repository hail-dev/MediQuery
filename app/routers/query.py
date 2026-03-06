from fastapi import APIRouter

router = APIRouter()

@router.get("/query", tags=["Query"])
def query():
    return {"message": "Query endpoint."}