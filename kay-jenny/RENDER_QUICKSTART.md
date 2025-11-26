# Render Deployment - Quick Start

## 5-Minute Setup

### Step 1: Push to GitHub
```bash
git add render.yaml .env.example DEPLOYMENT_GUIDE.md
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Go to Render Dashboard
1. Open https://render.com/
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Select your FJC-Pizza repository

### Step 3: Connect Repository
- Repository: `FJC-Pizza` (or your repo name)
- Branch: `main`
- Runtime: `Python 3.11`

### Step 4: Set Build Command
```
pip install -r requirements.txt && python sales_inventory_system/manage.py migrate && python sales_inventory_system/manage.py collectstatic --no-input
```

### Step 5: Set Start Command
```
gunicorn sales_inventory_system.sales_inventory.wsgi:application --bind 0.0.0.0:$PORT
```

### Step 6: Add Environment Variables
Click "Advanced" → "Add Environment Variable"

**Add these 3 required variables:**
1. `DEBUG` = `False`
2. `SECRET_KEY` = (generate via: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
3. `ALLOWED_HOSTS` = `*.onrender.com`

### Step 7: Create PostgreSQL Database
1. On Dashboard, click "New +" → "PostgreSQL"
2. Name: `fjc-pizza-db`
3. PostgreSQL: 15
4. Plan: Free
5. Click "Create Database"

### Step 8: Add DATABASE_URL
1. Copy the "Internal Database URL" from PostgreSQL service
2. Go back to Web Service → Environment
3. Add: `DATABASE_URL` = (paste the URL)

### Step 9: Deploy!
Click "Create Web Service" and wait 5-10 minutes ☕

---

## After Deployment ✅

### Your App is Live!
- URL: `https://<your-service-name>.onrender.com`
- Admin: `https://<your-service-name>.onrender.com/admin/`

### Create Admin User
```bash
# Use Render Shell:
python sales_inventory_system/manage.py createsuperuser
```

### Test Login
- Username: (from createsuperuser)
- Password: (from createsuperuser)

---

## Next Deploys (Super Easy!)
Just push to GitHub and Render automatically:
```bash
git push origin main
```
Done! Render redeploys automatically ✨

---

## Need Help?
See `DEPLOYMENT_GUIDE.md` for:
- Troubleshooting
- Environment variables
- Custom domain setup
- Performance tips

---

**Your app is now deployed to the internet! 🚀**
