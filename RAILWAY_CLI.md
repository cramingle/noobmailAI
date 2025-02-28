# Railway CLI Deployment Guide for NoobMail AI

This guide provides step-by-step instructions for deploying NoobMail AI using the Railway CLI.

## Prerequisites

- Railway account (sign up at [railway.app](https://railway.app))
- Railway CLI installed (`npm install -g @railway/cli`)
- Node.js 18 or higher
- Git

## Deployment Steps

### 1. Login to Railway

```bash
railway login --browserless
```

Follow the instructions to complete the login process.

### 2. Initialize Your Project

```bash
railway init
```

Enter a project name when prompted.

### 3. Deploy Your Services

Since your account is on a limited plan, you'll need to deploy through the Railway dashboard:

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Select your project
3. Click "New Service" → "GitHub Repo"
4. Connect your GitHub repository
5. Configure each service as described below

### 4. Configure Services in Dashboard

#### Frontend Service
- Name: "frontend"
- Root Directory: "/"
- Build Command: `cd frontend && npm install && npm run build`
- Start Command: `cd frontend && npm run preview -- --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `PORT`: 3000
  - `PUBLIC_API_URL`: URL of your API service

#### API Service
- Name: "api"
- Root Directory: "/"
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `PORT`: 8002

#### AI Service
- Name: "ai-service"
- Root Directory: "/"
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && python -m uvicorn local_ai_service:app --host 0.0.0.0 --port $PORT`
- Environment Variables:
  - `PORT`: 8001

### 5. Link Local Project to Railway Services (Optional)

After creating services in the dashboard, you can link your local project to them:

```bash
# Link to frontend service
railway service frontend

# Link to API service
railway service api

# Link to AI service
railway service ai-service
```

### 6. Set Environment Variables

```bash
# For frontend service
railway variables set PORT=3000 PUBLIC_API_URL=https://your-api-url.railway.app

# For API service
railway variables set PORT=8002

# For AI service
railway variables set PORT=8001
```

### 7. Monitor Your Deployment

```bash
railway status
railway logs
```

## Upgrading Your Plan

To unlock all Railway CLI features, consider upgrading your plan at [railway.app/account/plans](https://railway.app/account/plans).

## Troubleshooting

- If you encounter deployment issues, check the logs using `railway logs`
- For service-specific issues, use `railway logs --service <service-name>`
- For more help, visit [docs.railway.app](https://docs.railway.app) 