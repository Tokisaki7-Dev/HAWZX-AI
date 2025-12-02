from fastapi import APIRouter

router = APIRouter(
    prefix="/vision",
    tags=["Vision"],
)

# TODO: Implementar endpoints de visão computacional.
# Exemplo:
# @router.post("/perceive")
# async def perceive_image():
#     return {"message": "Endpoint de percepção de imagem a ser implementado"}