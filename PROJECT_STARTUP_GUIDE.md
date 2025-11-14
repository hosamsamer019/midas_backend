# Project Startup Guide
## Smart Antibiogram System - Quick Start

**Status**: ✅ CURRENTLY RUNNING

---

## Current Server Status

### ✅ Backend Server (Django)
- **Status**: RUNNING
- **URL**: http://127.0.0.1:8000
- **API Base**: http://127.0.0.1:8000/api
- **Terminal**: Active (Terminal 1)

### ✅ Frontend Server (Next.js)
- **Status**: RUNNING
- **URL**: http://localhost:3000
- **Network**: http://192.168.1.8:3000
- **Terminal**: Active (Terminal 2)

---

## Access the Application

### 1. Open Frontend in Browser
```
http://localhost:3000
```
You should see the **Login to Antibiogram System** page.

### 2. Test Backend API
```
http://127.0.0.1:8000/api/welcome/
```
You should see: `{"message":"Welcome to the Data Analysis API Service!"}`

### 3. View API Endpoints
Try these endpoints in your browser:
- Stats: http://127.0.0.1:8000/api/stats/
- Bacteria List: http://127.0.0.1:8000/api/bacteria-list/
- Departments: http://127.0.0.1:8000/api/departments-list/

---

## If You Need to Restart

### Stop the Servers
Press `CTRL+C` in each terminal to stop the servers.

### Start Backend Server
```bash
cd Data_Analysis_Project
py manage.py runserver
```

Expected output:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version 5.2.7, using settings 'antibiogram.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Start Frontend Server
```bash
cd Data_Analysis_Project/frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.0.0 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.1.8:3000

✓ Ready in 23.2s
```

---

## Login Credentials

### Default Users
Check the database for existing users or create a new superuser:

```bash
cd Data_Analysis_Project
py manage.py createsuperuser
```

Follow the prompts to create:
- Username
- Email (optional)
- Password

---

## Available API Endpoints

### Public Endpoints (No Authentication)
- `GET /api/welcome/` - Welcome message
- `GET /api/stats/` - Dashboard statistics
- `GET /api/bacteria-list/` - List of bacteria
- `GET /api/departments-list/` - List of departments
- `GET /api/sensitivity-distribution/` - Sensitivity data
- `GET /api/antibiotic-effectiveness/` - Effectiveness metrics
- `GET /api/resistance-over-time/` - Time-series data
- `GET /api/resistance-heatmap/` - Heatmap data

### Authenticated Endpoints (JWT Token Required)
- `GET /api/users/` - User management
- `GET /api/bacteria/` - Bacteria CRUD
- `GET /api/antibiotics/` - Antibiotics CRUD
- `GET /api/samples/` - Samples CRUD
- `GET /api/results/` - Test results CRUD
- `GET /api/uploads/` - File uploads
- `GET /api/ai-recommendations/` - AI recommendations
- `GET /api/analytics/` - Analytics data
- `GET /api/antibiotics-list/` - Antibiotics list

### AI Endpoints
- `POST /api/ai/predict/` - Get antibiotic recommendations
  ```json
  {
    "bacteria_name": "E. coli"
  }
  ```

---

## Testing the System

### Quick API Test
```bash
cd Data_Analysis_Project
py test_live_api.py
```

### Comprehensive E2E Test
```bash
cd Data_Analysis_Project
py test_e2e.py
```

### Full System Test
```bash
cd Data_Analysis_Project
py full_system_test.py
```

---

## Troubleshooting

### Port Already in Use

**Backend (Port 8000)**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart
py manage.py runserver
```

**Frontend (Port 3000)**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Then restart
cd frontend && npm run dev
```

### Database Issues
```bash
# Reset migrations
py manage.py migrate --run-syncdb

# Load initial data
py manage.py load_initial_data
```

### Frontend Build Issues
```bash
cd frontend
rm -rf .next
npm run dev
```

---

## Development Workflow

### 1. Make Backend Changes
- Edit files in Django apps
- Server auto-reloads on file changes
- Check terminal for errors

### 2. Make Frontend Changes
- Edit files in `frontend/src/`
- Hot Module Replacement (HMR) updates automatically
- Check browser console for errors

### 3. Database Changes
```bash
# Create migrations
py manage.py makemigrations

# Apply migrations
py manage.py migrate
```

---

## Project Structure

```
Data_Analysis_Project/
├── antibiogram/          # Django settings
├── api/                  # REST API endpoints
├── users/                # User management
├── bacteria/             # Bacteria models
├── antibiotics/          # Antibiotic models
├── samples/              # Sample models
├── results/              # Test result models
├── uploads/              # File upload handling
├── ai_recommendations/   # AI recommendation models
├── ai_engine/            # ML model training
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/         # Pages
│   │   ├── components/  # React components
│   │   └── context/     # Context providers
│   └── public/          # Static files
├── DB/                   # Database files
└── manage.py            # Django management
```

---

## Next Steps

### For Development
1. ✅ Servers are running
2. Open http://localhost:3000 in browser
3. Start developing features
4. Test changes in real-time

### For Testing
1. Run test scripts (see Testing section)
2. Check API endpoints
3. Test frontend functionality
4. Verify data integrity

### For Production
1. Set DEBUG = False in settings.py
2. Generate new SECRET_KEY
3. Configure PostgreSQL
4. Set up environment variables
5. Deploy with Gunicorn + Nginx

---

## Quick Reference Commands

```bash
# Backend
cd Data_Analysis_Project
py manage.py runserver              # Start server
py manage.py migrate                # Run migrations
py manage.py createsuperuser        # Create admin user
py manage.py test                   # Run tests

# Frontend
cd Data_Analysis_Project/frontend
npm run dev                         # Start dev server
npm run build                       # Build for production
npm start                           # Start production server

# Testing
cd Data_Analysis_Project
py test_live_api.py                 # Test live API
py test_e2e.py                      # E2E tests
py full_system_test.py              # Full system test
```

---

## Support

For issues or questions:
1. Check the terminal output for errors
2. Review the test reports in the project root
3. Check the documentation files:
   - `TESTING_COMPLETE_SUMMARY.md`
   - `FINAL_E2E_TEST_REPORT.md`
   - `COMPLETE_SYSTEM_VERIFICATION_REPORT.md`

---

**Last Updated**: November 14, 2025  
**System Status**: ✅ FULLY OPERATIONAL  
**Servers**: ✅ RUNNING  
**Ready for**: Development, Testing, Demonstrations

---

*The system is ready to use. Open http://localhost:3000 in your browser to get started!*
