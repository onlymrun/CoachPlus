"""Pydantic models for request/response schemas."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ── Request Models ──────────────────────────────────────────────────────────

class PreviousNote(BaseModel):
    """A previous coaching session note for cross-session analysis."""

    session_date: Optional[str] = Field(None, description="Date of the previous session")
    notes: str = Field(..., description="Session notes text")
    goals: Optional[List[str]] = Field(None, description="Goals discussed in that session")


class Goal(BaseModel):
    """A goal the client is working on."""

    description: str = Field(..., description="The goal statement")


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze."""

    session_notes: str = Field(..., description="The raw session notes text to analyze")
    client_id: str = Field(..., description="Unique identifier for the client")
    goals: Optional[List[str]] = Field(None, description="List of explicit goals the client is working on")
    previous_notes: Optional[List[PreviousNote]] = Field(None, description="Previous session notes for trend analysis")


# ── Response Models ─────────────────────────────────────────────────────────

class GoalProgress(BaseModel):
    """Progress tracking for a single goal."""

    goal: str = Field(..., description="The goal statement")
    status: str = Field(..., description="One of: improving, stagnant, slipping, newly_identified, achieved")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this assessment (0-1)")
    evidence: str = Field(..., description="Specific evidence from session notes supporting this assessment")


class RiskItem(BaseModel):
    """An identified risk or concern."""

    type: str = Field(..., description="Risk category: burnout, anxiety, depression, relationship, career, health")
    severity: str = Field(..., description="One of: low, medium, high")
    detail: str = Field(..., description="Specific details about the risk")


class EmotionalPatterns(BaseModel):
    """Emotional patterns detected in the session."""

    dominant_emotions: List[str] = Field(..., description="Dominant emotions detected in this session")
    shifts: Optional[str] = Field(None, description="Emotional shifts observed during the session")
    recurring_themes: List[str] = Field(..., description="Recurring themes across sessions")


class AnalyzeResponse(BaseModel):
    """Response body for POST /analyze."""

    goals_progress: List[GoalProgress] = Field(..., description="Progress tracking for each goal")
    emotional_patterns: EmotionalPatterns = Field(..., description="Emotional patterns detected")
    risks: List[RiskItem] = Field(..., description="Identified risks and concerns")
    session_prep_summary: str = Field(..., description="A concise session prep summary for the coach")