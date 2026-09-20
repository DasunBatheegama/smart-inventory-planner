from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def heath():
    return {
        "status": "healthy"
    }