# Domestic Solar & Battery Management System (BMS) Deployment Guide

This application is ready for deployment on **Render** (FastAPI Backend / Full-stack) and **Cloudflare Pages** (Static Edge CDN Frontend).

---

## Deployment Option A: Full-Stack Deployment on Render (Simplest)

Deploying both the API and Web Dashboard together on Render.

1. **Push your code to GitHub / GitLab**.
2. **Log in to Render** ([dashboard.render.com](https://dashboard.render.com)).
3. Click **New +** -> **Web Service**.
4. Connect your repository.
5. Configure the service settings:
   - **Name**: `bms-engine` (or custom name)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/healthz`
6. Click **Create Web Service**.
7. Once deployed, your site will be live at `https://bms-engine.onrender.com`!

---

## Deployment Option B: Split Architecture (Render API + Cloudflare Pages Frontend)

Hosting the dynamic Python backend engine on Render and serving the UI at edge speeds via Cloudflare Pages.

### Step 1: Deploy Backend API on Render
1. Follow Deployment Option A above to launch the FastAPI backend on Render.
2. Note down your backend URL (e.g. `https://bms-engine.onrender.com`).

### Step 2: Configure Cloudflare Pages
1. Open the `_redirects` file in your repository.
2. Replace `YOUR-RENDER-APP-NAME` with your actual Render URL:
   ```text
   /api/*  https://bms-engine.onrender.com/api/:splat  200!
   ```
3. Log in to **Cloudflare Dashboard** -> **Workers & Pages** -> **Create application** -> **Pages**.
4. Connect your GitHub repository.
5. Set Build settings:
   - **Framework preset**: `None`
   - **Build output directory**: `templates` (or root if serving directly)
6. Click **Save and Deploy**.

Now, Cloudflare Pages will serve your UI across global edge nodes, and automatically proxy `/api/v1/simulate` calls to your Render backend with zero CORS issues!

---

## Code Features & Fixes for Production Deployment

- **CORS Enabled**: `CORSMiddleware` configured in `app/main.py` allowing cross-origin requests from Cloudflare domain.
- **Dynamic JS API Resolution**: `getApiEndpoint()` dynamically routes requests without hardcoded URLs.
- **Health Check Endpoint**: `/healthz` added for Render uptime monitoring.
- **Port Binding**: Standard `--port $PORT` binding for containerized cloud deployment.
