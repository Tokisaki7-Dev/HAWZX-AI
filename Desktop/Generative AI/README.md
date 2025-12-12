# 🎮 Noki AI - Game IA Generativo

Um jogo de aventura infinita com mundo gerado proceduralmente usando IA generativa.

## 📋 Estrutura do Projeto

```
noki-ai/
├── index.html              # Frontend do jogo
├── script.js              # Game engine (Canvas, Physics, Chunks)
├── style.css              # Estilos do jogo
├── backend/
│   ├── main.py            # FastAPI backend
│   ├── requirements.txt    # Dependências Python
│   └── .env              # Variáveis de ambiente
├── docker-compose.yml     # Setup local com Docker
├── Dockerfile             # Imagem Docker
├── fly.toml              # Configuração Fly.io
├── DEPLOY.md             # Guias de deployment
└── PLANO_PROJETO.md      # Planejamento técnico

```

## 🚀 Início Rápido

### Desenvolvimento Local

#### Pré-requisitos
- Python 3.11+
- Node.js (opcional, para servidor HTTP)

#### Setup

1. **Clone o repositório**
```bash
git clone https://github.com/Tokisaki7-Dev/noki-ai.git
cd noki-ai
```

2. **Ambiente Python**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Instale dependências**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

4. **Configure variáveis de ambiente**
```bash
cp backend/.env.example backend/.env
# Edite backend/.env com suas chaves
```

5. **Inicie o backend**
```bash
cd backend
uvicorn main:app --reload
```

6. **Inicie o frontend**
```bash
# Em outro terminal
python -m http.server 5500
```

7. **Acesse** `http://localhost:5500`

### Com Docker

```bash
docker-compose up -d
```

Acesse `http://localhost:5500` para o frontend e `http://localhost:8000` para o backend.

## 🌍 Tecnologias

### Frontend
- **HTML5 Canvas**: Renderização do jogo
- **JavaScript**: Game engine, física, input handling
- **CSS3**: UI e estilos

### Backend
- **FastAPI**: API REST
- **Supabase**: Database PostgreSQL
- **Python Imaging**: Processamento de imagens
- **Stability AI**: Geração de imagens

### Hospedagem
- **Fly.io**: Deployment recomendado
- **Railway**, **Render**, **Oracle Cloud**: Alternativas

## 🎯 Features

- ✅ Mundo infinito com chunks de 800px
- ✅ Biomas procedurais (Forest, Desert, Mountain, Cave)
- ✅ Sistema de física e colisão
- ✅ Geração de imagens por IA
- ✅ Banco de dados Supabase
- ✅ API REST FastAPI
- ✅ Containerização Docker
- ✅ Multi-platform deployment

## 📚 Documentação

- **[DEPLOY.md](./DEPLOY.md)**: Guias de deployment (Fly.io, Railway, Render, Oracle, Docker)
- **[PLANO_PROJETO.md](./PLANO_PROJETO.md)**: Planejamento técnico e roadmap
- **[script.js](./script.js)**: Game engine com comentários
- **[backend/main.py](./backend/main.py)**: API com documentação

## 🔑 Variáveis de Ambiente

```
STABILITY_API_KEY=seu_stability_key
SUPABASE_URL=sua_supabase_url
SUPABASE_KEY=sua_supabase_key
```

## 🚢 Deploy

Veja [DEPLOY.md](./DEPLOY.md) para instruções completas:

1. **Fly.io** (Recomendado): `flyctl deploy`
2. **Railway**: Interface web
3. **Render**: Interface web
4. **Oracle Cloud**: SSH + systemd
5. **Docker**: Qualquer VPS

## 🐛 Troubleshooting

### Backend não conecta ao Supabase
- Verifique `SUPABASE_URL` e `SUPABASE_KEY` em `.env`
- Verifique conectividade de rede
- Veja logs: `docker logs noki-ai-backend`

### Frontend não carrega imagens
- Verifique URL do backend em `script.js`
- Verifique CORS: `backend/main.py` line ~20
- Verifique `STABILITY_API_KEY`

### Docker não inicia
```bash
docker-compose down
docker-compose up -d --build
```

## 📞 Suporte

- 📖 [Documentação Fly.io](https://fly.io/docs/)
- 📖 [Documentação FastAPI](https://fastapi.tiangolo.com/)
- 📖 [Documentação Supabase](https://supabase.com/docs)

## 📄 Licença

MIT - Veja LICENSE para detalhes

---

**Status**: Em desenvolvimento 🚧
**Última atualização**: Dezembro 2025
