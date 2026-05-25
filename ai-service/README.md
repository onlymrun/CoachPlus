# CoachPlus AI Analysis Service

AI-powered session notes analysis for life coaches. Extracts goal progress, emotional patterns, risk flags, and session prep summaries from raw coaching notes using OpenAI's GPT-4o-mini.

## Quick Start

```bash
# 1. Set your OpenAI API key (or run in mock mode without it)
export OPENAI_API_KEY=sk-your-key-here

# 2. Start the server
./start.sh
# Server runs on http://0.0.0.0:8080

# 3. Test it
curl http://localhost:8080/health
```

## API Endpoints

### `GET /health`
Health check — returns `{"status": "healthy", "service": "coachplus-ai"}`

### `POST /analyze`
Analyze session notes and return structured insights.

**Request:**
```json
{
  "session_notes": "Client reported feeling anxious about work deadlines. Used breathing techniques successfully.",
  "client_id": "client-1",
  "goals": ["Reduce work-related anxiety", "Improve work-life balance"],
  "previous_notes": [
    {
      "session_date": "2024-01-10",
      "notes": "Client was very stressed about project deadlines.",
      "goals": ["Reduce work-related anxiety"]
    }
  ]
}
```

**Response:**
```json
{
  "goals_progress": [
    {
      "goal": "Reduce work-related anxiety",
      "status": "improving",
      "confidence": 0.85,
      "evidence": "Client reported using breathing techniques successfully"
    }
  ],
  "emotional_patterns": {
    "dominant_emotions": ["anxiety", "hope"],
    "shifts": "Noticed shift from defensive to open body language mid-session",
    "recurring_themes": ["work pressure", "family expectations"]
  },
  "risks": [
    {
      "type": "burnout",
      "severity": "medium",
      "detail": "Working 60+ hours consistently"
    }
  ],
  "session_prep_summary": "Key topic this week: career transition. Client has been resistant to exploring options. Start with wins from last week before diving into the tough conversation."
}
```

## Interactive API Docs
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

## Configuration
| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | (none) | OpenAI API key. Without it, mock data is returned. |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model to use |
| `OPENAI_MAX_TOKENS` | 2000 | Max tokens for response |
| `OPENAI_TEMPERATURE` | 0.3 | Temperature (lower = more consistent) |

## Architecture

```
app/
├── __init__.py       # Package init
├── main.py           # FastAPI application, routes, CORS
├── analyzer.py       # AI analysis engine (OpenAI prompt chains)
├── models.py         # Pydantic request/response schemas
└── config.py         # Environment variable configuration
```

## Prompt Engineering
The system prompt establishes the AI as a "senior session analyst for a professional life coach" and instructs it to:
- Track goal progress: improving, stagnant, slipping, newly_identified, achieved
- Detect emotional patterns and shifts within sessions
- Flag risks across categories: burnout, anxiety, depression, relationship, career, health
- Generate actionable session prep summaries for the coach's next session
- Return ONLY valid JSON (uses OpenAI response_format)

## Mock Mode
Without `OPENAI_API_KEY`, the service returns plausible mock data so the Product Engineer can integrate without needing the API key immediately.
