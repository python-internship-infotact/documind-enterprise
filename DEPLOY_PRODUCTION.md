# Production Deployment Guide - DocuMind Enterprise

Follow these instructions to get your project live on **Vercel** (Frontend) and **Render** (Backend).

---

## 🚀 Step 1: Backend Deployment (Render)

1. **GitHub**: Push your code to a GitHub repository.
2. **Render Dashboard**:
   - Go to [dashboard.render.com](https://dashboard.render.com).
   - Click **New +** and select **Blueprint**.
   - Connect your repository. Render will automatically detect `render.yaml`.
   - Alternatively, create a **Web Service** manually:
     - **Environment**: Docker
     - **Dockerfile Path**: `Dockerfile.backend`
     - **Docker Context**: `.` (Root)
3. **Environment Variables**: Add the following safely in the Render dashboard:
   - `GROQ_API_KEY`: Your Groq API key.
   - `PINECONE_API_KEY`: Your Pinecone API key.
   - `PINECONE_ENVIRONMENT`: e.g., `us-east-1`.
   - `PINECONE_INDEX_NAME`: Your index name.
   - `ALLOWED_ORIGINS`: Your Vercel URL (e.g., `https://your-app.vercel.app`).
   - `ENVIRONMENT`: `production`.
4. **Deploy**: Wait for the build to complete. Copy your **Render service URL** (e.g., `https://documind-backend.onrender.com`).

---

## 🎨 Step 2: Frontend Deployment (Vercel)

1. **Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com).
   - Click **Add New...** -> **Project**.
   - Import your GitHub repository.
2. **Project Configuration**:
   - **Root Directory**: Select `frontend`.
   - **Framework Preset**: Vite.
   - **Build Command**: `npm run build` or `vite build`.
   - **Output Directory**: `dist`.
3. **Environment Variables**:
   - Add `VITE_API_BASE_URL`: Paste your **Render service URL** from Step 1.
4. **Deploy**: Click **Deploy**. Vercel will build and host your site.

---

## 🔒 Security & Safety Notes

- **CORS**: I have updated `ai_service/main.py` to allow dynamic origins via the `ALLOWED_ORIGINS` environment variable. Make sure this matches your Vercel URL.
- **SPA Routing**: Added `frontend/vercel.json` to ensure refreshing the page on Vercel doesn't result in a 404 error.
- **Docker**: The backend uses the existing `Dockerfile.backend` to ensure system dependencies (like PDF processing libraries) are correctly installed.

---

## 🛠 Troubleshooting

- **CORS Errors**: Ensure `ALLOWED_ORIGINS` in Render exactly matches your Vercel domain.
- **API Connectivity**: Check the Browser Console (F12) to see if requests are hitting the correct Render URL.
- **Memory Limits**: The embedding model requires ~300MB RAM. If the Render Free tier crashes, you may need to upgrade to the 'Starter' plan.
