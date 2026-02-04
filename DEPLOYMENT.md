# DocuMind Enterprise - Deployment Guide

This guide covers deploying DocuMind Enterprise to production using Render (backend) and Vercel (frontend).

## Prerequisites

Before deploying, ensure you have:

1. **API Keys**:
   - Groq API key for LLM functionality
   - Pinecone API key for vector database

2. **Accounts**:
   - [Render](https://render.com) account for backend deployment
   - [Vercel](https://vercel.com) account for frontend deployment
   - GitHub repository with your code

## Backend Deployment (Render)

### 1. Prepare Your Repository

Ensure your repository contains:
- `render.yaml` (already created)
- `ai_service/requirements.txt` with all dependencies
- Updated CORS configuration in `ai_service/main.py`

### 2. Deploy to Render

1. **Connect Repository**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

2. **Configure Environment Variables**:
   - In the Render dashboard, go to your service settings
   - Add the following environment variables:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     PINECONE_API_KEY=your_pinecone_api_key_here
     ```

3. **Deploy**:
   - Render will automatically build and deploy your backend
   - Your backend will be available at: `https://documind-backend.onrender.com`
   - Health check endpoint: `https://documind-backend.onrender.com/health`

### 3. Verify Backend Deployment

Test your backend deployment:
```bash
curl https://documind-backend.onrender.com/health
```

You should receive a JSON response indicating the service is healthy.

## Frontend Deployment (Vercel)

### 1. Update Configuration

The following files have been configured for Vercel deployment:
- `vercel.json` - Vercel deployment configuration
- `frontend/.env.production` - Production environment variables
- Updated `frontend/vite.config.ts` - Build configuration
- Updated `frontend/src/hooks/useConversation.ts` - API URL configuration

### 2. Deploy to Vercel

#### Option A: Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel --prod
   ```

#### Option B: Vercel Dashboard

1. **Connect Repository**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

2. **Configure Build Settings**:
   - Framework Preset: Vite
   - Build Command: `cd frontend && npm ci && npm run build:prod`
   - Output Directory: `frontend/dist`
   - Install Command: `cd frontend && npm ci`

3. **Environment Variables**:
   - Add: `VITE_API_BASE_URL=https://documind-backend.onrender.com`
   - (Replace with your actual Render backend URL)

4. **Deploy**:
   - Click "Deploy"
   - Your frontend will be available at: `https://your-project.vercel.app`

### 3. Update Backend CORS

After deploying to Vercel, update your backend's CORS configuration:

1. Note your Vercel deployment URL (e.g., `https://documind-frontend.vercel.app`)
2. The backend is already configured to accept Vercel URLs in the CORS settings

## Post-Deployment Configuration

### 1. Update Frontend API URL

If your Render backend URL is different from `https://documind-backend.onrender.com`:

1. Update `frontend/.env.production`:
   ```
   VITE_API_BASE_URL=https://your-actual-backend-url.onrender.com
   ```

2. Update `vercel.json`:
   ```json
   {
     "env": {
       "VITE_API_BASE_URL": "https://your-actual-backend-url.onrender.com"
     }
   }
   ```

3. Redeploy the frontend

### 2. Custom Domain (Optional)

#### For Render (Backend):
1. Go to your service settings in Render
2. Add a custom domain under "Custom Domains"
3. Update DNS records as instructed

#### For Vercel (Frontend):
1. Go to your project settings in Vercel
2. Add a custom domain under "Domains"
3. Update DNS records as instructed

## Environment Variables Reference

### Backend (Render)
```
ENVIRONMENT=production
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=documind-hf
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50
```

### Frontend (Vercel)
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

## Monitoring and Maintenance

### Health Checks

Both services include health check endpoints:
- Backend: `https://your-backend.onrender.com/health`
- Frontend: Vercel automatically monitors your deployment

### Logs

- **Render**: View logs in the Render dashboard under your service
- **Vercel**: View function logs and analytics in the Vercel dashboard

### Scaling

- **Render**: Upgrade to paid plans for auto-scaling and better performance
- **Vercel**: Automatically scales based on traffic

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure your Vercel URL is added to the backend CORS configuration
   - Check that the API URL in frontend matches your backend URL

2. **Build Failures**:
   - Check that all dependencies are listed in `package.json` and `requirements.txt`
   - Verify environment variables are set correctly

3. **API Connection Issues**:
   - Verify the backend is deployed and healthy
   - Check the API URL configuration in the frontend

### Getting Help

- Check service logs in respective dashboards
- Verify environment variables are set correctly
- Test API endpoints directly using curl or Postman

## Security Considerations

1. **Environment Variables**: Never commit API keys to your repository
2. **CORS**: The backend is configured with specific allowed origins for security
3. **HTTPS**: Both Render and Vercel provide HTTPS by default
4. **Headers**: Security headers are configured in `vercel.json`

## Cost Optimization

- **Render**: Free tier available with limitations; paid plans for production workloads
- **Vercel**: Generous free tier for personal projects; paid plans for teams and high traffic

Both platforms offer usage-based pricing, so costs scale with your application's usage.