# FJC-Pizza Hosting Guide on Render

A step-by-step guide for deploying your Django application to Render. This is your first deployment, so follow each step carefully!

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Step 1: Create a Render Account](#step-1-create-a-render-account)
3. [Step 2: Create a PostgreSQL Database](#step-2-create-a-postgresql-database)
4. [Step 3: Configure Your GitHub Repository](#step-3-configure-your-github-repository)
5. [Step 4: Create a Web Service on Render](#step-4-create-a-web-service-on-render)
6. [Step 5: Add Environment Variables](#step-5-add-environment-variables)
7. [Step 6: Deploy Your Application](#step-6-deploy-your-application)
8. [Step 7: Verify Your Deployment](#step-7-verify-your-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Post-Deployment](#post-deployment)

---

## Prerequisites

Before starting, make sure you have:
- ✅ A GitHub account with your project pushed to a repository
- ✅ A Render account (free tier available)
- ✅ All code committed and pushed to GitHub
- ✅ A `requirements.txt` file with all dependencies
- ✅ A `render.yaml` file (already in your project)

**Check if everything is committed:**
```bash
cd C:\Users\Administrator\Desktop\projects\FJC-Pizza
git status  # Should show no uncommitted changes
git push    # Push any pending changes to GitHub
```

---

## Step 1: Create a Render Account

1. Go to [https://render.com](https://render.com)
2. Click **Sign Up**
3. Choose "Sign up with GitHub" (easier for deployments)
4. Authorize Render to access your GitHub account
5. Verify your email address

---

## Step 2: Create a PostgreSQL Database

### Why PostgreSQL?
Render requires a managed PostgreSQL database for your Django app to store data.

### Creating the Database:

1. **Log in to Render** and go to your dashboard
2. **Click "New" button** in the top-left → select **PostgreSQL**
3. **Fill in the details:**
   - **Name**: `fcj-pizza-db` (any name you prefer)
   - **Database**: `fcj_pizza_q4rm` (or the name from your credentials)
   - **User**: `fcj_pizza_q4rm_user` (or from your credentials)
   - **Region**: Choose the one closest to your users (e.g., **Oregon** for US West)
   - **PostgreSQL Version**: **18** (latest stable)
   - **Plan**: **Free** (for testing)

4. **Click "Create Database"**
5. **Wait 2-3 minutes** for the database to be created

### Copying Your Database Credentials:

Once created, Render will show you your database credentials:
- **Hostname** (internal and external)
- **Port** (usually 5432)
- **Database name**
- **Username**
- **Password**
- **Database URLs** (Internal and External)

**IMPORTANT:** Copy the **External Database URL** - this is what your web service will use.

Example:
```
postgresql://fcj_pizza_q4rm_user:r06v85uYsqN6DmOMjV2fA3lSOy9VXIqJ@dpg-d4h8qcf5r7bs73bmppsg-a.oregon-postgres.render.com/fcj_pizza_q4rm
```

---

## Step 3: Configure Your GitHub Repository

Your project must be pushed to GitHub for Render to deploy it.

```bash
cd C:\Users\Administrator\Desktop\projects\FJC-Pizza

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit for Render deployment"

# Push to GitHub
git push -u origin main
```

---

## Step 4: Create a Web Service on Render

### Step 4a: Connect Your GitHub Repository

1. **Go to Render Dashboard**
2. **Click "New" button** → Select **Web Service**
3. **Connect to GitHub:**
   - Click "Connect account" if not already connected
   - Search for your `FJC-Pizza` repository
   - Click "Connect"

### Step 4b: Configure the Web Service

Fill in the following details:

| Field | Value |
|-------|-------|
| **Name** | `fjc-pizza-app` |
| **Environment** | `Python 3` |
| **Region** | Same as your database (e.g., Oregon) |
| **Branch** | `main` |
| **Build Command** | *(will auto-fill, leave as is)* |
| **Start Command** | *(will auto-fill, leave as is)* |
| **Plan** | **Free** (for testing) |

4. **Scroll down** - Don't add environment variables yet, we'll do that in the next step
5. **Click "Create Web Service"**

---

## Step 5: Add Environment Variables

Now you need to tell Render how to connect to your database and configure Django.

### On Render Dashboard:

1. **Go to your web service** (`fjc-pizza-app`)
2. **Go to the "Environment" tab** on the left sidebar
3. **Click "Add Environment Variable"** and add these variables:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your External Database URL from Step 2 |
| `DEBUG` | `False` |
| `SECRET_KEY` | Generate a strong key (see below) |
| `ALLOWED_HOSTS` | `*.onrender.com` |
| `PYTHONUNBUFFERED` | `1` |

### Generating a SECRET_KEY:

Run this in your terminal:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as your `SECRET_KEY` value.

### Complete Example:

```
DATABASE_URL = postgresql://fcj_pizza_q4rm_user:r06v85uYsqN6DmOMjV2fA3lSOy9VXIqJ@dpg-d4h8qcf5r7bs73bmppsg-a.oregon-postgres.render.com/fcj_pizza_q4rm
DEBUG = False
SECRET_KEY = your-generated-key-here
ALLOWED_HOSTS = *.onrender.com
PYTHONUNBUFFERED = 1
```

**After adding all variables, click "Save"**

---

## Step 6: Deploy Your Application

### Automatic Deployment (Recommended)

Render automatically deploys when you push to GitHub:

1. **Make any final changes locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Final changes before deployment"
   git push
   ```
3. **Render automatically starts deploying** (watch the dashboard)

### Manual Deployment

If you need to redeploy manually:
1. Go to your service on Render
2. Click the **"Manual Deploy"** button
3. Select **"Deploy latest commit"**

---

## Step 7: Verify Your Deployment

### Watch the Deployment Logs:

1. **Go to your web service** (`fjc-pizza-app`)
2. **Click the "Logs" tab**
3. **Watch for these messages:**
   - ✅ `Build started`
   - ✅ `pip install -r requirements.txt` (installing packages)
   - ✅ `python manage.py migrate` (running migrations)
   - ✅ `python manage.py collectstatic` (collecting static files)
   - ✅ `Build successful!`
   - ✅ `Listening on port 10000` (app is running)

### Test Your Deployment:

Once the build is complete:

1. **Click the URL at the top** of your service page (looks like `https://fjc-pizza-app.onrender.com`)
2. **You should see your application loading**
3. **Test key pages:**
   - Home page: `/`
   - Admin panel: `/admin/` (login with your superuser account)
   - Other app pages

### If You Get a 404 Error:

This is normal! Add `/admin/` to the URL to access the admin panel:
```
https://fjc-pizza-app.onrender.com/admin/
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. **Build Fails - FileNotFoundError**

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'logs/queries.log'`

**Solution:** ✅ Already fixed in your code! The logging configuration now uses console-only logging.

---

#### 2. **Build Fails - Missing Dependencies**

**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
1. Add the missing package to `requirements.txt`
2. Push to GitHub
3. Render will automatically redeploy

---

#### 3. **Database Connection Error**

**Error:** `OperationalError: could not connect to server`

**Solution:**
1. Check the `DATABASE_URL` in Environment Variables
2. Verify the database is still running on Render
3. Check that the database credentials match exactly

---

#### 4. **Static Files Not Loading (CSS/Images Broken)**

**Error:** Pages load but styling is missing

**Solution:**
1. This usually happens if `collectstatic` failed
2. Check the logs for errors
3. Make sure `STATIC_ROOT` is configured correctly in `settings.py`

---

#### 5. **502 Bad Gateway Error**

**Error:** "The server is temporarily unable to service your request"

**Solution:**
1. Check the logs - the app likely crashed during startup
2. Look for Python errors in the logs
3. Verify all environment variables are set
4. Check that migrations ran successfully

---

### Viewing Logs for Debugging

**To see what went wrong:**

1. Go to your service on Render
2. Click the **"Logs"** tab
3. Read from bottom to top to see the error messages
4. Common places to look:
   - During build phase
   - During migration phase
   - During startup phase

---

## Post-Deployment

### Create a Superuser (Admin Account)

If you need to access `/admin/`, you must create a superuser account on Render:

1. Go to your service on Render
2. Click the **"Shell"** tab (or use "One-off job")
3. Run:
   ```bash
   python sales_inventory_system/manage.py createsuperuser
   ```
4. Follow the prompts to create an admin account

### Making Updates After Deployment

**The workflow is simple:**

1. Make changes to your code locally
2. Test locally:
   ```bash
   cd sales_inventory_system
   python manage.py runserver
   ```
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
4. Render automatically deploys within 1-2 minutes

### Database Migrations

If you modify your Django models:

1. Create migration locally:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
2. Commit and push
3. Render will automatically run `python manage.py migrate` during build

### Environment Variable Changes

If you need to change any environment variables:

1. Go to your service
2. Go to **Environment** tab
3. Edit the variable
4. Click **"Save"**
5. Render will **automatically redeploy**

---

## Monitoring Your Application

### View Metrics

1. Go to your service on Render
2. Click the **"Metrics"** tab
3. Monitor:
   - CPU usage
   - Memory usage
   - Requests per second
   - Error rates

### Check Status

- **Green light** = App is running normally
- **Yellow light** = App is building/deploying
- **Red light** = App crashed or has an error

---

## Scaling Up (Later)

When you're ready to move beyond the free tier:

1. Go to your service
2. Go to **Settings** tab
3. Click **"Change Plan"**
4. Choose a paid plan (Starter, Standard, etc.)
5. Your app will redeploy with more resources

---

## Important Notes

⚠️ **Free Tier Limitations:**
- 0.5 GB RAM (limited)
- Spins down after 15 minutes of inactivity (takes ~5 seconds to wake up)
- Good for testing, not for production

✅ **Best Practices:**
- Always test locally before pushing to GitHub
- Keep your `SECRET_KEY` safe - never share it
- Use strong database passwords
- Set `DEBUG = False` in production
- Monitor your logs regularly

📧 **Support:**
- Render documentation: https://render.com/docs
- Django deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

## Quick Checklist

Before deploying, verify:

- [ ] All code is committed to GitHub
- [ ] `requirements.txt` has all dependencies
- [ ] `render.yaml` exists in root directory
- [ ] Database is created on Render
- [ ] All environment variables are set on Render
- [ ] `DEBUG = False` in production settings
- [ ] `ALLOWED_HOSTS` includes Render domain
- [ ] No hardcoded secrets in code
- [ ] Static files configuration is correct

---

## Example Deployment Commands

```bash
# Check status before deployment
cd C:\Users\Administrator\Desktop\projects\FJC-Pizza
git status

# Push to GitHub
git push

# Then go to Render dashboard and watch deployment in Logs tab
```

---

**Good luck with your deployment! 🚀**

If you hit any issues, check the Logs tab first - it usually has the answer!
