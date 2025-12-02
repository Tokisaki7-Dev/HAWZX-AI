from fastapi import APIRouter

router = APIRouter(
    tags=["Monitoring"],
)

@router.get("/health", summary="Verifica a saúde da API")
def health():
    """
    Endpoint de health check. Retorna o status da aplicação.
    """
    return {"status": "ok"}