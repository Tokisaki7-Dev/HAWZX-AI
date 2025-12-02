from fastapi import APIRouter

router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

# TODO: Implementar endpoints de RAG (Retrieval-Augmented Generation).
# Exemplo:
# @router.post("/query")
# async def query_rag():
#     return {"message": "Endpoint de RAG query a ser implementado"}