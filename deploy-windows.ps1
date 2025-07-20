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

Write-Host "🚀 Kembang Kopi Deployment Script untuk Windows" -ForegroundColor Cyan
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
    Write-Info "SSH client tersedia ✓"
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

Write-Info "Project files ditemukan ✓"

# Create deployment commands
$deployCommands = @"
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx git ufw certbot python3-certbot-nginx -y

# Setup firewall
sudo ufw allow 22
sudo ufw allow 80  
sudo ufw allow 443
sudo ufw --force enable

# Clone project
cd /opt
sudo rm -rf kembangkopi 2>/dev/null || true
sudo git clone https://github.com/kaziqu/kembangkopi.git
sudo chown -R `$USER:`$USER /opt/kembangkopi
cd /opt/kembangkopi/backend

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup directories
sudo mkdir -p /var/www/order.kembangkopi.my.id
sudo mkdir -p /var/www/dashboard.kembangkopi.my.id

# Copy frontend files
sudo cp -r /opt/kembangkopi/orderinterface/* /var/www/order.kembangkopi.my.id/
sudo cp -r /opt/kembangkopi/dashboard-frontend/* /var/www/dashboard.kembangkopi.my.id/
sudo chown -R www-data:www-data /var/www/

echo "✅ Deployment script completed successfully!"
echo "📝 Next steps:"
echo "1. Create .env file: nano /opt/kembangkopi/backend/.env"
echo "2. Configure Nginx sites"
echo "3. Setup SSL certificates"
echo "4. Start the service"
"@

Write-Info "Menjalankan deployment script di server..."
Write-Warning "Anda akan diminta password SSH untuk koneksi ke server."

# Execute deployment on server
try {
    $deployCommands | ssh $SSHUser@$ServerIP "bash -s"
    
    Write-Info "✅ Deployment script berhasil dijalankan!"
    Write-Warning "📝 Langkah selanjutnya yang harus dilakukan manual:"
    Write-Host ""
    Write-Host "1. Setup file .env:" -ForegroundColor Yellow
    Write-Host "   ssh $SSHUser@$ServerIP" -ForegroundColor Gray
    Write-Host "   cd /opt/kembangkopi/backend" -ForegroundColor Gray
    Write-Host "   cp .env.example .env" -ForegroundColor Gray
    Write-Host "   nano .env" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Setup Nginx dan SSL:" -ForegroundColor Yellow
    Write-Host "   # Ikuti step 4-5 di DEPLOYMENT.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Setup Supabase database:" -ForegroundColor Yellow
    Write-Host "   # Ikuti step 8 di DEPLOYMENT.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📚 Lihat file DEPLOYMENT.md untuk panduan lengkap!" -ForegroundColor Cyan
    
} catch {
    Write-Error "❌ Deployment gagal: $($_.Exception.Message)"
    Write-Warning "Pastikan:"
    Write-Host "- SSH key sudah terkonfigurasi atau gunakan password authentication"
    Write-Host "- Server dapat diakses dari komputer Anda"
    Write-Host "- User memiliki sudo privileges"
}

Write-Host ""
Write-Host "🌐 Setelah setup selesai, website akan tersedia di:" -ForegroundColor Cyan
Write-Host "- API: https://api.kembangkopi.my.id" -ForegroundColor Green
Write-Host "- Order: https://order.kembangkopi.my.id" -ForegroundColor Green  
Write-Host "- Dashboard: https://dashboard.kembangkopi.my.id" -ForegroundColor Green
