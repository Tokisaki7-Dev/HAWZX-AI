# Deploy Noki AI Backend no Oracle Cloud Free Tier

## 🎉 Por que Oracle Cloud?

✅ **Sempre grátis** (2 vCPU, 12GB RAM, 100GB storage)  
✅ **Melhor que Fly.io** (muito mais poder)  
✅ **Sem limitações de tráfego**  
✅ **Sempre 100% online** (sem hibernação)  
✅ **Ideal para produção**  

## 🚀 Passos de Configuração

### 1. Criar Conta Oracle Cloud
1. Acesse: https://www.oracle.com/cloud/free/
2. Clique em **Sign Up**
3. Preencha email, país (Brasil), etc
4. Escolha **Always Free** (padrão)
5. Valide com cartão de crédito (NÃO cobra, apenas verifica)
6. Aguarde confirmação por email (5-10 min)

### 2. Criar Instância (VM)

Na console Oracle:

1. **Menu** (≡) → **Compute** → **Instances**
2. **Create Instance**
3. Configurações:
   - **Name**: `noki-ai-backend`
   - **Image**: Ubuntu 22.04 (sempre disponível grátis)
   - **Shape**: Ampere (ARM) - **Selecione free-eligible**
   - **vCPU count**: 4 (máximo grátis)
   - **RAM**: 24GB (máximo grátis)
   - **Storage**: 200GB
4. **SSH Key Pair**: Gere nova
   - Baixe e guarde a chave privada (`.key`)
5. **Create**

### 3. Configurar Firewall

Na instância criada:

1. Vá em **Security** → **Subnet**
2. Clique em **Security List**
3. **Add Ingress Rule**:
   ```
   Stateless: No
   Source Type: CIDR
   Source CIDR: 0.0.0.0/0
   IP Protocol: TCP
   Destination Port Range: 80
   ```
4. Repita para porta **443**

### 4. Conectar via SSH

**Windows (PowerShell):**
```powershell
# Defina permissões da chave
icacls.exe $env:USERPROFILE\.ssh\id_rsa /grant:r "$env:USERNAME`:F"
icacls.exe $env:USERPROFILE\.ssh\id_rsa /inheritance:r

# Conecte
ssh -i "caminho/para/chave.key" ubuntu@seu-ip-publico
```

**macOS/Linux:**
```bash
chmod 600 sua-chave.key
ssh -i sua-chave.key ubuntu@seu-ip-publico
```

### 5. Setup do Backend na VM

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install -y python3 python3-pip python3-venv git

# Clonar repositório
git clone https://github.com/Tokisaki7-Dev/noki-ai.git
cd noki-ai/backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Testar localmente
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Setup Nginx como Reverse Proxy

```bash
# Instalar Nginx
sudo apt install -y nginx

# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/noki-ai
```

Colar:
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/noki-ai /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 7. Rodar Backend Permanentemente (Systemd)

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/noki-ai.service
```

Colar:
```ini
[Unit]
Description=Noki AI Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/noki-ai/backend
Environment="PATH=/home/ubuntu/noki-ai/backend/venv/bin"
ExecStart=/home/ubuntu/noki-ai/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl enable noki-ai.service
sudo systemctl start noki-ai.service
sudo systemctl status noki-ai.service
```

### 8. SSL/HTTPS com Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado (substitua seu-dominio.com)
sudo certbot certonly --nginx -d seu-dominio.com

# Nginx usa automaticamente
sudo systemctl restart nginx
```

### 9. Encontrar IP Público

Na console Oracle:
1. **Compute** → **Instances**
2. Clique na sua instância
3. Copie **Public IP Address** (ex: `123.45.67.89`)

### 10. Atualizar Frontend

No `script.js`:
```javascript
apiEndpoint: 'http://seu-ip-publico:8000'
// ou com domínio:
apiEndpoint: 'https://seu-dominio.com'
```

## 📋 Verificações

**Testar backend:**
```bash
curl http://seu-ip-publico:8000
# Deve retornar: {"message":"Servidor do Jogo de IA está rodando!"}
```

**Ver logs:**
```bash
sudo journalctl -u noki-ai.service -f
```

**Monitoramento:**
```bash
# Ver uso de recursos
top
# ou
htop
```

## 🔄 Atualizações

Quando fizer push no GitHub:
```bash
ssh -i sua-chave ubuntu@seu-ip
cd noki-ai
git pull origin main
# Se mudou requirements.txt:
cd backend && source venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart noki-ai.service
```

## 💰 Custo

**Totalmente grátis:**
- 2 vCPU ARM (ou 1 vCPU x86) sempre grátis
- 12GB RAM
- 100GB storage
- 10TB tráfego/mês

Noki AI usa ~10% desses recursos 🚀

## 🐛 Troubleshooting

**Conexão SSH recusada:**
```bash
# Verificar security list das regras
# Ter certeza que porta 22 está aberta
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
```

**Serviço não inicia:**
```bash
sudo systemctl status noki-ai.service
# Ver erros completos:
sudo journalctl -u noki-ai.service --no-pager
```

**Nginx retorna 502:**
```bash
sudo nginx -t
# Verificar se backend está rodando:
ps aux | grep uvicorn
```

**Recuperar IP se perdeu:**
```bash
# Na console Oracle, instância → Primary VNIC → Primary private IP address
```
