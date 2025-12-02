<#
.SYNOPSIS
    Inicia todos os serviços do HAWZX-AI (Backend e Frontend/Overlay).
.DESCRIPTION
    Este script orquestra a inicialização completa do ambiente de desenvolvimento.
    Ele inicia o servidor backend FastAPI em uma nova janela e, em seguida,
    instala as dependências do Node.js e inicia o aplicativo Electron em outra.
.EXAMPLE
    .\infra\run-all.ps1
    Executa o backend e o frontend a partir da raiz do projeto.
#>

Write-Host "--- Iniciando o Ecossistema Completo HAWZX-AI ---" -ForegroundColor Magenta

# Define o diretório raiz do projeto
$projectRoot = (Get-Item -Path (Join-Path $PSScriptRoot "..\")).FullName
Push-Location $projectRoot

# --- 1. Iniciar o Backend ---
Write-Host "Iniciando o Backend (FastAPI) em uma nova janela..." -ForegroundColor Cyan
$backendScript = Join-Path $projectRoot "infra\start-backend.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$backendScript'"

# --- 2. Iniciar o Frontend (Electron Overlay) ---
Write-Host "Verificando dependências do Frontend (Node.js)..." -ForegroundColor Cyan

# Verifica se o npm está instalado
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "NPM não encontrado. Por favor, instale o Node.js (https://nodejs.org/)."
    exit 1
}

Write-Host "Instalando dependências do Node.js (npm install)..."
npm install

Write-Host "Iniciando o Frontend (Electron) em uma nova janela..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start"

Pop-Location

Write-Host "--- Todos os serviços foram iniciados em janelas separadas. ---" -ForegroundColor Magenta
Write-Host "Para parar, feche as janelas do Backend e do Frontend manualmente."