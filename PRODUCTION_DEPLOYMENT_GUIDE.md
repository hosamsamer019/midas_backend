# Production Deployment Guide - Authentication System

## Overview
This guide provides step-by-step instructions for deploying the authentication system to production.

---

## 🔧 **Prerequisites**

### **System Requirements:**
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.8 or higher
- **Database**: PostgreSQL 12+ (recommended) or SQLite (development only)
- **Web Server**: Nginx + Gunicorn
- **SSL Certificate**: Required for HTTPS

### **Security Requirements:**
- ✅ **HTTPS Only** - No HTTP access in production
- ✅ **Firewall** - Restrict ports (only 80, 443, 22)
- ✅ **SSL/TLS** - Valid certificate from trusted CA
- ✅ **Database Encryption** - Encrypted connections
- ✅ **Environment Variables** - No secrets in code

---

## 📋 **Pre-Deployment Checklist**

### **Code Preparation:**
- [ ] Run all tests: `python test_auth_simple.py`
- [ ] Code review completed
- [ ] Security audit passed
- [ ] Dependencies updated and tested

### **Environment Setup:**
- [ ] Production server provisioned
- [ ] Domain name configured
- [ ] SSL certificate obtained
- [ ] Database server configured
- [ ] Backup systems in place

### **Security Configuration:**
- [ ] Environment variables configured
- [ ] Secret keys generated
- [ ] Database credentials secured
- [ ] Firewall rules applied

---

## 🚀 **Step-by-Step Deployment**

### **Step 1: Server Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Install certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

### **Step 2: Database Setup**

```bash
# Create PostgreSQL database and user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE antibiogram_db;
CREATE USER antibiogram_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE antibiogram_db TO antibiogram_user;
ALTER USER antibiogram_user CREATEDB;
\q
```

### **Step 3: Application Deployment**

```bash
# Create application directory
sudo mkdir -p /var/www/antibiogram
sudo chown -R $USER:$USER /var/www/antibiogram

# Clone or copy application code
cd /var/www/antibiogram
# Copy your Django project here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Install additional production packages
pip install django-cors-headers django-environ sentry-sdk
```

### **Step 4: Environment Configuration**

```bash
# Create environment file
nano .env

# Add production settings:
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-here
DATABASE_URL=postgresql://antibiogram_user:password@localhost/antibiogram_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email settings (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security settings
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
X_FRAME_OPTIONS=DENY
```

### **Step 5: Django Configuration**

```python
# settings.py - Production settings
import os
import environ

env = environ.Env()
environ.Env.read_env()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Database
DATABASES = {
    'default': env.db(),
}

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add whitenoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Add CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.Middleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS settings
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# SSL/HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### **Step 6: Database Migration**

```bash
# Run migrations
cd /var/www/antibiogram
source venv/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### **Step 7: Gunicorn Setup**

```bash
# Create Gunicorn service file
sudo nano /etc/systemd/system/antibiogram.service

# Add this content:
[Unit]
Description=Antibiogram Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/antibiogram
Environment="PATH=/var/www/antibiogram/venv/bin"
ExecStart=/var/www/antibiogram/venv/bin/gunicorn --workers 3 --bind unix:/var/www/antibiogram/antibiogram.sock antibiogram.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable antibiogram
sudo systemctl start antibiogram
sudo systemctl status antibiogram
```

### **Step 8: Nginx Configuration**

```bash
# Create Nginx site configuration
sudo nano /etc/nginx/sites-available/antibiogram

# Add this configuration:
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/antibiogram/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/antibiogram/antibiogram.sock;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/antibiogram /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 9: SSL Certificate Setup**

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test SSL configuration
sudo openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Set up auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Step 10: Monitoring Setup**

```bash
# Install monitoring tools
sudo apt install -y htop iotop nmon

# Set up log rotation
sudo nano /etc/logrotate.d/antibiogram

# Add:
/var/www/antibiogram/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload antibiogram
    endscript
}

# Install fail2ban for security
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🔍 **Post-Deployment Testing**

### **Functional Testing:**

