# ============================================================
# git-security-scan hooks 설치 스크립트 (Windows PowerShell)
# 사용법: PowerShell -ExecutionPolicy Bypass -File hooks/install.ps1
# ============================================================

$GitDir = git rev-parse --git-dir 2>$null
if (-not $GitDir) {
    Write-Host "❌ git 저장소가 아닙니다. 프로젝트 루트에서 실행하세요." -ForegroundColor Red
    exit 1
}

$HooksDir = Join-Path $GitDir "hooks"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Source = Join-Path $ScriptDir "pre-commit"
$Dest = Join-Path $HooksDir "pre-commit"

Write-Host "🔧 git-security-scan 훅 설치 중..." -ForegroundColor Cyan

Copy-Item -Path $Source -Destination $Dest -Force
Write-Host "✅ pre-commit 훅 설치 완료: $Dest" -ForegroundColor Green
Write-Host ""
Write-Host "이제 git commit 시 자동으로 보안 검사가 실행됩니다."
Write-Host "훅 제거: Remove-Item `"$Dest`""
