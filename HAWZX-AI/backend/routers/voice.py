from fastapi import APIRouter

router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

# TODO: Implementar endpoints de voz (ASR/TTS).
# Exemplo:
# @router.post("/asr")
# async def speech_to_text():
#     return {"message": "Endpoint de ASR a ser implementado"}