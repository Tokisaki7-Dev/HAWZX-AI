# backend/main.py
import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
from io import BytesIO
from supabase import create_client, Client
from datetime import datetime

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = None

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase conectado!")
else:
    print("⚠️ Supabase não configurado - funcionando sem banco de dados")

app = FastAPI()

# Configuração do CORS
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://*.github.io",
    "https://*.vercel.app",
    "https://*.netlify.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios exatos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"message": "Servidor do Jogo de IA está rodando!"}

@app.post("/generate-frame")
async def generate_frame_endpoint(prompt_data: Prompt):
    api_key = os.getenv("STABILITY_API_KEY")
    prompt = prompt_data.prompt

    if not api_key or api_key == "YOUR_API_KEY":
        print("AVISO: STABILITY_API_KEY não configurada. Usando imagem de placeholder.")
        return {
            "message": "API Key não configurada, usando placeholder.",
            "image_url": "https://via.placeholder.com/800x600.png?text=Configure+sua+API+Key+no+.env"
        }

    engine_id = "stable-diffusion-v1-6"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        image_b64 = data["artifacts"][0]["base64"]
        image_data = f"data:image/png;base64,{image_b64}"
        
        # Salvar no Supabase (se configurado)
        if supabase:
            try:
                supabase.table("generations").insert({
                    "prompt": prompt,
                    "image_base64": image_b64,
                    "created_at": datetime.utcnow().isoformat()
                }).execute()
                print("✅ Geração salva no Supabase")
            except Exception as e:
                print(f"⚠️ Erro ao salvar no Supabase: {e}")
        
        return {
            "message": "Frame gerado com sucesso!",
            "image_url": image_data
        }

    except requests.exceptions.RequestException as e:
        print(f"Erro ao chamar a API da Stability AI: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na comunicação com a API de geração de imagem: {e}")
    except (KeyError, IndexError) as e:
        print(f"Erro ao processar a resposta da API: {e}")
        raise HTTPException(status_code=500, detail="Formato de resposta inesperado da API de geração de imagem.")

# Para rodar o servidor:
# 1. Navegue até a pasta 'backend' no terminal
# 2. Instale as dependências: pip install -r requirements.txt
# 3. Rode o servidor: uvicorn main:app --reload
