from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel # Import BaseModel
import uvicorn
import json
import os

# Importar serviços
from backend.services.ai_service import AIService
from backend.services.rag_service import RAGService
from backend.services.vision_service import VisionService
from backend.services.voice_service import VoiceService
from backend.game_service import GameService # Import GameService

app = FastAPI()

# Pydantic model for thinking model configuration
class ThinkingModelConfig(BaseModel):
    thinking_model_name: str
    thinking_api_key: str = None
    thinking_endpoint: str = None

# Pydantic model for loading game strategy
class GameStrategyLoadRequest(BaseModel):
    game_name: str
    stage: int = 1 # Default stage to 1

# Configuração para servir arquivos estáticos do frontend
# Assumindo que o frontend está na pasta HAWZX-AI/frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)
    # Create a dummy index.html if it doesn't exist
    with open(os.path.join(frontend_dir, "index.html"), "w") as f:
        f.write("<!DOCTYPE html><html><head><title>HAWZX AI Frontend</title></head><body><h1>HAWZX AI Frontend Placeholder</h1></body></html>")

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

templates = Jinja2Templates(directory=frontend_dir)


# Instanciação dos serviços
rag_service_instance = RAGService()
vision_service_instance = VisionService()
voice_service_instance = VoiceService()
game_service_instance = GameService() # Instantiate GameService
ai_service_instance = AIService(rag_service_instance, game_service_instance) # Pass GameService to AIService

# Carregar base de conhecimento do RAG (exemplo)
rag_service_instance.load_knowledge_base(["info sobre o jogo A", "dicas para o jogo B", "história do personagem X"])

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_ai(message: dict):
    user_text = message.get("text")
    if not user_text:
        return {"error": "No text provided"}
    
    response = ai_service_instance.process_query(user_text)
    voice_service_instance.speak(response["text"], response["emotion"])
    return {"response": response["text"]}

@app.post("/update_thinking_config")
async def update_thinking_config(config: ThinkingModelConfig):
    ai_service_instance.update_thinking_model_config(
        model_name=config.thinking_model_name,
        api_key=config.thinking_api_key,
        endpoint=config.thinking_endpoint
    )
    return {"message": "Thinking model configuration updated successfully."}

@app.post("/load_game_strategy")
async def load_game_strategy(request: GameStrategyLoadRequest):
    game_service_instance.load_game_strategy(request.game_name, request.stage)
    return {"message": f"Game strategy for {request.game_name} (stage {request.stage}) loaded successfully."}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Exemplo de processamento do loop principal
            message = json.loads(data)
            
            if message.get("type") == "screen_capture":
                # Quando o frontend envia dados de captura de tela
                # vision_result = vision_service_instance.analyze_screen(message.get("image_data")) # Adapte conforme o formato do image_data
                vision_result = vision_service_instance.analyze_screen() # Usando o método que captura internamente
                ai_service_instance.update_context(vision_data=vision_result)
                
                # Por enquanto, enviamos apenas uma confirmação ou dados simplificados de volta
                await websocket.send_text(json.dumps({"type": "vision_update", "game": vision_result.get("game"), "objects_count": len(vision_result.get("objects", []))}))
            
            elif message.get("type") == "chat_message":
                user_text = message.get("text")
                if user_text:
                    ai_service_instance.update_context(voice_text=user_text)
                    ai_response = ai_service_instance.process_query(user_text)
                    voice_service_instance.speak(ai_response["text"], ai_response["emotion"])
                    await websocket.send_text(json.dumps({"type": "ai_response", "text": ai_response["text"], "emotion": ai_response["emotion"]}))
            else:
                await websocket.send_text(f"Received unknown message type: {message.get('type')}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket.close()

# Para rodar localmente (apenas para desenvolvimento, em produção use uvicorn diretamente)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
