# 🚀 Guia de Deployment - Noki AI

Este guia consolida as opções de deployment disponíveis. Escolha uma plataforma abaixo.

## 📋 Comparação Rápida

| Plataforma | Custo | Hibernação | Setup | Suporte |
|-----------|-------|-----------|-------|---------|
| **Fly.io** | Gratuito | Não | Muito fácil | ⭐⭐⭐⭐⭐ |
| **Railway** | $5/mês free | Não | Fácil | ⭐⭐⭐⭐ |
| **Render** | Gratuito | 15 min | Fácil | ⭐⭐⭐ |
| **Oracle Cloud** | Gratuito (Always Free) | Não | Moderado | ⭐⭐⭐⭐ |

---

## 🎯 Opção 1: Fly.io (Recomendado)

### Vantagens
- Gratuitamente sem limite de tempo
- Sem hibernação
- Deploy em ~30 segundos
- Ótimo desempenho

### Setup

#### 1. Instalar CLI
**Windows (PowerShell Admin):**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

#### 2. Login
```bash
flyctl auth login
```

#### 3. Deploy
```bash
cd "C:\Users\endri\Desktop\Generative AI"
flyctl deploy
```

#### 4. Copiar URL
```bash
flyctl status
```
A URL será exibida como: `https://noki-ai-backend.fly.dev`

#### 5. Atualizar Frontend
Abra `script.js` e altere:
```javascript
// Mude isto:
const apiEndpoint = 'http://127.0.0.1:8000';

// Para:
const apiEndpoint = 'https://noki-ai-backend.fly.dev';
```

---

## 🚂 Opção 2: Railway

### Setup

#### 1. Criar Conta
- Acesse: https://railway.app
- Login com GitHub

#### 2. Novo Projeto
1. Dashboard → **New Project**
2. **Deploy from GitHub repo**
3. Selecione **Tokisaki7-Dev/noki-ai**

#### 3. Configurar Variáveis
Em **Variables**, adicione:
```
STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow
SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co
SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl
```

#### 4. Deploy
- Railway detecta automaticamente Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 5. Copiar URL
Dashboard → seu projeto → **Deployments** → **Generated Domain**

#### 6. Atualizar Frontend
```javascript
const apiEndpoint = 'https://seu-dominio-railway.up.railway.app';
```

---

## 🎨 Opção 3: Render

### Setup

#### 1. Criar Conta
- Acesse: https://render.com
- Login com GitHub

#### 2. Web Service
1. Dashboard → **New** → **Web Service**
2. Conecte: **Tokisaki7-Dev/noki-ai**

#### 3. Configurações
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 4. Variáveis de Ambiente
```
STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow
SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co
SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl
```

#### 5. Deploy
Clique em **Create Web Service** e aguarde 3-5 minutos.

#### 6. Atualizar Frontend
```javascript
const apiEndpoint = 'https://noki-ai-backend.onrender.com';
```

⚠️ **Aviso**: Render coloca projetos inativos em hibernação após 15 minutos.

---

## ☁️ Opção 4: Oracle Cloud Always Free

### Vantagens
- Sempre gratuito (verdadeiramente)
- 2 vCPU + 12GB RAM
- Sem limites de tempo
- Ótimo para longo prazo

### Setup

#### 1. Criar Conta
- Acesse: https://www.oracle.com/cloud/free/
- Crie conta com cartão (não será cobrado)

#### 2. Criar Instância Compute
1. Acesse **Compute → Instances**
2. **Create Instance**:
   - Image: Ubuntu 22.04
   - Shape: Ampere (Always Free eligible)
   - Network: Create new VCN

#### 3. SSH na Instância
```bash
ssh ubuntu@seu-ip-publico
```

#### 4. Instalar Dependências
```bash
sudo apt update && sudo apt install -y python3-pip git
cd ~
git clone https://github.com/Tokisaki7-Dev/noki-ai.git
cd noki-ai/backend
pip3 install -r requirements.txt
```

#### 5. Configurar Variáveis
```bash
cat > .env << EOF
STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow
SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co
SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl
EOF
```

#### 6. Usar systemd para Manter Ativo
```bash
sudo tee /etc/systemd/system/noki-ai.service > /dev/null <<EOF
[Unit]
Description=Noki AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/noki-ai/backend
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 80
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable noki-ai
sudo systemctl start noki-ai
```

#### 7. Abrir Firewall
```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save
```

#### 8. Atualizar Frontend
```javascript
const apiEndpoint = 'http://seu-ip-oracle-publico';
```

---

## 🐳 Opção 5: Docker Local

Para testar localmente antes de deployar:

```bash
cd "C:\Users\endri\Desktop\Generative AI"
docker build -t noki-ai-backend .
docker run -p 8000:8000 \
  -e STABILITY_API_KEY=AIzaSyCegsTQvSQrS4giNDV_19svmMJrdD6i_ow \
  -e SUPABASE_URL=https://qwsnxutkvwfubtcnavnt.supabase.co \
  -e SUPABASE_KEY=sb_secret_5f_W3QQAOT0Sqo39DkYXHQ_oKe1kWwl \
  noki-ai-backend
```

Backend rodará em `http://localhost:8000`

---

## ✅ Checklist Pós-Deploy

1. ✅ URL do backend foi gerada
2. ✅ Variáveis de ambiente configuradas
3. ✅ `script.js` atualizado com nova URL
4. ✅ Frontend commitado e pushado
5. ✅ Testar endpoint: `curl https://seu-backend/generate-frame`

---

## 🆘 Troubleshooting

### "Port already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Supabase connection error"
Verifique variáveis de ambiente e URLs no `.env`

---

## 📞 Suporte

- Documentação Fly.io: https://fly.io/docs/
- Documentação Railway: https://railway.app/docs
- Documentação Render: https://render.com/docs
- Documentação Oracle: https://docs.oracle.com/en-us/iaas/

---

**Última atualização**: Dezembro 2025
