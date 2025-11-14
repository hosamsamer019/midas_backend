# Smart Antibiogram System - Project Startup Guide

## Overview
This document provides step-by-step instructions to start the Smart Antibiogram System, a comprehensive web application for antibiogram data analysis with AI-powered antibiotic recommendations.

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL (or use Docker)
- Git

## Quick Start (Recommended)

### Option 1: Docker Setup (Easiest)
```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd smart-antibiogram

# Start all services with Docker Compose
docker-compose up --build

# Access the application:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Option 2: Local Development Setup

#### Step 1: Backend Setup
```bash
# Navigate to project root
cd /path/to/smart-antibiogram

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Load initial data (optional)
python manage.py load_initial_data

# Start Django development server
python manage.py runserver
```
**Expected Output:**
```
System check identified no issues (0 silenced).
Django version 5.2.7, using settings 'antibiogram.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### Step 2: Frontend Setup
```bash
# Open new terminal and navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start Next.js development server
npm run dev
```
**Expected Output:**
```
▲ Next.js 16.0.0 (Turbopack)
- Local:        http://localhost:3000
- Network:      http://192.168.1.5:3000
✓ Ready in 894ms
```

## Reopening Project on Same Device

### If Project Was Previously Set Up

#### Terminal Commands to Run:
```bash
# Terminal 1: Start Backend
python manage.py runserver

# Terminal 2: Start Frontend
cd frontend && npm run dev
```

#### Quick Verification:
1. **Backend**: Check `http://127.0.0.1:8000` shows Django REST framework page
2. **Frontend**: Check `http://localhost:3000` loads the dashboard
3. **Database**: Should already be migrated and populated

#### If Issues Occur:
```bash
# Kill any existing processes on ports 8000/3000
taskkill /F /PID <PID>  # Windows
# or
kill -9 <PID>  # Linux/Mac

# Clear Next.js cache if frontend issues
cd frontend && rm -rf .next && npm run dev

# Reset database if needed
python manage.py migrate --run-syncdb
```

## Access the Application

1. **Open your web browser**
2. **Navigate to:** `http://localhost:3000`
3. **Login with default credentials:**
   - Username: `admin`
   - Password: `password123`

## System Architecture

### Backend (Django REST Framework)
- **URL:** http://127.0.0.1:8000
- **Technology:** Python 3.9, Django 5.2, PostgreSQL
- **Key Features:**
  - RESTful API endpoints
  - JWT authentication
  - AI-powered antibiotic recommendations
  - File upload with Cloudinary integration
  - PDF/Excel report generation

### Frontend (Next.js + TypeScript)
- **URL:** http://localhost:3000
- **Technology:** Next.js 16, TypeScript, TailwindCSS
- **Key Features:**
  - Interactive dashboard with charts
  - Real-time data filtering
  - Drag-and-drop file upload
  - Responsive design

## Available Features

### Dashboard
- Statistics cards (total samples, bacteria, antibiotics)
- Pie chart: Sensitivity distribution
- Bar chart: Antibiotic effectiveness
- Line chart: Resistance over time
- Heatmap: Resistance patterns

### Data Management
- CRUD operations for bacteria, antibiotics, samples
- Excel/CSV data import
- Advanced filtering (date, bacteria, department)

### AI Features
- Antibiotic recommendations based on bacteria type
- Machine learning model (Random Forest)
- Real-time predictions

### Reports & Analytics
- PDF report generation with date filtering
- Excel export functionality
- Digital signature support

### Advanced Features
- OCR processing for antibiogram images
- Heatmap visualization
- Role-based access control

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

### Dashboard Data
- `GET /api/stats/` - Dashboard statistics
- `GET /api/sensitivity-distribution/` - Sensitivity data
- `GET /api/antibiotic-effectiveness/` - Effectiveness metrics
- `GET /api/resistance-over-time/` - Time-series data
- `GET /api/resistance-heatmap/` - Heatmap data

### Data Management
- `GET /api/bacteria/` - List bacteria
- `GET /api/antibiotics/` - List antibiotics
- `GET /api/samples/` - List samples
- `GET /api/results/` - List test results

### AI & Advanced Features
- `POST /api/ai/predict/` - Get antibiotic recommendations
- `POST /api/ocr/` - Process antibiogram images
- `POST /api/digital-signature/` - Create digital signatures
- `GET /api/reports/{type}/` - Generate reports

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process using port 3000
taskkill /F /PID <PID>

# Or use a different port
npm run dev -- --port 3001
```

#### Database Connection Issues
```bash
# Ensure PostgreSQL is running
# Update settings.py with correct database credentials
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'antibiogram',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Module Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# For OCR functionality
pip install pytesseract opencv-python
# Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### Frontend Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Development Commands

#### Backend
```bash
# Run tests
python manage.py test

# Create superuser
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load initial data
python manage.py load_initial_data
```

#### Frontend
```bash
# Run linting
npm run lint

# Build for production
npm run build

# Start production server
npm start
```

## Production Deployment

### Using Docker
```bash
# Build and run in production mode
docker-compose -f docker-compose.prod.yml up --build
```

### Manual Production Setup
1. Set `DEBUG = False` in `settings.py`
2. Configure environment variables
3. Set up PostgreSQL database
4. Configure Cloudinary for file storage
5. Set up Nginx reverse proxy
6. Run `npm run build` for frontend
7. Use Gunicorn for Django deployment

## Support

For issues and questions:
- Check the README.md file
- Review the TODO.md for current status
- Run the test files: `python comprehensive_test.py`
- Check logs in terminal output

## Version Information
- Django: 5.2.7
- Next.js: 16.0.0
- Python: 3.9+
- Node.js: 18+
- PostgreSQL: 13+
