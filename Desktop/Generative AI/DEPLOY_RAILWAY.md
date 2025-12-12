# Deploy Noki AI Backend no Railway

## 🚀 Passos Rápidos

### 1. Criar conta no Railway
- Acesse: https://railway.app
- Login com GitHub

### 2. Novo Projeto
1. Dashboard → **New Project**
2. Selecione **Deploy from GitHub repo**
3. Conecte **Tokisaki7-Dev/noki-ai**

### 3. Configurar Variáveis de Ambiente
1. No Railway dashboard, vá em **Variables**
2. Adicione as seguintes variáveis:

```
STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow
SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co
SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl
```

### 4. Configurar Serviço
1. Railway detectará automaticamente o Python project
2. Define:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Deploy
1. Clique em **Deploy**
2. Aguarde 2-3 minutos
3. Railway gerará uma URL automaticamente

### 6. Encontrar a URL do Serviço
1. Dashboard → seu projeto
2. **Deployments** → clique no serviço
3. Copie o **Generated Domain** (ex: `https://noki-ai-backend-prod.up.railway.app`)

### 7. Atualizar Frontend
No arquivo `script.js`, substitua:
```javascript
apiEndpoint: 'http://127.0.0.1:8000'
```
Por:
```javascript
apiEndpoint: 'https://seu-dominio-railway.up.railway.app'
```

## 📋 Vantagens do Railway

✅ Grátis com crédito inicial ($5/mês)  
✅ Sem hibernação (sempre ativo)  
✅ Melhor UX que Render  
✅ Suporte a múltiplos serviços  
✅ Logs em tempo real  

## 🐛 Troubleshooting

**Erro 502 Bad Gateway:**
- Verifique os logs no Railway
- Confirme que `requirements.txt` tem todas as dependências

**CORS Error:**
- Backend já está configurado com `allow_origins=["*"]`
- Se precisar restringir depois, atualize `main.py`

**Serviço não inicia:**
- Verifique se `Procfile` e `requirements.txt` existem
- Logs devem mostrar o erro de startup

## 📝 Arquivo requirements.txt

Já está pronto em `backend/requirements.txt`:
```
fastapi
uvicorn[standard]
python-dotenv
requests
Pillow
supabase>=2.25.1
```

## 🔄 Auto Deploy

A cada push no GitHub (`main` branch), Railway redeploya automaticamente!
