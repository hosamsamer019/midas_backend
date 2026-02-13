# Server Maintenance Guide
## Preventing Server Downtime and 500 Errors

### 🚨 Common Issues & Solutions

#### 1. Server Stops Unexpectedly
**Symptoms:** 500 errors, "Failed to fetch" in browser console
**Causes:** Process crashes, system restarts, resource exhaustion

**Prevention:**
- Use process managers (PM2, supervisorctl)
- Set up automatic restarts
- Monitor server logs regularly

#### 2. Port Conflicts
**Symptoms:** "Port already in use" errors
**Prevention:**
- Use dedicated ports (8000 for Django, 3000 for Next.js)
- Check port availability before starting servers

#### 3. Database Connection Issues
**Symptoms:** Database errors in logs
**Prevention:**
- Ensure PostgreSQL/MySQL is running
- Check database credentials in settings.py
- Use connection pooling

### 🛠️ Quick Fixes

#### Restart Servers
```bash
# Windows
cd Data_Analysis_Project
python manage.py runserver    # Terminal 1
cd frontend && npm run dev    # Terminal 2

# Or use the batch file
start_servers.bat
```

#### Check Server Health
```bash
python check_servers.py
```

#### Kill Conflicting Processes
```bash
# Windows - Find process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Find process using port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### 📋 Best Practices

#### 1. Development Environment
- Always start servers in separate terminals
- Use `python manage.py runserver --noreload` for debugging
- Monitor terminal output for errors

#### 2. Production Deployment
- Use Gunicorn + Nginx for Django
- Use PM2 for Next.js
- Set up monitoring (health checks, logs)
- Use environment variables for configuration

#### 3. Database Management
- Regular backups
- Monitor connection pools
- Use database migration best practices

#### 4. Error Monitoring
- Check Django logs: `tail -f logs/django.log`
- Monitor Next.js console output
- Set up error alerting

### 🔧 Advanced Solutions

#### Process Monitoring (Windows)
```batch
# Create a monitoring script
@echo off
:loop
python check_servers.py
timeout /t 60 /nobreak > nul
goto loop
```

#### Auto-restart on Crash (Linux/Mac)
```bash
# Install supervisor
pip install supervisor

# Configure supervisor for Django
[program:django]
command=python manage.py runserver
directory=/path/to/project
autorestart=true
```

#### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    restart: unless-stopped
```

### 🚨 Emergency Procedures

#### When Servers Won't Start
1. Check system resources (RAM, CPU)
2. Verify Python/Node.js installations
3. Check database connectivity
4. Review recent code changes
5. Check firewall/antivirus settings

#### Database Issues
1. Verify database service is running
2. Check connection string in settings.py
3. Run database migrations: `python manage.py migrate`
4. Reset database if needed: `python manage.py flush`

#### Frontend Build Issues
1. Clear Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `npm install`
3. Check Node.js version compatibility

### 📞 Support

If issues persist:
1. Check the ISSUES_AND_FIXES.md file
2. Review FINAL_IMPLEMENTATION_REPORT.md
3. Run comprehensive tests: `python comprehensive_test.py`
4. Check system logs and error messages

### 🎯 Prevention Checklist

- [ ] Start servers using `start_servers.bat`
- [ ] Monitor servers with `python check_servers.py`
- [ ] Keep terminals open and visible
- [ ] Check logs regularly for errors
- [ ] Backup database regularly
- [ ] Update dependencies periodically
- [ ] Test after code changes

**Remember:** Prevention is better than cure. Regular monitoring and proper startup procedures will minimize downtime.
