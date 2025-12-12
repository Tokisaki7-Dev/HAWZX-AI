#!/usr/bin/env python3
"""Deploy Noki AI to Google Cloud Run using Python SDK"""

import os
import sys
import subprocess
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path("backend/.env")
if env_file.exists():
    load_dotenv(env_file)

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0511757842")
SERVICE_NAME = "noki-ai-backend"
REGION = "us-central1"
IMAGE_NAME = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}"
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
GCLOUD_KEY = Path("backend/gcloud-key.json")

print("🚀 Noki AI Deploy (Python Version)")
print("=" * 50)

# 1. Check if gcloud-key.json exists
if not GCLOUD_KEY.exists():
    print(f"❌ Chave de serviço não encontrada: {GCLOUD_KEY}")
    print("Execute no Google Cloud Console:")
    print(f"  gcloud iam service-accounts keys create {GCLOUD_KEY}")
    print(f"  --iam-account=SERVICE_ACCOUNT_EMAIL@{PROJECT_ID}.iam.gserviceaccount.com")
    sys.exit(1)

print(f"✅ Chave de serviço encontrada: {GCLOUD_KEY}")

# 2. Authenticate
print("\n🔐 Autenticando no Google Cloud...")
auth_cmd = [
    "gcloud", "auth", "activate-service-account",
    f"--key-file={GCLOUD_KEY}"
]
result = subprocess.run(auth_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Erro na autenticação:\n{result.stderr}")
    sys.exit(1)
print("✅ Autenticação bem-sucedida")

# 3. Set project
print(f"\n📋 Configurando projeto: {PROJECT_ID}")
proj_cmd = ["gcloud", "config", "set", "project", PROJECT_ID]
result = subprocess.run(proj_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Erro ao configurar projeto:\n{result.stderr}")
    sys.exit(1)
print(f"✅ Projeto configurado: {PROJECT_ID}")

# 4. Build image with Cloud Build
print(f"\n🔨 Buildando imagem: {IMAGE_NAME}")
build_cmd = [
    "gcloud", "builds", "submit",
    f"--tag={IMAGE_NAME}",
    "--timeout=600"
]
result = subprocess.run(build_cmd, cwd="backend", capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Erro no build:\n{result.stderr}")
    sys.exit(1)
print(f"✅ Build concluído: {IMAGE_NAME}")

# 5. Deploy to Cloud Run
print(f"\n🚢 Deployando para Cloud Run: {SERVICE_NAME}")
deploy_cmd = [
    "gcloud", "run", "deploy", SERVICE_NAME,
    f"--image={IMAGE_NAME}",
    "--platform=managed",
    f"--region={REGION}",
    "--allow-unauthenticated",
    f"--set-env-vars=STABILITY_API_KEY={STABILITY_API_KEY}"
]
result = subprocess.run(deploy_cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"❌ Erro no deploy:\n{result.stderr}")
    sys.exit(1)

# Extract service URL
output = result.stdout
print(result.stdout)

# Try to extract the service URL
if "https://" in output:
    import re
    match = re.search(r'https://[^\s]+', output)
    if match:
        service_url = match.group(0)
        print(f"\n✅ Deploy bem-sucedido!")
        print(f"📍 URL do serviço: {service_url}")
        
        # Update script.js with new API endpoint
        script_js = Path("script.js")
        if script_js.exists():
            print(f"\n🔄 Atualizando script.js com novo endpoint...")
            content = script_js.read_text()
            updated = content.replace(
                'apiEndpoint = "http://localhost:8000"',
                f'apiEndpoint = "{service_url}"'
            )
            script_js.write_text(updated)
            print(f"✅ script.js atualizado com: {service_url}")
    else:
        print(f"\n⚠️ Deploy concluído, mas não consegui extrair a URL")
        print(f"Saída do deploy:\n{output}")
else:
    print(f"\n✅ Deploy concluído!")
    print(result.stdout)

print("\n" + "=" * 50)
print("🎉 Deploy finalizado com sucesso!")
