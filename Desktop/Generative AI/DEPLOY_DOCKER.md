# Deploy Noki AI com Docker

## 🐳 O que é Docker?

Docker é um container - empacota todo o código, dependências e configurações em uma "caixa" que funciona em qualquer lugar.

## 🚀 Opção 1: Rodar Localmente com Docker

### Instalar Docker

**Windows:**
1. Baixe: https://www.docker.com/products/docker-desktop
2. Instale e reinicie

**Verificar instalação:**
```bash
docker --version
docker-compose --version
```

### Rodar localmente

```bash
cd "C:\Users\endri\Desktop\Generative AI"
docker-compose up --build
```

Pronto! Backend rodando em `http://localhost:8000`

**Parar:**
```bash
docker-compose down
```

---

## 🌍 Opção 2: Hospedar em Plataforma Docker

### **A) DigitalOcean (Melhor custo/benefício)**

1. Criar conta: https://www.digitalocean.com
2. **Create** → **Container Registry**
3. Gerar **Access Token**
4. Build e push:
```bash
# Login no Docker Hub (ou DigitalOcean)
docker login

# Build
docker build -t seu-usuario/noki-ai-backend .

# Push
docker push seu-usuario/noki-ai-backend

# Na console DigitalOcean, criar App:
# Conectar container do registry
# Definir portas, variáveis, etc
```

Custo: **$4-6/mês** para container Always On

### **B) Heroku + Docker**

```bash
# Login no Heroku
heroku login

# Criar app
heroku create noki-ai-backend

# Build e push para Heroku
heroku container:push web --app noki-ai-backend

# Deploy
heroku container:release web --app noki-ai-backend

# Verificar
heroku open --app noki-ai-backend
```

Custo: Grátis (tem limitações) ou $7/mês

### **C) AWS ECR + ECS**

```bash
# Criar repositório no AWS ECR
aws ecr create-repository --repository-name noki-ai-backend

# Build e push
docker build -t noki-ai-backend .
docker tag noki-ai-backend:latest [seu-aws-account].dkr.ecr.us-east-1.amazonaws.com/noki-ai-backend:latest
docker push [seu-aws-account].dkr.ecr.us-east-1.amazonaws.com/noki-ai-backend:latest

# Criar ECS Task + Service via console
```

Custo: **Free Tier** (12 meses) ou ~$10/mês

---

## 📊 Comparação de Plataformas Docker

| Plataforma | Custo | Vantage | Dificuldade |
|-----------|-------|---------|------------|
| **DigitalOcean** | $4-6/mês | Fácil, confiável | ⭐ |
| **Heroku** | Grátis/$7 | UI simples | ⭐ |
| **AWS ECR+ECS** | Free/~$10 | Poderoso | ⭐⭐⭐ |
| **Docker Hub** | Grátis | Apenas registry | ⭐ |
| **Fly.io** | Grátis | Fácil | ⭐ |

---

## 🔧 Arquivos Docker Criados

### `Dockerfile`
- Base: Python 3.11 slim
- Instala requirements.txt
- Roda: `uvicorn main:app`

### `docker-compose.yml`
- Define container, portas, variáveis de ambiente
- Fácil para desenvolvimento local

---

## 📝 Variáveis de Ambiente

No `docker-compose.yml`, atualize:
```yaml
environment:
  - STABILITY_API_KEY=seu_valor
  - SUPABASE_URL=seu_url
  - SUPABASE_KEY=sua_chave
```

Ou use arquivo `.env`:
```bash
docker-compose --env-file .env up
```

---

## 🐛 Troubleshooting Docker

**Erro: Docker daemon not running**
```bash
# Abra Docker Desktop
# Ou reinicie o serviço:
sudo systemctl restart docker
```

**Imagem muito grande?**
```bash
# Ver tamanho
docker images

# Limpar dangling images
docker image prune
```

**Container não inicia**
```bash
docker logs noki-ai-backend
```

**Redefinir tudo**
```bash
docker-compose down --volumes --rmi all
docker-compose up --build
```

---

## ✅ Próximas Ações

1. Instale Docker Desktop
2. Rode localmente: `docker-compose up`
3. Escolha plataforma (recomendo **DigitalOcean** ou **Fly.io**)
4. Faça push da imagem
5. Deploy!

Qual plataforma você quer usar com Docker?
