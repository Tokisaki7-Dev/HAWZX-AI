<#
.SYNOPSIS
    Monitora inatividade de edição e injeta automaticamente o snippet de retomada do Gemini.
.DESCRIPTION
    Verifica o tempo desde a última modificação de arquivo no workspace. Se exceder o limite
    (IdleMinutes) e o snippet não tiver sido enviado recentemente, ativa a janela do VS Code
    e envia a combinação de teclas (Ctrl+Shift+G) mapeada para o snippet `gemini-resume`.

    Limitações:
    - Não detecta estado real do Gemini; usa heurística de inatividade.
    - Requer VS Code aberto com o keybinding configurado.
    - Pode focar a janela do VS Code ao disparar.

.PARAMETER WorkspacePath
    Caminho raiz do workspace (default: diretório atual).
.PARAMETER IdleMinutes
    Minutos de inatividade antes de disparar (default: 5).
.PARAMETER CheckSeconds
    Intervalo em segundos entre checagens (default: 30).
.PARAMETER CooldownMinutes
    Mínimo de minutos entre disparos consecutivos (default: 3).

.EXAMPLE
    ./infra/gemini-auto-resume.ps1 -IdleMinutes 4 -CheckSeconds 20

.NOTES
    Interrompa com CTRL+C. Log em `.gemini-resume-log` na raiz.
#>
param(
    [string]$WorkspacePath = (Resolve-Path '.').Path,
    [int]$IdleMinutes = 5,
    [int]$CheckSeconds = 30,
    [int]$CooldownMinutes = 3
)

Write-Host "[Gemini-Auto-Resume] Iniciando monitor em '$WorkspacePath'" -ForegroundColor Cyan

if (-not (Test-Path $WorkspacePath)) {
    Write-Error "WorkspacePath inválido: $WorkspacePath"; exit 1
}

$logFile = Join-Path $WorkspacePath '.gemini-resume-log'
if (-not (Test-Path $logFile)) { New-Item -Path $logFile -ItemType File -Force | Out-Null }

function Get-LastEditTime {
    # Ignora .venv e diretórios grandes
    $items = Get-ChildItem -Path $WorkspacePath -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike '*\.venv*' }
    if ($items.Count -eq 0) { return (Get-Date).AddMinutes(-999) }
    ($items | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
}

function Should-Fire($lastEdit, $lastFire) {
    $idleThreshold = (Get-Date).AddMinutes(-$IdleMinutes)
    $cooldownThreshold = (Get-Date).AddMinutes(-$CooldownMinutes)
    return ($lastEdit -lt $idleThreshold) -and ($lastFire -lt $cooldownThreshold)
}

function Fire-ResumeSnippet {
    Write-Host "[Gemini-Auto-Resume] Disparando snippet de retomada..." -ForegroundColor Yellow
    try {
        Add-Type -AssemblyName System.Windows.Forms | Out-Null
        $shell = New-Object -ComObject WScript.Shell
        # Tenta focar janela VS Code (título contém 'Visual Studio Code')
        $activated = $shell.AppActivate('Visual Studio Code')
        if (-not $activated) { Write-Warning 'Não foi possível focar VS Code; verifique se está aberto.' }
        Start-Sleep -Milliseconds 300
        # Atalho configurado Ctrl+Shift+G
        $shell.SendKeys('^+g')
        (Get-Date).ToString('u') + " - resume fired" | Add-Content $logFile
    }
    catch {
        Write-Error "Falha ao enviar teclas: $_"
    }
}

$lastFireTime = (Get-Date).AddMinutes(-999)
Write-Host "[Gemini-Auto-Resume] IdleMinutes=$IdleMinutes CheckSeconds=$CheckSeconds CooldownMinutes=$CooldownMinutes" -ForegroundColor DarkGray

while ($true) {
    try {
        $lastEdit = Get-LastEditTime
        if (Should-Fire -lastEdit $lastEdit -lastFire $lastFireTime) {
            Fire-ResumeSnippet
            $lastFireTime = Get-Date
        }
        else {
            Write-Host ("[Status] Última edição: {0:u} | Próximo disparo possível após: {1:u}" -f $lastEdit, (Get-Date).AddMinutes($CooldownMinutes)) -ForegroundColor DarkGray
        }
    }
    catch {
        Write-Warning "Erro no loop: $_"
    }
    Start-Sleep -Seconds $CheckSeconds
}
