# Vercel Postgres Setup Guide

This guide will help you set up persistent storage for your Agent Load Balancer on Vercel.

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Postgres Database on Vercel

1. Go to your Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: `solvers-one` (or your project name)
3. Click on the **Storage** tab
4. Click **Create Database**
5. Select **Postgres**
6. Choose a database name (e.g., `solvers-db`)
7. Select a region (choose closest to your users)
8. Click **Create**

### Step 2: Connect Database to Project

Vercel will automatically:
- Create the Postgres database
- Add environment variables to your project:
  - `POSTGRES_URL`
  - `POSTGRES_PRISMA_URL`
  - `POSTGRES_URL_NON_POOLING`
  - `POSTGRES_USER`
  - `POSTGRES_HOST`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DATABASE`

### Step 3: Verify Environment Variables

1. Go to **Settings** → **Environment Variables**
2. Verify that `POSTGRES_URL` exists
3. The app will automatically use it (no code changes needed!)

### Step 4: Redeploy

Push any commit to trigger a redeploy:

```bash
git add .
git commit -m "Add Vercel Postgres setup guide" --allow-empty
git push
```

Or manually redeploy from Vercel Dashboard:
- Go to **Deployments**
- Click on the latest deployment
- Click **Redeploy**

---

## ✅ How It Works

The application automatically detects the database:

1. **On Vercel (with Postgres)**:
   - Uses `POSTGRES_URL` environment variable
   - All data persists across deployments
   - Multiple serverless functions share the same database

2. **On Vercel (without Postgres)**:
   - Falls back to in-memory SQLite
   - **Data is lost** between function invocations
   - ⚠️ You'll see agents disappear after refresh

3. **Locally**:
   - Uses `DATABASE_URL` or defaults to `sqlite:///./data/data.db`
   - Data persists in `backend/data/data.db` file

---

## 🔍 Testing After Setup

### Test Persistence:

1. Open https://solvers-one.vercel.app
2. Create an agent (e.g., "Agent Smith")
3. **Refresh the page** → Agent should still be there! ✅
4. Create a request
5. **Refresh again** → Everything should persist! ✅

### If agents disappear:
- ❌ Postgres is not set up yet
- Check environment variables in Vercel Dashboard
- Make sure `POSTGRES_URL` or `POSTGRES_PRISMA_URL` exists
- Redeploy after adding the database

---

## 💰 Pricing

**Vercel Postgres:**
- **Free tier**: Up to 256 MB storage, 60 hours compute/month
- **Perfect for development and small apps**
- Upgrade only if you need more

**Alternative: External Postgres**

If you prefer, use any external Postgres provider:
1. [Neon](https://neon.tech) - Free tier available
2. [Supabase](https://supabase.com) - Free tier available
3. [Railway](https://railway.app) - $5/month
4. AWS RDS, Google Cloud SQL, etc.

Then add the connection URL as `DATABASE_URL` in Vercel Environment Variables.

---

## 🐛 Troubleshooting

### Problem: Agents disappear after refresh

**Solution**: Add Vercel Postgres (see Step 1)

### Problem: "No DATABASE_URL" error

**Solution**: 
1. Make sure you created the Postgres database in Vercel
2. Check **Settings** → **Environment Variables**
3. Add manually if missing: `POSTGRES_URL=postgres://...`

### Problem: Connection errors

**Solution**:
1. Check the connection string is valid
2. Make sure your Vercel project is in the same region as the database
3. Check Vercel function logs for detailed errors

### Problem: Database tables not created

**Solution**: The app automatically creates tables on startup. If issues persist:
1. Check Vercel function logs
2. Manually connect to the database and verify tables exist
3. Run migrations if needed

---

## 📊 Database Schema

The app uses these tables:

### `agents`
- `id` (String, Primary Key)
- `name` (String)
- `max_requests` (Integer, default: 2)

### `requests`
- `id` (String, Primary Key)
- `customer_name` (String)
- `description` (String)
- `assigned_agent_id` (String, Foreign Key → agents.id)
- `status` (String: "pending", "processing", "completed")
- `created_at` (DateTime)
- `completed_at` (DateTime, nullable)

---

## ✨ Benefits of Vercel Postgres

✅ **Automatic connection pooling** - Handles serverless connections efficiently  
✅ **Built-in backups** - Your data is safe  
✅ **Fast queries** - Same region as your Vercel functions  
✅ **Easy scaling** - Upgrade plan as you grow  
✅ **Free tier** - Perfect for getting started  

---

## 🎯 Summary

1. ✅ Create Postgres in Vercel Dashboard → Storage → Create Database
2. ✅ Vercel auto-adds `POSTGRES_URL` environment variable
3. ✅ Push a commit to trigger redeploy
4. ✅ Test by creating agents and refreshing page
5. ✅ Agents should persist! 🎉

Need help? Check the logs in Vercel Dashboard → Deployments → Function Logs
