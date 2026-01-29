# Vercel Deployment Guide

This project is configured for deployment on Vercel with the following setup:

## Prerequisites

1. A Vercel account (https://vercel.com)
2. GitHub repository connected to Vercel
3. The following secrets must be configured in your GitHub repository:
   - `VERCEL_TOKEN` - Your Vercel API token

## Getting Your Vercel Credentials

### 1. Get your Vercel Token
- Go to https://vercel.com/account/tokens
- Create a new token with appropriate permissions
- Add it as `VERCEL_TOKEN` in your GitHub repository secrets

### 2. Get your Organization and Project IDs
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Link your project (run in project root)
vercel link

# This will create a .vercel directory with project.json
# containing your org_id and project_id
cat .vercel/project.json
```

## GitHub Secrets Setup

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `VERCEL_TOKEN`, Value: [your token from step 1]

## Deployment

### Automatic Deployment
- Push to `main` branch triggers automatic deployment
- Pull requests create preview deployments

### Manual Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to production
vercel --prod

# Deploy to preview
vercel
```

## Important Notes

1. **Backend API**: The backend runs as serverless functions on Vercel
2. **Frontend**: Static files served from Vercel's CDN
3. **Data Persistence**: The backend requires a database. Locally it uses SQLite; on Vercel set `DATABASE_URL` to a Postgres instance.
4. **CORS**: Already configured to accept all origins in development. Update for production.

## Environment Variables

### Required Environment Variables (Vercel)
Set the following in Vercel → Project Settings → Environment Variables:

- `DATABASE_URL` (Postgres connection string)

Example:
```
DATABASE_URL=postgres://user:pass@host:5432/dbname
```

### Vercel Postgres (quick setup)
1. In Vercel dashboard, open your project.
2. Go to **Storage** → **Postgres** → **Create**.
3. After creation, Vercel will offer to add environment variables to the project.
4. Ensure `DATABASE_URL` is added to **Production** (and Preview if needed).

## Limitations

Vercel serverless functions have some limitations:
- 10-second execution timeout (Hobby plan)
- No local filesystem persistence between requests
- Use Postgres/SQL storage for persistence (this project relies on `DATABASE_URL`)

## Alternative: Deploy with Docker

If you prefer Docker deployment (e.g., on AWS ECS, Google Cloud Run, or DigitalOcean):

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```
