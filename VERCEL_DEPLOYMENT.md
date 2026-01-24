# Vercel Deployment Guide

This project is configured for deployment on Vercel with the following setup:

## Prerequisites

1. A Vercel account (https://vercel.com)
2. GitHub repository connected to Vercel
3. The following secrets configured in your GitHub repository:
   - `VERCEL_TOKEN` - Your Vercel API token
   - `VERCEL_ORG_ID` - Your Vercel organization ID
   - `VERCEL_PROJECT_ID` - Your Vercel project ID

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
   - Name: `VERCEL_ORG_ID`, Value: [from .vercel/project.json]
   - Name: `VERCEL_PROJECT_ID`, Value: [from .vercel/project.json]

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
3. **Data Persistence**: The current implementation uses in-memory storage. For production, integrate a database (e.g., Vercel Postgres, MongoDB Atlas)
4. **CORS**: Already configured to accept all origins in development. Update for production.

## Environment Variables

You can set additional environment variables in Vercel dashboard:
- Go to Project Settings → Environment Variables
- Add any custom variables your app needs

## Limitations

Vercel serverless functions have some limitations:
- 10-second execution timeout (Hobby plan)
- No persistent storage between requests
- Consider using Vercel KV or external database for production

## Alternative: Deploy with Docker

If you prefer Docker deployment (e.g., on AWS ECS, Google Cloud Run, or DigitalOcean):

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```
