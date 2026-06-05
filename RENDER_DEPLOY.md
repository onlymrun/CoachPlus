# CoachPlus — Render Deployment Guide

Deploy all three CoachPlus services on [Render](https://render.com). The backend and AI service deploy together via Blueprint; the frontend is a manual Static Site.

---

## Step 1: Deploy Backend + AI Service (Blueprint)

Render Blueprint reads `render.yaml` from the repo root to deploy multiple services together.

1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repo (`onlymrun/CoachPlus`)
4. Render will detect `render.yaml` and show two services:
   - **coachplus-ai** — AI analysis engine
   - **coachplus-api** — FastAPI backend
5. Click **"Apply"**

Render will deploy both services and auto-wire the `ANALYSIS_SERVICE_URL` env var on the backend to point at the AI service.

**Optional:** Set `OPENAI_API_KEY` in the coachplus-ai service environment for real AI analysis (mock mode works without it).

---

## Step 2: Deploy Frontend (Manual Static Site)

The frontend is a React SPA that must be deployed manually as a Render Static Site (Render Blueprint does not support `type: static_site`).

1. Go to https://dashboard.render.com/static
2. Click **"New Static Site"**
3. Connect your GitHub repo (`onlymrun/CoachPlus`)
4. Configure:

   | Field | Value |
   |-------|-------|
   | **Name** | `coachplus-frontend` |
   | **Root Directory** | `frontend` |
   | **Build Command** | `npm run build` |
   | **Publish Directory** | `dist` |

5. Add environment variable:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://coachplus-api.onrender.com` (or your deployed backend URL) |

6. Click **"Deploy"**

Render will build and deploy the frontend. The site will be available at a URL like `https://coachplus-frontend.onrender.com`.

---

## Deploy Order Summary

| Order | Service | Method | URL Env Var |
|-------|---------|--------|-------------|
| 1st | **coachplus-ai** | Blueprint (auto) | — |
| 2nd | **coachplus-api** | Blueprint (auto) | `ANALYSIS_SERVICE_URL` → auto-wired |
| 3rd | **coachplus-frontend** | Manual Static Site | `VITE_API_URL` → set to backend URL |

---

## Verifying the Deployment

1. **AI Service:** Visit `https://coachplus-ai.onrender.com/health` → should return `{"status": "healthy"}`
2. **Backend API:** Visit `https://coachplus-api.onrender.com/api/health` → should return `{"status": "healthy"}`
3. **Frontend:** Visit your frontend URL → should show the CoachPlus login page
4. **Full flow:** Register an account → add a client → add session notes → trigger AI analysis → view insights

---

## Troubleshooting

- **Backend can't reach AI service:** Check `ANALYSIS_SERVICE_URL` env var on backend — should point to `https://coachplus-ai.onrender.com/analyze`
- **Frontend can't reach backend:** Check `VITE_API_URL` env var on frontend — should point to `https://coachplus-api.onrender.com`
- **Build fails:** Check Render build logs. Common issues: missing `package-lock.json`, wrong Node version