# 🚀 HAWZX-AI - Guia de Assinatura e Setup

## 📋 LINKS DIRETOS - Cadastre-se AGORA

### ✅ 1. GOOGLE CLOUD (PRINCIPAL - GRÁTIS POR 90 DIAS)

**Link:** https://console.cloud.google.com/freetrial

**Plano:** Free Trial
- 💰 **$300 em créditos GRÁTIS**
- ⏰ Válido por 90 dias
- 💳 Precisa cadastrar cartão (mas NÃO será cobrado)
- ✅ Acesso a TODOS os serviços

**Passo a passo:**
1. Acesse o link acima
2. Clique em "Começar gratuitamente"
3. Faça login com sua conta Google
4. Adicione dados do cartão (não será cobrado no trial)
5. Ative o trial ($300 grátis)

**Depois dos 90 dias:**
- Você escolhe se quer continuar
- Passa a pagar apenas o que usar
- Custo estimado: $15-30/mês

---

### ✅ 2. GOOGLE AI STUDIO (GEMINI GRÁTIS - SEM CARTÃO)

**Link:** https://makersuite.google.com/app/apikey

**Plano:** Free (para sempre)
- 💰 **GRÁTIS** permanentemente
- 🚀 60 requisições por minuto
- 🎯 Gemini Pro API
- ❌ NÃO precisa cartão
- ✅ Suficiente para começar

**Passo a passo:**
1. Acesse o link
2. Faça login com Google
3. Clique em "Get API Key"
4. Copie a chave
5. Cole no seu arquivo .env

---

### ✅ 3. GITHUB (GRÁTIS)

**Link:** https://github.com/signup

**Plano:** Free
- 💰 **GRÁTIS** para sempre
- 📦 Repositórios ilimitados (públicos e privados)
- 🔄 GitHub Actions: 2,000 minutos/mês
- 📄 GitHub Pages para site

**Passo a passo:**
1. Acesse o link
2. Cadastre-se (email, senha)
3. Verifique email
4. Pronto!

**Upgrade futuro (opcional):**
- GitHub Pro: $4/mês (só quando crescer)

---

### ✅ 4. GROQ CLOUD (LLM GRÁTIS - ULTRA RÁPIDO)

**Link:** https://console.groq.com

**Plano:** Free
- 💰 **GRÁTIS** 
- 🚀 LLaMA 3 (70B)
- ⚡ Mais rápido que GPT-4
- 🎯 30 requisições/minuto grátis
- ❌ NÃO precisa cartão

**Passo a passo:**
1. Acesse o link
2. Sign up com Google/GitHub
3. Vá em API Keys
4. Crie uma nova key
5. Copie e guarde

---

### ✅ 5. RAILWAY (HOSPEDAGEM GRÁTIS)

**Link:** https://railway.app

**Plano:** Trial ($5 grátis/mês)
- 💰 **$5 grátis** por mês
- 🔄 Renova todo mês
- ❌ NÃO precisa cartão inicialmente
- 🚀 Deploy automático do GitHub

**Passo a passo:**
1. Acesse o link
2. Sign up com GitHub
3. Conecte seu repositório
4. Deploy automático!

**Upgrade futuro:**
- Hobby Plan: $5/mês quando acabar trial
- Pro: $20/mês quando crescer

---

## 🎯 OPCIONAL (Só quando crescer)

### 6. SUPABASE (Database Grátis)

**Link:** https://supabase.com/dashboard

**Plano:** Free
- 💰 GRÁTIS
- 💾 500MB database
- 👥 50,000 usuários
- 🔐 Auth incluso

---

### 7. CLOUDFLARE (CDN Grátis)

**Link:** https://dash.cloudflare.com/sign-up

**Plano:** Free
- 💰 GRÁTIS para sempre
- 🌐 CDN global
- 🛡️ DDoS protection básico
- 📊 Analytics

---

### 8. VERCEL (Frontend Grátis)

**Link:** https://vercel.com/signup

**Plano:** Hobby (Free)
- 💰 GRÁTIS
- ⚡ 100GB bandwidth
- 🚀 Deploy automático
- 🌐 Domínio .vercel.app

---

## 💰 RESUMO DE CUSTOS

### Fase 1: Primeiros 3 meses (GRÁTIS)

| Serviço | Plano | Custo |
|---------|-------|-------|
| Google Cloud | Trial | $0 (usando créditos) |
| Google AI Studio | Free | $0 |
| GitHub | Free | $0 |
| Groq Cloud | Free | $0 |
| Railway | Trial | $0 |
| Supabase | Free | $0 |
| Cloudflare | Free | $0 |
| **TOTAL** | | **$0/mês** |

### Fase 2: Meses 4-6 (Pagando)

| Serviço | Plano | Custo |
|---------|-------|-------|
| Google Cloud | Pay as you go | $15-25/mês |
| Railway | Hobby | $5/mês |
| Outros | Free | $0 |
| **TOTAL** | | **$20-30/mês** |

### Fase 3: Crescimento (1000+ usuários)

| Serviço | Plano | Custo |
|---------|-------|-------|
| Google Cloud | Standard | $100-200/mês |
| Railway/Cloud Run | Pro | $20-50/mês |
| Supabase | Pro | $25/mês |
| **TOTAL** | | **$145-275/mês** |

---

## 🔥 CHECKLIST DE SETUP (30 MINUTOS)

### ✅ Passo 1: Criar todas as contas (10 min)

```
□ Google Cloud - https://console.cloud.google.com/freetrial
□ Google AI Studio - https://makersuite.google.com/app/apikey
□ GitHub - https://github.com/signup
□ Groq Cloud - https://console.groq.com
□ Railway - https://railway.app
```

### ✅ Passo 2: Pegar as API Keys (10 min)

