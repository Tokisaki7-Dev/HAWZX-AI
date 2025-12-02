<#
.SYNOPSIS
    Automatiza a inicialização do backend HAWZX-AI.
.DESCRIPTION
    Este script verifica e cria o ambiente virtual, instala as dependências
    e inicia o servidor FastAPI, conforme definido no guia do projeto.
.EXAMPLE
    .\infra\scripts\start-backend.ps1
    Inicia o backend a partir da raiz do projeto.
#>

Write-Host "--- Iniciando o Backend HAWZX-AI ---" -ForegroundColor Green

# Define o diretório raiz do projeto (assumindo que o script está em infra/scripts)
$projectRoot = (Get-Item -Path (Join-Path $PSScriptRoot "..\" "..\" )).FullName
Write-Host "Raiz do projeto: $projectRoot"

# Define o caminho para o ambiente virtual
$venvPath = Join-Path -Path $projectRoot -ChildPath ".venv"

# 1. Verifica e cria o ambiente virtual se não existir
if (-not (Test-Path -Path $venvPath -PathType Container)) {
    Write-Host "Ambiente virtual não encontrado. Criando em '$venvPath'..."
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha ao criar o ambiente virtual. Verifique se o Python está instalado e no PATH."
        exit 1
    }
}

# 2. Ativa o ambiente virtual
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"
. $activateScript
Write-Host "Ambiente virtual ativado."

# 3. Instala/atualiza as dependências
Write-Host "Instalando/atualizando dependências de 'requirements.txt'..."
$requirementsFile = Join-Path -Path $projectRoot -ChildPath "requirements.txt"
pip install -r $requirementsFile --upgrade

# 4. Inicia o servidor backend
Write-Host "Iniciando o servidor FastAPI... (Pressione CTRL+C para parar)" -ForegroundColor Yellow
$mainScriptPath = Join-Path -Path $projectRoot -ChildPath "src\web\main.py"
uvicorn src.web.main:app --reload --host 0.0.0.0 --port 8000