"""Plan definitions and limits for CoachPlus subscriptions."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Plan:
    name: str
    display_name: str
    price_monthly: int  # in USD
    max_clients: Optional[int]  # None = unlimited
    max_sessions_per_client: Optional[int]  # None = unlimited


PLANS = {
    "starter": Plan(
        name="starter",
        display_name="Starter",
        price_monthly=29,
        max_clients=10,
        max_sessions_per_client=None,
    ),
    "pro": Plan(
        name="pro",
        display_name="Pro",
        price_monthly=59,
        max_clients=50,
        max_sessions_per_client=None,
    ),
    "agency": Plan(
        name="agency",
        display_name="Agency",
        price_monthly=99,
        max_clients=None,  # Unlimited
        max_sessions_per_client=None,
    ),
}

FREE_TIER_CLIENTS = 3  # Free/trial users get 3 clients

ALLOWED_PLANS = list(PLANS.keys())


def get_plan(tier: str) -> Optional[Plan]:
    """Get plan details by tier name."""
    return PLANS.get(tier)


def get_max_clients(tier: str) -> Optional[int]:
    """Get max clients allowed for a plan tier. None = unlimited."""
    if tier == "free" or tier not in PLANS:
        return FREE_TIER_CLIENTS
    plan = PLANS.get(tier)
    return plan.max_clients if plan else FREE_TIER_CLIENTS


def format_usage(current: int, max_allowed: Optional[int]) -> dict:
    """Format usage data for API response."""
    return {
        "used": current,
        "limit": max_allowed if max_allowed is not None else None,
        "remaining": None if max_allowed is None else max_allowed - current,
        "percent": None if max_allowed is None else round((current / max_allowed) * 100, 1),
        "unlimited": max_allowed is None,
    }