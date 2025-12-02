from fastapi import APIRouter

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

# TODO: Implementar endpoints de IA, como chat, geração de texto, etc.
# Exemplo:
# @router.post("/chat/stream")
# async def chat_stream():
#     return {"message": "Endpoint de chat stream a ser implementado"}