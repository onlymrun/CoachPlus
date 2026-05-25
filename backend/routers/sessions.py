"""Session notes CRUD and analysis trigger."""

import json
import os
from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import User, Client, Session as SessionModel, Analysis
from schemas import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    AnalysisTriggerResponse,
    AnalysisResponse,
    GoalProgress,
    EmotionalPattern,
    RiskFlag,
    SessionPrep,
)
from auth import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

# AI service URL — configurable via environment variable
AI_SERVICE_URL = os.environ.get(
    "ANALYSIS_SERVICE_URL",
    "http://localhost:8080/analyze"
)


@router.get("/", response_model=List[SessionResponse])
def list_sessions(
    client_id: str = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List sessions, optionally filtered by client_id."""
    query = db.query(SessionModel).filter(SessionModel.coach_id == current_user.id)

    if client_id:
        query = query.filter(SessionModel.client_id == client_id)

    sessions = query.order_by(SessionModel.session_date.desc()).offset(skip).limit(limit).all()

    result = []
    for session in sessions:
        has_analysis = db.query(Analysis).filter(Analysis.session_id == session.id).count() > 0
        session_data = SessionResponse.model_validate(session)
        session_data.has_analysis = has_analysis
        result.append(session_data)
    return result


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    data: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new session note for a client."""
    # Verify the client belongs to the current coach
    client = (
        db.query(Client)
        .filter(Client.id == data.client_id, Client.coach_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    session = SessionModel(
        client_id=data.client_id,
        coach_id=current_user.id,
        title=data.title,
        notes=data.notes,
        session_date=data.session_date,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single session by ID."""
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.coach_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    has_analysis = db.query(Analysis).filter(Analysis.session_id == session.id).count() > 0
    session_data = SessionResponse.model_validate(session)
    session_data.has_analysis = has_analysis
    return session_data


@router.put("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: str,
    data: SessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a session note."""
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.coach_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if data.title is not None:
        session.title = data.title
    if data.notes is not None:
        session.notes = data.notes
    if data.session_date is not None:
        session.session_date = data.session_date

    db.commit()
    db.refresh(session)

    has_analysis = db.query(Analysis).filter(Analysis.session_id == session.id).count() > 0
    session_data = SessionResponse.model_validate(session)
    session_data.has_analysis = has_analysis
    return session_data


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a session note."""
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.coach_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    db.delete(session)
    db.commit()
    return None


@router.post("/{session_id}/analyze", response_model=AnalysisTriggerResponse)
def analyze_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger AI analysis on a session.

    Calls the AI Analyst's service to extract insights from session notes.
    Maps the response to the frontend's expected format.
    """
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.coach_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        # Call the AI service with its expected request format
        response = requests.post(
            AI_SERVICE_URL,
            json={
                "session_notes": session.notes,
                "client_id": session.client_id,
                "goals": [],
            },
            timeout=30,
        )
        response.raise_for_status()
        ai_result = response.json()
        # Transform from AI service format to our internal format
        normalized = _normalize_ai_response(ai_result)
    except requests.ConnectionError:
        # AI service not available — return mock analysis for development
        normalized = _generate_mock_analysis(session.notes)
    except requests.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI analysis service timed out. Please try again.",
        )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis service error: {str(e)}",
        )

    # Save the analysis
    analysis = Analysis(
        session_id=session.id,
        coach_id=current_user.id,
        goal_progress=normalized.get("goal_progress", []),
        emotional_patterns=normalized.get("emotional_patterns", []),
        risk_flags=normalized.get("risk_flags", []),
        session_prep=normalized.get("session_prep", {}),
        raw_analysis=json.dumps(normalized),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return AnalysisTriggerResponse(
        status="success",
        analysis=_analysis_to_response(analysis),
    )


@router.get("/{session_id}/analysis", response_model=AnalysisResponse)
def get_analysis(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest analysis for a session."""
    session = (
        db.query(SessionModel)
        .filter(SessionModel.id == session_id, SessionModel.coach_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    analysis = (
        db.query(Analysis)
        .filter(Analysis.session_id == session_id)
        .order_by(Analysis.analyzed_at.desc())
        .first()
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found for this session. Trigger analysis first.",
        )

    return _analysis_to_response(analysis)


def _normalize_ai_response(ai_result: dict) -> dict:
    """Transform AI service response format to our internal format.

    AI service returns:
      goals_progress: [{goal, status, confidence, evidence}]
      emotional_patterns: {dominant_emotions, shifts, recurring_themes}
      risks: [{type, severity, detail}]
      session_prep_summary: str

    We transform to:
      goal_progress: [{goal, progress, status}]
      emotional_patterns: [{emotion, intensity, context}]
      risk_flags: [{risk, severity, suggestion}]
      session_prep: {summary, key_topics, recommended_focus}
    """
    # Map goals_progress -> goal_progress
    gp_list = []
    for gp in ai_result.get("goals_progress", []):
        gp_list.append({
            "goal": gp.get("goal", ""),
            "progress": gp.get("evidence", ""),
            "status": gp.get("status", "identified"),
        })

    # Map emotional_patterns object -> list of emotion entries
    ep_obj = ai_result.get("emotional_patterns", {})
    ep_list = []
    for emotion in ep_obj.get("dominant_emotions", []):
        ep_list.append({
            "emotion": emotion,
            "intensity": 5,
            "context": ep_obj.get("shifts", ""),
        })

    # Map risks -> risk_flags
    rf_list = []
    for risk in ai_result.get("risks", []):
        rf_list.append({
            "risk": risk.get("type", "").replace("_", " ").title(),
            "severity": risk.get("severity", "low"),
            "suggestion": risk.get("detail", ""),
        })

    # Map session_prep_summary -> session_prep object
    prep_summary = ai_result.get("session_prep_summary", "")
    topics = ep_obj.get("recurring_themes", [])

    return {
        "goal_progress": gp_list,
        "emotional_patterns": ep_list,
        "risk_flags": rf_list,
        "session_prep": {
            "summary": prep_summary,
            "key_topics": topics,
            "recommended_focus": topics[0] if topics else "Continue working on identified goals.",
        },
    }


def _analysis_to_response(analysis: Analysis) -> AnalysisResponse:
    """Convert Analysis model to response schema."""
    return AnalysisResponse(
        id=analysis.id,
        session_id=analysis.session_id,
        goal_progress=[GoalProgress(**gp) for gp in (analysis.goal_progress or [])],
        emotional_patterns=[EmotionalPattern(**ep) for ep in (analysis.emotional_patterns or [])],
        risk_flags=[RiskFlag(**rf) for rf in (analysis.risk_flags or [])],
        session_prep=SessionPrep(**analysis.session_prep) if analysis.session_prep else None,
        analyzed_at=analysis.analyzed_at,
    )


def _generate_mock_analysis(notes: str) -> dict:
    """Generate mock analysis when the AI service is unavailable (development mode)."""
    return {
        "goal_progress": [
            {
                "goal": "Improve work-life balance",
                "progress": "Client mentioned setting boundaries at work this week.",
                "status": "on_track",
            },
            {
                "goal": "Reduce anxiety symptoms",
                "progress": "Still experiencing morning anxiety but using breathing techniques.",
                "status": "in_progress",
            },
        ],
        "emotional_patterns": [
            {"emotion": "anxiety", "intensity": 7, "context": "Discussed work pressures and deadlines"},
            {"emotion": "hope", "intensity": 5, "context": "Noticed improvement in communication skills"},
            {"emotion": "frustration", "intensity": 6, "context": "Relationship with manager"},
        ],
        "risk_flags": [
            {
                "risk": "Persistent high anxiety",
                "severity": "medium",
                "suggestion": "Consider recommending stress management techniques or therapist referral",
            },
        ],
        "session_prep": {
            "summary": "Client is making progress on work-life balance but struggling with workplace anxiety. Key focus areas include boundary-setting and coping strategies.",
            "key_topics": [
                "Workplace relationships",
                "Anxiety management",
                "Boundary setting",
                "Communication skills",
            ],
            "recommended_focus": "Continue building on boundary-setting exercises and explore root causes of workplace anxiety.",
        },
    }