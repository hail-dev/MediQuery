from fastapi import APIRouter

router = APIRouter()

@router.get("/upload", tags=["Upload"])
def upload():
    return {"message": "Upload endpoint."}