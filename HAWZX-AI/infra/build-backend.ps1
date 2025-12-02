<#
.SYNOPSIS
    Empacota o backend FastAPI em um único executável (.exe) usando PyInstaller.
.DESCRIPTION
    Este script ativa o ambiente virtual, instala o PyInstaller e executa o build,
    colocando o resultado final no diretório 'dist'.
.EXAMPLE
    .\infra\scripts\build-backend.ps1
    Executa o processo de build a partir da raiz do projeto.
#>

Write-Host "--- Empacotando o Backend HAWZX-AI para Distribuição ---" -ForegroundColor Cyan

# Define o diretório raiz do projeto
$projectRoot = (Get-Item -Path (Join-Path $PSScriptRoot "..\" "..\" )).FullName
Write-Host "Raiz do projeto: $projectRoot"

# Define o caminho para o ambiente virtual
$venvPath = Join-Path -Path $projectRoot -ChildPath ".venv"
if (-not (Test-Path -Path $venvPath -PathType Container)) {
    Write-Error "Ambiente virtual não encontrado. Execute '.\infra\scripts\start-backend.ps1' primeiro."
    exit 1
}

# Ativa o ambiente virtual
$activateScript = Join-Path -Path $venvPath -ChildPath "Scripts\Activate.ps1"
. $activateScript
Write-Host "Ambiente virtual ativado."

# Instala o PyInstaller se ainda não estiver instalado
Write-Host "Verificando/instalando PyInstaller..."
pip install pyinstaller

# Executa o PyInstaller
Write-Host "Iniciando o build com PyInstaller... Isso pode levar alguns minutos." -ForegroundColor Yellow

Push-Location $projectRoot

pyinstaller --name HAWZX-Backend --onefile --noconsole "src/web/main.py"

Pop-Location

Write-Host "Build concluído! O executável está em '$projectRoot\dist'" -ForegroundColor Green