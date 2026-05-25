"""Authentication routes — register, login, plan management, usage."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import bcrypt

from database import get_db
from models import User, Client, Session as SessionModel
from schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    PlanUpdate,
    UsageResponse,
    UsageInfo,
)
from auth import create_access_token, get_current_user
from plans import PLANS, ALLOWED_PLANS, get_plan, format_usage

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Register a new coach account."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    password_hash = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user = User(
        email=data.email,
        password_hash=password_hash,
        full_name=data.full_name,
        subscription_tier="starter",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Log in and receive a JWT token."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not bcrypt.checkpw(data.password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user.id})

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/plan", response_model=UserResponse)
def update_plan(
    data: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the user's subscription plan (mock Stripe checkout)."""
    if data.plan not in ALLOWED_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {', '.join(ALLOWED_PLANS)}",
        )

    plan = get_plan(data.plan)
    current_user.subscription_tier = data.plan
    db.commit()
    db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/usage", response_model=UsageResponse)
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current usage stats — clients used vs plan limits."""
    plan = get_plan(current_user.subscription_tier)

    client_count = db.query(func.count(Client.id)).filter(
        Client.coach_id == current_user.id
    ).scalar()

    session_count = db.query(func.count(SessionModel.id)).filter(
        SessionModel.coach_id == current_user.id
    ).scalar()

    return UsageResponse(
        plan=current_user.subscription_tier,
        plan_display_name=plan.display_name if plan else "Starter",
        plan_price=plan.price_monthly if plan else 0,
        clients=format_usage(
            client_count,
            plan.max_clients if plan else 3,
        ),
        sessions=UsageInfo(
            used=session_count,
            limit=None,
            remaining=None,
            percent=None,
            unlimited=True,
        ),
    )