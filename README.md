# CoachPlus — AI-Powered Coaching Insights

An AI-powered analytics platform for life coaches. Transforms raw session notes into actionable intelligence — automatically tracking client goal progress, surfacing emotional patterns and risks, and generating ready-to-use session prep summaries.

## Architecture

```
coachplus/
├── backend/          # Python FastAPI REST API (port 8000)
│   ├── routers/      # Auth, clients, sessions endpoints
│   ├── models.py     # SQLAlchemy models
│   ├── auth.py       # JWT authentication
│   └── main.py       # App entry point
├── frontend/         # Vite + React SPA (port 5173)
│   └── src/
│       ├── pages/    # Login, Dashboard, Clients, Sessions
│       └── context/  # Auth context (JWT management)
└── ai-service/       # AI Analysis Engine (port 8080)
    └── app/
        ├── main.py       # FastAPI service
        ├── analyzer.py   # OpenAI-powered analysis
        └── models.py     # Request/response schemas
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) OpenAI API key — set `OPENAI_API_KEY` for real AI analysis

### 1. Start the AI Service
```bash
cd ai-service
export OPENAI_API_KEY=sk-your-key-here  # Optional: enables real AI analysis
./start.sh
# Runs on http://localhost:8080
```

### 2. Start the Backend API
```bash
cd backend
export ANALYSIS_SERVICE_URL=http://localhost:8080/analyze
./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# Runs on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/auth/register` | Register coach account |
| POST | `/api/auth/login` | Login, returns JWT |
| GET | `/api/auth/me` | Current user profile |
| GET/POST | `/api/clients` | List / Create clients |
| GET/PUT/DELETE | `/api/clients/:id` | Client CRUD |
| GET/POST | `/api/sessions` | List / Create sessions |
| GET/PUT/DELETE | `/api/sessions/:id` | Session CRUD |
| POST | `/api/sessions/:id/analyze` | Trigger AI analysis |
| GET | `/api/sessions/:id/analysis` | Get analysis results |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANALYSIS_SERVICE_URL` | `http://localhost:8080/analyze` | AI service endpoint |
| `COACHPLUS_SECRET_KEY` | (dev key) | JWT signing secret |
| `OPENAI_API_KEY` | — | OpenAI API key (AI service) |

## License
MIT