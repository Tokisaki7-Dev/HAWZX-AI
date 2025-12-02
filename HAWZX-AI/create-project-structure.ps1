<#
.SYNOPSIS
    Cria a estrutura completa de diretórios e arquivos iniciais para o projeto HAWZX-AI.
.DESCRIPTION
    Este script automatiza a criação do projeto seguindo a arquitetura definida no
    HAWZX_AI_Guide.md. Ele gera todas as pastas, arquivos .gitkeep para versionamento
    e arquivos de configuração básicos como .gitignore, requirements.txt e um
    ponto de entrada para o backend FastAPI.
.PARAMETER NewProjectName
    O nome da nova pasta raiz do projeto (ex: 'HAWZX-AI' ou 'HAWZX-AI-v2').
.PARAMETER ProjectParentPath
    O caminho onde a pasta raiz do novo projeto será criada (ex: 'C:\Projetos').
.PARAMETER GuideSourceDir
    O caminho do diretório onde o arquivo HAWZX_AI_Guide.md está localizado (ex: 'C:\Users\endri\HAWZX').
.EXAMPLE
    # Executa o script para criar o projeto 'HAWZX-AI-v2' em 'C:\Projetos\'
    # e copia o guia de 'C:\Users\endri\HAWZX\'
    .\create-project-structure.ps1 -NewProjectName "HAWZX-AI-v2" -ProjectParentPath "C:\Projetos\" -GuideSourceDir "C:\Users\endri\HAWZX"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$NewProjectName,
    [Parameter(Mandatory=$true)]
    [string]$ProjectParentPath,
    [Parameter(Mandatory=$true)]
    [string]$GuideSourceDir
)

$projectName = $NewProjectName
$projectRoot = Join-Path -Path $ProjectParentPath -ChildPath $projectName

Write-Host "--- Iniciando a criação automática do projeto HAWZX-AI ---" -ForegroundColor Cyan
Write-Host "O projeto '$projectName' será criado em: $projectRoot"

if (Test-Path -Path $projectRoot) {
    Write-Error "O diretório do projeto '$projectRoot' já existe. A execução foi interrompida para evitar sobrescrever dados."
    exit 1
}

# --- 1. Criação da Estrutura de Pastas ---
Write-Host "Criando estrutura de diretórios..." -ForegroundColor Yellow

$directories = @(
    "assets",
    "data",
    "models",
    "src",
    "src/character",
    "src/voice",
    "src/vision",
    "src/ai",
    "src/games",
    "src/overlay",
    "src/db",
    "src/web",
    "infra",
    "infra/docker",
    "infra/monitoring",
    "infra/scripts",
    "tests",
    "ci",
    "ci/github-actions"
)

New-Item -Path $projectRoot -ItemType Directory | Out-Null

$directories | ForEach-Object {
    $dirPath = Join-Path -Path $projectRoot -ChildPath $_ 
    New-Item -Path $dirPath -ItemType Directory -Force | Out-Null
}

# --- 2. Criação de arquivos .gitkeep ---
Write-Host "Criando arquivos .gitkeep para pastas vazias..."
$gitkeepFolders = @(
    "assets", "data", "models", "src/character", "src/voice", "src/vision",
    "src/ai", "src/games", "src/overlay", "src/db", "infra/monitoring",
    "ci/github-actions", "tests"
)

$gitkeepFolders | ForEach-Object {
    New-Item -Path (Join-Path $projectRoot $_ ".gitkeep") -ItemType File | Out-Null
}

# --- 3. Criação de Arquivos Iniciais ---
Write-Host "Criando arquivos de configuração iniciais..." -ForegroundColor Yellow

# .gitignore
@'# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
.venv/
virtual environment
venv/
ENV/'@ | Set-Content -Path (Join-Path $projectRoot ".gitignore")

# README.md
@'# 🧠 HAWZX AI

HAWZX AI é um assistente de jogos de última geração, projetado para ser executado localmente, com custo zero e de código aberto.

## Visão Geral

Este projeto visa fornecer funcionalidades avançadas de IA para gamers, incluindo reconhecimento de tela em tempo real, chat de voz com personalidade, estratégias de jogo contextuais e muito mais.

## Começando

> Instruções de instalação e execução serão adicionadas aqui.

Consulte o `HAWZX_AI_Guide.md` para detalhes completos sobre a arquitetura e o roadmap.
'@ | Set-Content -Path (Join-Path $projectRoot "README.md")

# requirements.txt
"fastapi", "uvicorn[standard]", "python-dotenv" | Set-Content -Path (Join-Path $projectRoot "requirements.txt")

# src/web/main.py
@'from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI(
    title="HAWZX AI Backend",
    description="Serviços de IA para o assistente de jogos HAWZX.",
    version="0.1.0"
)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo ao HAWZX AI!"}
'@ | Set-Content -Path (Join-Path $projectRoot "src/web/main.py")

# --- 4. Cópia de Documentação Essencial ---
Write-Host "Copiando documentação principal..." -ForegroundColor Yellow

$guideFileName = "HAWZX_AI_Guide.md"
$sourceGuidePath = Join-Path -Path $GuideSourceDir -ChildPath $guideFileName

if (Test-Path -Path $sourceGuidePath) {
    Copy-Item -Path $sourceGuidePath -Destination $projectRoot -Force
    Write-Host "Arquivo '$guideFileName' copiado para a raiz do projeto."
} else {
    Write-Error "Arquivo guia '$sourceGuidePath' não encontrado em '$GuideSourceDir'. Não foi possível copiar o guia."
    exit 1
}

Write-Host "--- Estrutura do projeto HAWZX-AI criada com sucesso! ---" -ForegroundColor Green
Write-Host "Próximos passos recomendados:"
Write-Host "1. Navegue até o diretório do projeto: cd '$projectRoot'"
Write-Host "2. Execute o setup do ambiente: .\infra\scripts\setup-env.ps1"
