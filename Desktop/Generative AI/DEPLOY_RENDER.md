# Deploy Noki AI Backend no Render

## Passos Rápidos

### 1. Criar conta no Render
- Acesse: https://render.com
- Faça login com GitHub

### 2. Push do código para GitHub (se ainda não fez)
```bash
cd "C:\Users\endri\Desktop\Generative AI"
git add .
git commit -m "Add Supabase integration and Render config"
git push origin main
```

### 3. Criar Web Service no Render
1. Dashboard → **New** → **Web Service**
2. Conectar repositório GitHub: **Tokisaki7-Dev/HAWZX-AI**
3. Configurações:
   - **Name**: `noki-ai-backend`
   - **Region**: `Oregon (US West)` ou mais próximo
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`

### 4. Adicionar Variáveis de Ambiente
No Render, vá em **Environment** e adicione:

```
STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow
SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co
SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl
```

### 5. Deploy
- Clique em **Create Web Service**
- Aguarde o build (3-5 minutos)
- Copie a URL gerada (ex: `https://noki-ai-backend.onrender.com`)

### 6. Atualizar Frontend
No arquivo `script.js`, substitua:
```javascript
apiEndpoint: 'http://127.0.0.1:8000'
```
Por:
```javascript
apiEndpoint: 'https://noki-ai-backend.onrender.com'
```

## Observações

- **CORS**: O backend já está configurado para aceitar requisições do frontend
- **Free Tier**: O serviço hiberna após 15 min sem uso (primeira requisição pode demorar)
- **Logs**: Render Dashboard → Logs para debug
- **Auto Deploy**: Cada push no GitHub redeploya automaticamente

## Troubleshooting

Se der erro 502:
- Verifique os logs no Render Dashboard
- Confirme que as variáveis de ambiente estão corretas
- O free tier pode levar até 1 minuto para acordar

Se CORS error:
- Adicione a URL do frontend nas origins permitidas em `main.py`
