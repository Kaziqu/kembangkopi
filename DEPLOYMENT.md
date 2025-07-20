# Kembang Kopi Deployment Checklist

## 📋 Pre-Deployment Checklist

### ✅ Backend Configuration
- [ ] `.env` file created with all required variables
- [ ] `ENVIRONMENT=production` set in `.env`
- [ ] Valid Supabase URL and API key
- [ ] Valid reCAPTCHA secret key
- [ ] Strong barista password set
- [ ] Server has Python 3.10+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)

### ✅ Domain & DNS
- [ ] Domain `api.kembangkopi.my.id` pointing to server IP
- [ ] Domain `order.kembangkopi.my.id` pointing to frontend hosting
- [ ] Domain `dashboard.kembangkopi.my.id` pointing to frontend hosting
- [ ] SSL certificates installed for all domains

### ✅ Server Configuration
- [ ] Nginx installed and configured
- [ ] Reverse proxy setup for API
- [ ] WebSocket support enabled in Nginx
- [ ] Firewall configured (allow ports 80, 443, 22)
- [ ] SystemD service created for auto-restart

### ✅ Database Setup
- [ ] Supabase project created
- [ ] Required tables created (orders, items, settings)
- [ ] Initial data inserted: `INSERT INTO settings (key, value) VALUES ('order_open', 'true');`
- [ ] Database accessible from server

### ✅ Frontend Configuration
- [ ] All API endpoints updated to `https://api.kembangkopi.my.id`
- [ ] reCAPTCHA site key updated for production domains
- [ ] Frontend files uploaded to hosting (Netlify/Vercel/S3)
- [ ] Static files accessible via HTTPS

### ✅ Security
- [ ] Strong passwords used
- [ ] CORS configured for production domains only
- [ ] HTTPS enforced (no HTTP traffic)
- [ ] Server regularly updated
- [ ] Backup strategy in place

### ✅ Testing
- [ ] API endpoints responding correctly
- [ ] WebSocket connection working
- [ ] Order creation and completion flow working
- [ ] Dashboard login working
- [ ] reCAPTCHA validation working
- [ ] Real-time updates working between order interface and dashboard

## 🚀 Step-by-Step Deployment Guide

### 📝 **STEP 1: Persiapan Server VPS**

1. **Beli VPS** (DigitalOcean, Vultr, AWS, dll)
   - Ubuntu 20.04+ recommended
   - Minimal 1GB RAM
   - Python 3.10+

2. **Pointing Domain ke Server:**
   ```
   A Record: api.kembangkopi.my.id → IP_SERVER_ANDA
   A Record: order.kembangkopi.my.id → IP_SERVER_ANDA  
   A Record: dashboard.kembangkopi.my.id → IP_SERVER_ANDA
   ```

3. **Login ke Server:**
   ```bash
   ssh root@IP_SERVER_ANDA
   ```

### 📦 **STEP 2: Install Dependencies di Server**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Nginx, Git
sudo apt install python3 python3-pip python3-venv nginx git ufw -y

# Install certbot untuk SSL
sudo apt install certbot python3-certbot-nginx -y

# Setup firewall
sudo ufw allow 22   # SSH
sudo ufw allow 80   # HTTP
sudo ufw allow 443  # HTTPS
sudo ufw enable
```

### 🗂️ **STEP 3: Deploy Backend (FastAPI)**

```bash
# Clone project
cd /opt
sudo git clone https://github.com/kaziqu/kembangkopi.git
sudo chown -R $USER:$USER /opt/kembangkopi
cd /opt/kembangkopi/backend

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # For production

