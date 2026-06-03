"""CoachPlus AI Analysis Microservice.

A FastAPI service that analyzes life coaching session notes using OpenAI's
GPT-4o-mini and returns structured insights for life coaches.

Endpoints:
- POST /analyze — Analyze session notes
- GET /health — Health check
- GET /openapi.json — OpenAPI specification
"""
from __future__ import annotations
import logging
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import analyze_session
from app.models import AnalyzeRequest, AnalyzeResponse

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("coachplus-ai")

# ── App Setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="CoachPlus AI Analysis Service",
    description="AI-powered session notes analysis for life coaches. "
    "Extracts goal progress, emotional patterns, risk flags, "
    "and session prep summaries from raw coaching notes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Allow all origins for development — Product Engineer will integrate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "coachplus-ai"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Analyze coaching session notes and return structured insights.

    Accepts raw session notes text along with optional goals and previous
    session context. Returns goal progress tracking, emotional patterns,
    risk flags, and a session prep summary for the coach.
    """
    try:
        logger.info(f"Analyzing session for client: {request.client_id}")
        result = await analyze_session(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error analyzing session: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")


# ── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
    )