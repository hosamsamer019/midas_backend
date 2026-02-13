# Smart Antibiogram System - Deployment Guide

## Prerequisites
- GitHub account
- Supabase account (https://supabase.com)
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)

## Step 1: GitHub Repository ✅ COMPLETED
- Repository: https://github.com/hosamsamerserver-dotcom/Data_Analysis_Project
- Code is already pushed and up-to-date

## Step 2: Set up Supabase Database

### 2.1 Create Supabase Project
1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in project details:
   - Name: `smart-antibiogram-db`
   - Database Password: Choose a strong password
   - Region: Select closest to your users
4. Click "Create new project"
5. Wait for project to be fully provisioned (5-10 minutes)

### 2.2 Get Database Connection Details
1. In your Supabase dashboard, go to Settings → Database
2. Copy the "Connection string" (it should look like: `postgresql://postgres:[password]@[host]:5432/postgres`)
3. Note down the connection string - you'll need it for Railway

## Step 3: Deploy Backend on Railway

### 3.1 Create Railway Project
1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Search for and select `Data_Analysis_Project`
6. Click "Deploy"

### 3.2 Configure Environment Variables
1. In Railway dashboard, go to your project
2. Click on "Variables" tab
3. Add the following variables:

```
SECRET_KEY=your-django-secret-key-here
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres  # From Supabase
DEBUG=False
ALLOWED_HOSTS=https://your-app-name.railway.app
CORS_ALLOWED_ORIGINS=https://your-app-name.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.vercel.app
```

**Note:** Replace the placeholder domains with actual domains once deployed.

### 3.3 Deploy Backend
1. Railway should automatically start building and deploying
2. Wait for deployment to complete
3. Note down the Railway domain (e.g., `https://your-app-name.railway.app`)

## Step 4: Deploy Frontend on Vercel

### 4.1 Create Vercel Project
1. Go to https://vercel.com and sign in
2. Click "New Project"
3. Import your GitHub repository `Data_Analysis_Project`
4. Configure project settings:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### 4.2 Configure Environment Variables
1. In Vercel project settings, go to "Environment Variables"
2. Add the following variable:

```
NEXT_PUBLIC_API_URL=https://your-app-name.railway.app
```

**Note:** Replace with your actual Railway domain.

### 4.3 Deploy Frontend
1. Click "Deploy"
2. Wait for deployment to complete
3. Note down the Vercel domain (e.g., `https://your-app-name.vercel.app`)

## Step 5: Configure CORS and Update Domains

### 5.1 Update Django Settings
1. In your local `antibiogram/settings.py`, update the CORS settings with actual domains:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://your-app-name.vercel.app",  # Replace with actual Vercel domain
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://your-app-name.vercel.app",  # Replace with actual Vercel domain
]
```

2. Commit and push these changes to GitHub
3. Railway will automatically redeploy with the updated settings

### 5.2 Update Railway Environment Variables
1. Go back to Railway dashboard
2. Update the `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` with actual domains
3. Railway will redeploy automatically

## Step 6: Database Migration

### 6.1 Run Migrations on Production
1. In Railway dashboard, go to your project
2. Open the Railway CLI or use the web terminal
3. Run the following commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

## Step 7: Testing & Verification

### 7.1 Test Frontend
- Visit your Vercel domain
- Check if the app loads without errors
- Test basic navigation

### 7.2 Test Backend API
- Visit `https://your-railway-domain/api/` (should show API root)
- Test authentication endpoints
- Test data endpoints

### 7.3 Test Full Integration
- Try logging in/registering
- Upload data files
- Generate reports
- Test chatbot functionality

## Troubleshooting

### Common Issues:
1. **CORS Errors**: Double-check CORS_ALLOWED_ORIGINS in Django settings and Railway env vars
2. **Database Connection**: Verify DATABASE_URL in Railway is correct
3. **Static Files**: Ensure collectstatic ran successfully
4. **Environment Variables**: Make sure all required env vars are set

### Logs:
- Check Railway logs for backend errors
- Check Vercel deployment logs for frontend build errors
- Check Supabase logs for database issues

## Security Notes
- Never commit secrets to GitHub
- Use strong passwords for database
- Keep Django SECRET_KEY secure
- Regularly update dependencies

## Cost Estimation (Free Tiers)
- Supabase: Free up to certain limits
- Railway: $5/month after trial
- Vercel: Free for personal projects

---

**Next Steps:** Follow this guide step by step. Let me know if you encounter any issues at each step, and I'll help you troubleshoot.
