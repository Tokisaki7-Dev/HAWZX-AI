from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

from ..rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG Service"])

# --- Modelos de Requisição (Pydantic) ---

class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="como derrotar boss Grimm fase 2")
    gameId: str = Field(..., example="Hollow-Knight-Silksong")
    top_k: int = Field(5, gt=0, le=20)

# --- Endpoints de RAG ---

@router.post("/query", response_model=Dict[str, Any], summary="Busca conhecimento contextual (RAG)")
async def query_knowledge(request: RAGQueryRequest):
    """
    Recebe uma pergunta e um contexto de jogo, e retorna uma resposta
    sintetizada com base em documentos de conhecimento relevantes.
    """
    try:
        result = rag_service.query(query_text=request.query, game_id=request.gameId, top_k=request.top_k)
        return result
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado durante a busca RAG: {e}")