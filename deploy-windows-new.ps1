# Kembang Kopi Windows Deployment Script
# Jalankan dengan: .\deploy-windows.ps1

param(
    [string]$ServerIP = "",
    [string]$SSHUser = "root"
)

# Colors for output
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

Write-Host " Kembang Kopi Deployment Script untuk Windows" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

if (-not $ServerIP) {
    $ServerIP = Read-Host "Masukkan IP Server VPS Anda"
}

if (-not $ServerIP) {
    Write-Error "IP Server tidak boleh kosong!"
    exit 1
}

Write-Info "Target Server: $ServerIP"
Write-Info "SSH User: $SSHUser"

# Check if SSH is available
try {
    ssh -V | Out-Null
    Write-Info "SSH client tersedia "
} catch {
    Write-Error "SSH client tidak ditemukan. Install OpenSSH atau Git Bash terlebih dahulu."
    Write-Warning "Download Git for Windows: https://git-scm.com/download/win"
    exit 1
}

# Check if files exist
if (-not (Test-Path "backend\main.py")) {
    Write-Error "File backend\main.py tidak ditemukan. Pastikan Anda berada di folder project."
    exit 1
}

Write-Info "Project files ditemukan "
