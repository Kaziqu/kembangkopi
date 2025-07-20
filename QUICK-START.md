# 🚀 Quick Start - Deploy Kembang Kopi

## 📋 Yang Anda Butuhkan:
- VPS Ubuntu (DigitalOcean, Vultr, AWS, dll) - minimal 1GB RAM
- Domain (atau subdomain) yang bisa di-pointing ke server
- Akun Supabase (gratis)
- Akun Google reCAPTCHA v3 (gratis)

## ⚡ Deploy dalam 10 Menit:

### 1. **Beli VPS & Setup Domain**
```
Beli VPS Ubuntu 20.04+
Pointing domain:
- A Record: api.kembangkopi.my.id → IP_VPS_ANDA
- A Record: order.kembangkopi.my.id → IP_VPS_ANDA  
- A Record: dashboard.kembangkopi.my.id → IP_VPS_ANDA
```

### 2. **Jalankan Script Auto-Deploy**
```powershell
# Di komputer LOCAL Windows (PowerShell)
# Script ini akan otomatis SSH ke server dan install semua
.\deploy-windows.ps1

# Script akan tanya IP server VPS Anda, lalu otomatis:
# - SSH ke server
# - Install Python, Nginx, dependencies
# - Clone project dari GitHub
# - Setup folder dan files
```

**ATAU manual SSH ke server:**
```bash
# SSH ke server VPS dari komputer local
ssh root@IP_VPS_ANDA

# Lalu jalankan command manual di server
```

### 3. **Setup Environment Variables**
```bash
# Di server VPS
cd /opt/kembangkopi/backend
cp .env.example .env
nano .env
```

Isi dengan:
```env
ENVIRONMENT=production
SUPABASE_URL=https://abcdefg.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
RECAPTCHA_SECRET_KEY=6Lc-xxxxxxxxxxxxx
BARISTA_PASSWORD=YourPassword123!
```

### 4. **Setup Nginx (Copy-Paste)**
```bash
# API Config
sudo tee /etc/nginx/sites-available/api.kembangkopi.my.id > /dev/null <<EOF
server {
    listen 80;
    server_name api.kembangkopi.my.id;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Order Interface Config  
sudo tee /etc/nginx/sites-available/order.kembangkopi.my.id > /dev/null <<EOF
server {
    listen 80;
    server_name order.kembangkopi.my.id;
    root /var/www/order.kembangkopi.my.id;
    index index.html;
    location / { try_files \$uri \$uri/ =404; }
}
EOF

# Dashboard Config
sudo tee /etc/nginx/sites-available/dashboard.kembangkopi.my.id > /dev/null <<EOF
server {
    listen 80;
    server_name dashboard.kembangkopi.my.id;
    root /var/www/dashboard.kembangkopi.my.id;
    index index.html;
    location / { try_files \$uri \$uri/ =404; }
}
EOF

# Enable sites
sudo ln -s /etc/nginx/sites-available/api.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/order.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/dashboard.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

### 5. **Setup SSL (Copy-Paste)**
```bash
# Generate SSL certificates
sudo certbot --nginx -d api.kembangkopi.my.id -d order.kembangkopi.my.id -d dashboard.kembangkopi.my.id
```

### 6. **Start Backend Service**
```bash
# Create service
sudo tee /etc/systemd/system/kembangkopi.service > /dev/null <<EOF
[Unit]
Description=Kembang Kopi FastAPI app
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kembangkopi/backend
Environment=PATH=/opt/kembangkopi/backend/venv/bin
ExecStart=/opt/kembangkopi/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable kembangkopi
sudo systemctl start kembangkopi
```

### 7. **Setup Supabase Database**
1. Buka [supabase.com](https://supabase.com) → Create new project
2. Go to SQL Editor, paste & run:
```sql
CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    status VARCHAR DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR REFERENCES orders(order_id),
    name VARCHAR NOT NULL,
    milk VARCHAR,
    sugar VARCHAR,
    quantity INTEGER DEFAULT 1,
    price DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL
);

CREATE TABLE settings (
    key VARCHAR PRIMARY KEY,
    value VARCHAR NOT NULL
);

INSERT INTO settings (key, value) VALUES ('order_open', 'true');
```
3. Copy URL & API key ke file `.env`

### 8. **Setup reCAPTCHA**
1. Buka [Google reCAPTCHA](https://www.google.com/recaptcha/admin)
2. Create site → reCAPTCHA v3
3. Add domains: `order.kembangkopi.my.id`, `dashboard.kembangkopi.my.id`
4. Copy secret key ke `.env`

### 9. **Test & Selesai! 🎉**
```bash
# Check status
sudo systemctl status kembangkopi

# Test endpoints
curl https://api.kembangkopi.my.id/docs
```

**Buka browser:**
- ✅ `https://order.kembangkopi.my.id` - Order interface
- ✅ `https://dashboard.kembangkopi.my.id` - Dashboard barista  
- ✅ `https://api.kembangkopi.my.id/docs` - API documentation

## 🆘 Troubleshooting Cepat:

**Error 502 Bad Gateway:**
```bash
sudo systemctl status kembangkopi
sudo journalctl -u kembangkopi -f
```

**Database connection error:**
- Check SUPABASE_URL dan SUPABASE_KEY di .env
- Pastikan tables sudah dibuat

**CORS error:**
- Check domain di config.py
- Pastikan SSL aktif (https://)

**WebSocket tidak connect:**
- Check Nginx config ada upgrade headers
- Pastikan service backend running

## 💰 Estimasi Biaya Bulanan:
- VPS 1GB RAM: $5-10/bulan
- Domain: $10-15/tahun  
- Supabase: Gratis (untuk traffic kecil)
- reCAPTCHA: Gratis
- **Total: ~$5-10/bulan**

**🎯 Butuh bantuan? Check DEPLOYMENT.md untuk panduan detail!**
