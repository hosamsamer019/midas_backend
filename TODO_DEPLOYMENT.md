# Deployment Plan for Smart Antibiogram System

## Overview
Deploy the full-stack application (Django backend + Next.js frontend) to free hosting platforms for testing.

## Hosting Platforms
- **Frontend**: Vercel (free tier, optimized for Next.js)
- **Backend**: Railway (free tier, supports Django/Python)
- **Database**: Supabase (free PostgreSQL database)

## Preparation Steps

### 1. Django Backend Preparation
- [ ] Update settings.py for production environment
- [ ] Create environment variables configuration
- [ ] Configure ALLOWED_HOSTS for Railway domain
- [ ] Set DEBUG=False for production
- [ ] Configure static files for Railway
- [ ] Update CORS settings for Vercel domain

### 2. Frontend Preparation
- [ ] Update API base URLs to production backend
- [ ] Configure Next.js for production build
- [ ] Update CORS origins in Django for Vercel domain

### 3. Database Setup
- [ ] Create Supabase project
- [ ] Configure PostgreSQL connection in Django
- [ ] Run migrations on production database
- [ ] Load initial data

### 4. Deployment Configuration
- [ ] Create Railway deployment configuration
- [ ] Create Vercel deployment configuration
- [ ] Set up environment variables on hosting platforms
- [ ] Configure build commands and settings

### 5. GitHub Repository
- [ ] Create GitHub repository
- [ ] Push project code
- [ ] Set up automatic deployments

### 6. Testing & Verification
- [ ] Test frontend deployment on Vercel
- [ ] Test backend deployment on Railway
- [ ] Verify database connectivity
- [ ] Test API endpoints
- [ ] Test authentication flow
- [ ] Test AI features (if possible on free tier)

## Files to Create/Modify
- `antibiogram/settings.py` - Production configuration
- `frontend/.env.local` - Frontend environment variables
- `railway.toml` - Railway deployment config
- `vercel.json` - Vercel deployment config
- `requirements.txt` - Ensure all dependencies are listed
- `frontend/package.json` - Build scripts

## Environment Variables Needed
### Backend (Railway)
- SECRET_KEY
- DEBUG=False
- DATABASE_URL (from Supabase)
- ALLOWED_HOSTS
- CORS_ALLOWED_ORIGINS
- CLOUDINARY_CREDENTIALS (if using file uploads)

### Frontend (Vercel)
- NEXT_PUBLIC_API_URL (Railway backend URL)
