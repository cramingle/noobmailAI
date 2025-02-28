# NoobMail AI

Email automation platform with AI capabilities.

## Railway Deployment Instructions

This application consists of three services:

1. **Frontend**: SvelteKit application
2. **Main API**: FastAPI service for the main backend
3. **AI Service**: FastAPI service for AI processing

### Deployment Steps

1. Create a new project in Railway
2. Add the following services:

#### Frontend Service
- Connect this GitHub repository
- Set the service name to "frontend"
- Environment variables:
  - `PORT`: 3000
  - `PUBLIC_API_URL`: URL of your API service
  - Other environment variables from `.env.example`

#### API Service
- Connect this GitHub repository
- Set the service name to "api"
- Set the start command to: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `PORT`: 8002
  - Other environment variables from backend configuration

#### AI Service
- Connect this GitHub repository
- Set the service name to "ai-service"
- Set the start command to: `cd backend && python -m uvicorn local_ai_service:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `PORT`: 8001
  - Other environment variables from backend configuration

### Custom Domain Setup

1. In Railway dashboard, go to each service settings
2. Add custom domains for each service:
   - Frontend: yourdomain.com
   - API: api.yourdomain.com
   - AI Service: ai.yourdomain.com

### Environment Variables

Make sure to set all required environment variables for each service based on your `.env.example` files. 