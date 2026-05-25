"""SQLAlchemy models for CoachPlus."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    subscription_tier = Column(String, default="starter")  # starter, pro, agency
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    clients = relationship("Client", back_populates="coach", cascade="all, delete-orphan")


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, default=generate_uuid)
    coach_id = Column(String, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    coach = relationship("User", back_populates="clients")
    sessions = relationship("Session", back_populates="client", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    coach_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    notes = Column(Text, nullable=False)  # The raw session notes
    session_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    client = relationship("Client", back_populates="sessions")
    analyses = relationship("Analysis", back_populates="session", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    coach_id = Column(String, ForeignKey("users.id"), nullable=False)

    # AI-generated insights stored as JSON
    goal_progress = Column(JSON, nullable=True)       # [{goal: "...", progress: "...", status: "on_track|at_risk|completed"}]
    emotional_patterns = Column(JSON, nullable=True)  # [{emotion: "...", intensity: 0-10, context: "..."}]
    risk_flags = Column(JSON, nullable=True)          # [{risk: "...", severity: "low|medium|high", suggestion: "..."}]
    session_prep = Column(JSON, nullable=True)        # {summary: "...", key_topics: [...], recommended_focus: "..."}

    raw_analysis = Column(Text, nullable=True)  # Raw AI response for debugging
    analyzed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="analyses")