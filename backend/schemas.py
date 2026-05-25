"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ─── Auth Schemas ───────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PlanUpdate(BaseModel):
    plan: str  # starter, pro, agency


class UsageInfo(BaseModel):
    used: int
    limit: Optional[int] = None
    remaining: Optional[int] = None
    percent: Optional[float] = None
    unlimited: bool = False


class UsageResponse(BaseModel):
    plan: str
    plan_display_name: str
    plan_price: int
    clients: UsageInfo
    sessions: UsageInfo

    class Config:
        from_attributes = True


# ─── Client Schemas ─────────────────────────────────────────────────────────

class ClientCreate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class ClientUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None


class ClientResponse(BaseModel):
    id: str
    coach_id: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    session_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ─── Session Schemas ────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    client_id: str
    title: Optional[str] = None
    notes: str
    session_date: Optional[datetime] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    session_date: Optional[datetime] = None


class SessionResponse(BaseModel):
    id: str
    client_id: str
    coach_id: str
    title: Optional[str] = None
    notes: str
    session_date: datetime
    created_at: datetime
    has_analysis: bool = False

    class Config:
        from_attributes = True


# ─── Analysis Schemas ───────────────────────────────────────────────────────

class GoalProgress(BaseModel):
    goal: str
    progress: str
    status: str


class EmotionalPattern(BaseModel):
    emotion: str
    intensity: int
    context: str


class RiskFlag(BaseModel):
    risk: str
    severity: str
    suggestion: str


class SessionPrep(BaseModel):
    summary: str
    key_topics: list[str]
    recommended_focus: str


class AnalysisResponse(BaseModel):
    id: str
    session_id: str
    goal_progress: Optional[list[GoalProgress]] = None
    emotional_patterns: Optional[list[EmotionalPattern]] = None
    risk_flags: Optional[list[RiskFlag]] = None
    session_prep: Optional[SessionPrep] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnalysisTriggerResponse(BaseModel):
    status: str
    analysis: Optional[AnalysisResponse] = None
    message: Optional[str] = None