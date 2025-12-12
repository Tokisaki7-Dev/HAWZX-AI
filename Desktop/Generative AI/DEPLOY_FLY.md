# Deploy Noki AI Backend no Fly.io

## 🚀 Passos Rápidos

### 1. Instalar CLI do Fly.io
**Windows (PowerShell como Admin):**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

Verifique a instalação:
```bash
flyctl version
```

### 2. Login no Fly.io
```bash
flyctl auth login
```
- Abre no navegador para autenticar com GitHub
- Retorna ao terminal automaticamente

### 3. Deploy (Automático!)
Na raiz do projeto:
```bash
flyctl deploy
```

O Fly.io vai:
- Detectar `fly.toml` automaticamente
- Fazer build do Docker
- Deploy em segundos
- Gerar URL automaticamente

### 4. Verificar Status
```bash
flyctl status
```

Copie a URL gerada (ex: `https://noki-ai-backend.fly.dev`)

### 5. Atualizar Frontend
No `script.js`, substitua:
```javascript
apiEndpoint: 'http://127.0.0.1:8000'
```
Por:
```javascript
apiEndpoint: 'https://noki-ai-backend.fly.dev'
```

### 6. Fazer Commit
```bash
git add script.js
git commit -m "Update API endpoint to Fly.io"
git push noki main
```

## 📋 Explicação de fly.toml

- **app**: Nome da aplicação
- **primary_region**: `gru` (São Paulo, melhor latência para BR)
- **STABILITY_API_KEY, SUPABASE_***: Variáveis de ambiente
- **internal_port**: Porta onde FastAPI roda (8000)
- **processes**: Comando para iniciar o app

## ✅ Vantagens

✅ **Sempre grátis** (não hibernação)  
✅ **Deploy em 30 segundos**  
✅ **Auto-scale**  
✅ **Região Brasil** (baixa latência)  
✅ **CI/CD automático** (push → deploy)  
✅ **Melhor que Render/Railway grátis**  

## 🐛 Troubleshooting

**Erro: `command not found: flyctl`**
- Feche e abra um novo terminal
- Ou adicione ao PATH manualmente

**Build falha:**
```bash
flyctl logs --tail
```
Mostra os erros em tempo real

**Resetar app:**
```bash
flyctl apps destroy noki-ai-backend
flyctl deploy
```

**Subir variáveis depois:**
```bash
flyctl secrets set STABILITY_API_KEY=seu_valor
```

## 🔄 CI/CD Automático

Não precisa fazer nada! A cada push em `main`:
1. GitHub notifica Fly.io
2. Fly.io faz build e deploy
3. URL sempre funciona

## 📝 Custo

**Free Tier:**
- 3 shared-cpu-1x 256MB VMs
- 3GB persistent storage
- 160GB data transfer/mês
- **Totalmente grátis!**

Tudo que você precisa para Noki AI funcionar 🚀
