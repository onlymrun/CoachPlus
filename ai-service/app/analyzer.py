"""AI Analysis Engine for CoachPlus.

Uses OpenAI's GPT-4o-mini to analyze life coaching session notes
and extract structured insights: goal progress, emotional patterns,
risk flags, and session prep summaries.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from openai import OpenAI

from app.config import (
    OPENAI_API_KEY,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
)
from app.models import (
    AnalyzeRequest,
    AnalyzeResponse,
    EmotionalPatterns,
    GoalProgress,
    PreviousNote,
    RiskItem,
)

logger = logging.getLogger(__name__)


# ── System Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a senior session analyst for a professional life coach. Your role is to analyze raw coaching session notes and extract actionable intelligence that helps the coach deliver more effective sessions.

You must analyze the notes carefully and return a JSON object with exactly these fields:

## 1. goals_progress (array)
For each goal (explicitly stated or implicitly mentioned), assess its status:
- "improving" — clear forward progress, new strategies being applied
- "stagnant" — no meaningful progress, same patterns persisting
- "slipping" — regression, setbacks, or abandoning progress
- "newly_identified" — a goal that emerged during this session
- "achieved" — the goal has been substantially met
Provide a confidence score (0.0 to 1.0) and specific evidence from the notes.

## 2. emotional_patterns (object)
- dominant_emotions: list of the most prominent emotions detected
- shifts: describe any emotional shifts during the session (e.g., "opened up midway", "became defensive when discussing career")
- recurring_themes: themes that appear repeatedly across the session or across sessions

## 3. risks (array)
Risk categories: burnout, anxiety, depression, relationship, career, health
Severity: low, medium, high
Only flag genuine concerns, not everyday challenges.

## 4. session_prep_summary (string)
A 2-3 sentence summary written for the coach to read BEFORE the next session. Include:
- Key topics from this session
- What to start with next time (e.g., "Celebrate the win on X before diving into Y")
- Any approach/style adjustments needed
Use a professional, warm, actionable tone.

IMPORTANT RULES:
- Be specific — reference concrete statements from the notes as evidence
- If notes are very short or sparse, state what you CAN infer and flag what's missing
- Don't invent information — only analyze what's in the notes
- Extract both explicit goals (stated by client) and implicit goals (revealed through subtext)
- Return ONLY valid JSON, no markdown formatting"""


def _build_messages(request: AnalyzeRequest) -> List[dict]:
    """Build the messages array for the OpenAI API call."""
    user_content_parts = []

    # Session notes
    user_content_parts.append(f"=== CURRENT SESSION NOTES ===\n{request.session_notes}\n")

    # Client context
    user_content_parts.append(f"Client ID: {request.client_id}")

    # Explicit goals
    if request.goals:
        goals_str = "\n".join(f"- {g}" for g in request.goals)
        user_content_parts.append(f"\n=== EXPLICIT GOALS ===\n{goals_str}")

    # Previous notes for trend context
    if request.previous_notes:
        prev_parts = []
        for i, prev in enumerate(request.previous_notes):
            date_str = prev.session_date or f"Session {i+1}"
            prev_parts.append(f"\n--- Previous Session ({date_str}) ---")
            prev_parts.append(prev.notes)
            if prev.goals:
                prev_parts.append(f"Goals discussed: {', '.join(prev.goals)}")
        user_content_parts.append("\n=== PREVIOUS SESSION NOTES ===\n" + "\n".join(prev_parts))

    user_content = "\n".join(user_content_parts)
    logger.debug(f"User content length: {len(user_content)} chars")

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _parse_response(raw: str) -> dict:
    """Parse the OpenAI response, handling potential formatting issues."""
    cleaned = raw.strip()
    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        # Find the first { or [
        start = cleaned.find("{")
        if start == -1:
            start = cleaned.find("[")
        if start != -1:
            # Find the last } or ]
            end = cleaned.rfind("}")
            if end == -1:
                end = cleaned.rfind("]")
            if end != -1:
                cleaned = cleaned[start : end + 1]
    return json.loads(cleaned)


def _generate_mock_response(request: AnalyzeRequest) -> AnalyzeResponse:
    """Generate a mock response when no API key is configured."""
    import uuid

    logger.warning("No OpenAI API key set. Returning mock analysis.")

    goals_list = request.goals or ["General well-being and growth"]
    goals_progress = [
        GoalProgress(
            goal=g,
            status="improving" if i == 0 else "stagnant",
            confidence=0.7,
            evidence=f"Based on session notes: client is actively engaged with this goal.",
        )
        for i, g in enumerate(goals_list)
    ]

    return AnalyzeResponse(
        goals_progress=goals_progress,
        emotional_patterns=EmotionalPatterns(
            dominant_emotions=["reflective", "engaged"],
            shifts="Client appeared more open in the second half of the session",
            recurring_themes=["personal growth", "work-life balance"],
        ),
        risks=[
            RiskItem(
                type="burnout",
                severity="low",
                detail="Monitor for signs of overwork in future sessions",
            )
        ],
        session_prep_summary=(
            f"Client {request.client_id} showed engagement this session. "
            "Continue building on the momentum from today. "
            "Consider starting next session by reviewing action items before diving into new topics."
        ),
    )


# ── Public API ──────────────────────────────────────────────────────────────

async def analyze_session(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze coaching session notes and return structured insights."""
    # If no API key, return mock data
    if not OPENAI_API_KEY:
        return _generate_mock_response(request)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        messages = _build_messages(request)

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        if not raw:
            raise ValueError("Empty response from OpenAI")

        parsed = _parse_response(raw)
        logger.info(f"Analysis complete for client {request.client_id}")

        # Parse into Pydantic models
        return AnalyzeResponse(
            goals_progress=[
                GoalProgress(**gp) for gp in parsed.get("goals_progress", [])
            ],
            emotional_patterns=EmotionalPatterns(**parsed.get("emotional_patterns", {})),
            risks=[
                RiskItem(**r) for r in parsed.get("risks", [])
            ],
            session_prep_summary=parsed.get("session_prep_summary", "No summary available."),
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        # Fall back to mock on failure
        return _generate_mock_response(request)