# Create .env file
cp .env.example .env
nano .env
```

**Isi file `.env` dengan data Anda:**
```env
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Dapatkan dari https://supabase.com
SUPABASE_URL=https://abcdefghijk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Dapatkan dari Google reCAPTCHA v3
RECAPTCHA_URL=https://www.google.com/recaptcha/api/siteverify
RECAPTCHA_SECRET_KEY=6Lc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Password untuk login dashboard
BARISTA_PASSWORD=YourSecurePassword123!
```

**Test backend:**
```bash
python3 main.py
# Buka browser: http://IP_SERVER:8000/docs
# Ctrl+C untuk stop
```

### 🌐 **STEP 4: Setup Nginx Reverse Proxy**

**Buat config untuk API:**
```bash
sudo nano /etc/nginx/sites-available/api.kembangkopi.my.id
```

Isi dengan:
```nginx
server {
    listen 80;
    server_name api.kembangkopi.my.id;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/api.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 🔒 **STEP 5: Setup SSL dengan Let's Encrypt**

```bash
# Generate SSL certificate
sudo certbot --nginx -d api.kembangkopi.my.id

# Test auto-renewal
sudo certbot renew --dry-run
```

### 📱 **STEP 6: Deploy Frontend Files**

**Setup directories:**
```bash
sudo mkdir -p /var/www/order.kembangkopi.my.id
sudo mkdir -p /var/www/dashboard.kembangkopi.my.id
```

**Upload Order Interface:**
```bash
# Copy files order interface
sudo cp -r /opt/kembangkopi/orderinterface/* /var/www/order.kembangkopi.my.id/
sudo chown -R www-data:www-data /var/www/order.kembangkopi.my.id
```

**Upload Dashboard:**
```bash
# Copy files dashboard
sudo cp -r /opt/kembangkopi/dashboard-frontend/* /var/www/dashboard.kembangkopi.my.id/
sudo chown -R www-data:www-data /var/www/dashboard.kembangkopi.my.id
```

**Setup Nginx untuk frontend:**
```bash
# Config untuk order interface
sudo nano /etc/nginx/sites-available/order.kembangkopi.my.id
```

Isi:
```nginx
server {
    listen 80;
    server_name order.kembangkopi.my.id;
    root /var/www/order.kembangkopi.my.id;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

```bash
# Config untuk dashboard
sudo nano /etc/nginx/sites-available/dashboard.kembangkopi.my.id
```

Isi:
```nginx
server {
    listen 80;
    server_name dashboard.kembangkopi.my.id;
    root /var/www/dashboard.kembangkopi.my.id;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

**Enable sites:**
```bash
sudo ln -s /etc/nginx/sites-available/order.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/dashboard.kembangkopi.my.id /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Generate SSL untuk frontend:**
```bash
sudo certbot --nginx -d order.kembangkopi.my.id
sudo certbot --nginx -d dashboard.kembangkopi.my.id
```

### ⚙️ **STEP 7: Setup Auto-Start Service**

```bash
sudo nano /etc/systemd/system/kembangkopi.service
```

Isi:
```ini
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
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable kembangkopi
sudo systemctl start kembangkopi

# Check status
sudo systemctl status kembangkopi
```

### 🗄️ **STEP 8: Setup Database di Supabase**

1. **Buat project baru di [supabase.com](https://supabase.com)**
2. **Buat tables:**

```sql
-- Table: orders
CREATE TABLE orders (
    order_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    status VARCHAR DEFAULT 'pending',
    total DECIMAL(10,2) NOT NULL
);

-- Table: items  
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

-- Table: settings
CREATE TABLE settings (
    key VARCHAR PRIMARY KEY,
    value VARCHAR NOT NULL
);

-- Insert initial data
INSERT INTO settings (key, value) VALUES ('order_open', 'true');
```

3. **Copy URL dan API Key ke file `.env`**

### 🔍 **STEP 9: Testing**

**Test semua endpoint:**
```bash
# API Health
curl https://api.kembangkopi.my.id/docs

# Order status
curl https://api.kembangkopi.my.id/api/isopen

# Frontend
# Buka browser: https://kembangkopi.my.id
# Buka browser: https://dashboard.kembangkopi.my.id
```

### 📱 **STEP 10: Alternative - Deploy dengan VPS Provider Managed**

Jika tidak mau setup manual, bisa pakai:
- **Vercel** (untuk frontend)
- **Railway/Render** (untuk backend)
- **Netlify** (untuk frontend)

### 🔧 **STEP 11: Monitoring & Maintenance**

```bash
# Check logs
sudo journalctl -u kembangkopi -f

# Restart service
sudo systemctl restart kembangkopi

# Update SSL certificates (auto)
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet

# Check Nginx status
sudo systemctl status nginx
```

## 🔧 Nginx Configuration Templates

### API Reverse Proxy
```nginx
server {
    listen 443 ssl;
    server_name api.kembangkopi.my.id;
    
    ssl_certificate /etc/letsencrypt/live/api.kembangkopi.my.id/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.kembangkopi.my.id/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Static File Hosting
```nginx
server {
    listen 443 ssl;
    server_name order.kembangkopi.my.id;
    root /var/www/order.kembangkopi.my.id;
    index index.html;
    
    ssl_certificate /etc/letsencrypt/live/order.kembangkopi.my.id/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/order.kembangkopi.my.id/privkey.pem;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

## 🔍 Troubleshooting

### Common Issues
1. **CORS Error**: Check `allow_origins` in config.py matches your frontend domains
2. **WebSocket Connection Failed**: Ensure Nginx has WebSocket upgrade headers
3. **Database Connection Error**: Verify Supabase URL and API key
4. **reCAPTCHA Failed**: Check secret key and site key match
5. **Login Failed**: Verify `BARISTA_PASSWORD` in .env

### Health Check URLs
- API Health: `https://api.kembangkopi.my.id/docs`
- Order Status: `https://api.kembangkopi.my.id/api/isopen`
- WebSocket: Browser console should show connection logs

### Log Locations
- SystemD logs: `journalctl -u kembangkopi -f`
- Nginx logs: `/var/log/nginx/access.log` & `/var/log/nginx/error.log`
- Application logs: Console output or log files if configured

## 📞 Support
For issues, check the logs first, then review this checklist. Most deployment issues are related to:
- Missing environment variables
- Incorrect domain configuration  
- CORS settings
- SSL certificate problems
