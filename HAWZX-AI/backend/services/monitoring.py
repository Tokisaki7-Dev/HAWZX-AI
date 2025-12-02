from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health", response_model=Dict[str, str], tags=["Monitoring"], summary="Verifica a saúde da API")
async def health_check():
    """Verifica se a API está online e respondendo."""
    return {"status": "ok"}