Depois de criar as contas, copie as chaves:

```env
# Google AI Studio
GOOGLE_AI_API_KEY=AIza...seu-codigo-aqui

# Groq
GROQ_API_KEY=gsk_...seu-codigo-aqui

# Google Cloud (após setup)
GOOGLE_APPLICATION_CREDENTIALS=caminho/para/credentials.json
```

### ✅ Passo 3: Configure o projeto (10 min)

```bash
# Clone ou crie o projeto
cd HAWZX-AI

# Crie arquivo .env
echo "GOOGLE_AI_API_KEY=sua-key-aqui" > .env
echo "GROQ_API_KEY=sua-key-aqui" >> .env

# Instale dependências
pip install -r requirements.txt
npm install

# Teste local
python main.py
```

---

## 🎓 ORDEM DE CADASTRO RECOMENDADA

### 1️⃣ PRIMEIRO (Essenciais - Agora)
1. **GitHub** (5 min) - Para versionar código
2. **Google AI Studio** (5 min) - Para IA grátis
3. **Groq** (5 min) - Backup LLM grátis

### 2️⃣ DEPOIS (Importantes - Hoje)
4. **Railway** (10 min) - Para hospedar
5. **Cloudflare** (5 min) - Para CDN

### 3️⃣ QUANDO FOR ESCALAR (Futuro)
6. **Google Cloud** (15 min) - Quando crescer
7. **Supabase** (5 min) - Se precisar database robusto

---

## ⚠️ IMPORTANTE: NÃO ASSINE

### ❌ NÃO assine estes (caro demais):

- **Azure** - Muito caro ($70-120/mês vs $15-30 GCP)
- **AWS** - Complexo e caro
- **OpenAI API** - $20/1M tokens (Groq é grátis)
- **Hostinger/Hostgator** - Não serve para IA
- **DigitalOcean** - Bom, mas mais caro que Railway

---

## 🎯 RESPOSTA DIRETA - ASSINE ESTES 5:

### HOJE (Grátis):
1. ✅ **GitHub Free** → https://github.com/signup
2. ✅ **Google AI Studio** → https://makersuite.google.com/app/apikey
3. ✅ **Groq Cloud** → https://console.groq.com
4. ✅ **Railway Trial** → https://railway.app
5. ✅ **Cloudflare Free** → https://dash.cloudflare.com/sign-up

### Em 3 meses (quando acabar créditos):
6. ✅ **Google Cloud Pay-as-go** ($20-30/mês)

**CUSTO TOTAL NOS PRIMEIROS 3 MESES: $0**
**CUSTO DEPOIS: $20-30/mês**

---

## 📱 LINKS RÁPIDOS - COPIE E COLE

```
GitHub: https://github.com/signup
Google AI: https://makersuite.google.com/app/apikey
Groq: https://console.groq.com
Railway: https://railway.app
Cloudflare: https://dash.cloudflare.com/sign-up
Google Cloud: https://console.cloud.google.com/freetrial
Supabase: https://supabase.com/dashboard
Vercel: https://vercel.com/signup
```

---

## 🚀 DEPOIS DO CADASTRO - PRÓXIMOS PASSOS

### 1. Instale ferramentas necessárias:

```bash
# Git
winget install Git.Git

# Python 3.11
winget install Python.Python.3.11

# Node.js
winget install OpenJS.NodeJS

# VS Code
winget install Microsoft.VisualStudioCode
```

### 2. Clone o projeto:

```bash
git clone https://github.com/seu-usuario/HAWZX-AI
cd HAWZX-AI
```

### 3. Configure as chaves:

```bash
# Crie .env
copy .env.example .env

# Edite e adicione suas keys
notepad .env
```

### 4. Rode local:

```bash
# Backend
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

### 5. Deploy no Railway:

```bash
# Conecte GitHub ao Railway
# Push para main
git add .
git commit -m "Initial commit"
git push

# Railway faz deploy automático!
```

---

## 💡 DICAS IMPORTANTES

### ✅ FAÇA:
- Use Google AI Studio para começar (grátis)
- Aproveite os $300 do Google Cloud
- Comece no Railway (grátis)
- Use Cloudflare para CDN (grátis)

### ❌ NÃO FAÇA:
- NÃO assine Azure (muito caro)
- NÃO use OpenAI API direta (caro)
- NÃO pague hospedagem tradicional
- NÃO contrate servidor dedicado ainda

---

## 🎁 BÔNUS: Ferramentas de Desenvolvimento Grátis

| Ferramenta | Link | Uso |
|-----------|------|-----|
| VS Code | https://code.visualstudio.com | Editor |
| Postman | https://postman.com | Testar APIs |
| Discord | https://discord.com | Comunidade |
| Figma | https://figma.com | Design |
| MongoDB Compass | https://mongodb.com/compass | Database GUI |

---

## 📞 PRECISA DE AJUDA?

Siga este checklist na ordem:

1. ✅ Criar GitHub
2. ✅ Criar Google AI Studio (pegar API key)
3. ✅ Criar Groq (pegar API key)
4. ✅ Criar Railway
5. ✅ Copiar API keys para .env
6. ✅ Rodar projeto local
7. ✅ Push para GitHub
8. ✅ Railway faz deploy automático

**Tempo total: 30-45 minutos**
**Custo: $0 nos primeiros 3 meses**

---

## 🏁 COMEÇE AGORA!

**Abra estas 5 abas no navegador AGORA:**

1. https://github.com/signup
2. https://makersuite.google.com/app/apikey
3. https://console.groq.com
4. https://railway.app
5. https://dash.cloudflare.com/sign-up

**Tempo para criar todas: 25 minutos**
**Custo: $0**

**Boa sorte! 🎮🚀**

---

*Última atualização: Dezembro 2024*
