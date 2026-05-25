"""Configuration for the CoachPlus AI Analysis Service."""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

if not OPENAI_API_KEY:
    print("⚠️  WARNING: OPENAI_API_KEY is not set. The /analyze endpoint will return mock data.")
    print("   Set the OPENAI_API_KEY environment variable or add it to a .env file.")