```bash
# Test basic connectivity
curl -I https://yourdomain.com/api/

# Test authentication endpoints
curl -X POST https://yourdomain.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Test protected endpoints
curl https://yourdomain.com/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Security Testing:**

```bash
# Test SSL configuration
sslscan yourdomain.com

# Test security headers
curl -I https://yourdomain.com/api/

# Check for vulnerabilities
nikto -h https://yourdomain.com
```

### **Performance Testing:**

```bash
# Load testing
ab -n 1000 -c 10 https://yourdomain.com/api/stats/

# Monitor resources
htop
iotop
```

---

## 📊 **Monitoring & Maintenance**

### **Log Monitoring:**

```bash
# View application logs
sudo journalctl -u antibiogram -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Django logs
tail -f /var/www/antibiogram/logs/django.log
```

### **Backup Strategy:**

```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U antibiogram_user -h localhost antibiogram_db > /backups/antibiogram_$DATE.sql

# File backup
tar -czf /backups/antibiogram_files_$DATE.tar.gz /var/www/antibiogram/

# Set up cron job
# 0 2 * * * /path/to/backup-script.sh
```

### **Health Checks:**

```bash
# Application health check
curl -f https://yourdomain.com/api/health/

# Database connectivity
python manage.py dbshell -c "SELECT 1;"

# Disk space monitoring
df -h
du -sh /var/www/antibiogram/
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **Application Not Starting:**
```bash
# Check service status
sudo systemctl status antibiogram

# Check logs
sudo journalctl -u antibiogram -n 50

# Check socket permissions
ls -la /var/www/antibiogram/antibiogram.sock
```

#### **Database Connection Issues:**
```bash
# Test database connection
python manage.py dbshell

# Check PostgreSQL status
sudo systemctl status postgresql

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### **Nginx Issues:**
```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart nginx
sudo systemctl restart antibiogram
```

#### **SSL Issues:**
```bash
# Check certificate
openssl s_client -connect yourdomain.com:443

# Renew certificate
sudo certbot renew

# Check certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

---

## 🔄 **Update Procedure**

### **Code Updates:**
```bash
# Stop application
sudo systemctl stop antibiogram

# Backup current version
cp -r /var/www/antibiogram /backups/antibiogram_$(date +%Y%m%d)

# Deploy new code
cd /var/www/antibiogram
git pull origin main  # or copy new files

# Install new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Start application
sudo systemctl start antibiogram

# Monitor logs
sudo journalctl -u antibiogram -f
```

### **Rollback Procedure:**
```bash
# Stop application
sudo systemctl stop antibiogram

# Restore backup
cp -r /backups/antibiogram_20231201 /var/www/antibiogram

# Restart application
sudo systemctl start antibiogram
```

---

## 📞 **Support & Emergency Contacts**

### **Emergency Procedures:**
1. **Application Down**: Check service status, restart if needed
2. **Database Issues**: Check PostgreSQL status, restore from backup if needed
3. **Security Incident**: Isolate affected systems, notify security team
4. **Data Loss**: Restore from latest backup, assess data integrity

### **Contact Information:**
- **System Administrator**: [Admin Contact]
- **Database Administrator**: [DBA Contact]
- **Security Team**: [Security Contact]
- **Infrastructure Team**: [Infra Contact]

### **Escalation Matrix:**
- **Level 1**: System monitoring alerts
- **Level 2**: Application performance issues
- **Level 3**: Service outages
- **Level 4**: Security incidents or data breaches

---

## ✅ **Deployment Checklist**

### **Pre-Launch:**
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance benchmarks met
- [ ] Backup systems tested
- [ ] Monitoring configured

### **Launch Day:**
- [ ] Code deployed successfully
- [ ] Services starting correctly
- [ ] SSL certificates valid
- [ ] DNS propagation complete
- [ ] Basic functionality tested

### **Post-Launch:**
- [ ] User acceptance testing
- [ ] Performance monitoring
- [ ] Security monitoring
- [ ] User training completed
- [ ] Documentation updated

---

**🎉 Deployment Complete!**

Your authentication system is now live and secure. Monitor the system closely for the first 24-48 hours and be prepared to address any issues that arise.
