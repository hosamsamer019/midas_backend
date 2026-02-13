# Deployment Steps for Smart Antibiogram System

## Completed
- [x] Install GitHub CLI
- [x] Update settings.py for production CORS
- [x] Commit and push code to GitHub

## Pending Steps

### 1. Set up Supabase Database
- [ ] Create Supabase project at https://supabase.com
- [ ] Get database URL and credentials
- [ ] Update environment variables with Supabase connection

### 2. Deploy Backend on Railway
- [ ] Create Railway account at https://railway.app
- [ ] Connect GitHub repository to Railway
- [ ] Set environment variables on Railway:
  - SECRET_KEY
  - DATABASE_URL (from Supabase)
  - DEBUG=False
  - ALLOWED_HOSTS (Railway domain)
  - CORS_ALLOWED_ORIGINS (Vercel domain)
  - CSRF_TRUSTED_ORIGINS (Vercel domain)
- [ ] Deploy backend

### 3. Deploy Frontend on Vercel
- [ ] Create Vercel account at https://vercel.com
- [ ] Connect GitHub repository to Vercel
- [ ] Set environment variables on Vercel:
  - NEXT_PUBLIC_API_URL (Railway backend URL)
- [ ] Deploy frontend

### 4. Configure CORS and Environment Variables
- [ ] Update CORS_ALLOWED_ORIGINS in settings.py with actual Vercel domain
- [ ] Update CSRF_TRUSTED_ORIGINS in settings.py with actual Vercel domain
- [ ] Test API connectivity between frontend and backend
- [ ] Verify authentication flow works in production

### 5. Testing & Verification
- [ ] Test frontend deployment
- [ ] Test backend deployment
- [ ] Verify database connectivity
- [ ] Test API endpoints
- [ ] Test authentication
- [ ] Test AI features (if possible on free tier)

## Environment Variables Summary

### Backend (Railway)
- SECRET_KEY: Django secret key
- DATABASE_URL: postgresql://[user]:[password]@[host]:[port]/[database]
- DEBUG: False
- ALLOWED_HOSTS: your-app.railway.app
- CORS_ALLOWED_ORIGINS: https://your-app.vercel.app
- CSRF_TRUSTED_ORIGINS: https://your-app.vercel.app

### Frontend (Vercel)
- NEXT_PUBLIC_API_URL: https://your-app.railway.app

## Notes
- Replace placeholder domains with actual deployed domains
- Ensure all environment variables are set correctly
- Test thoroughly after each deployment step
