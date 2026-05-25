"""CoachPlus Backend API — Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import auth, clients, sessions

app = FastAPI(
    title="CoachPlus API",
    description="AI-powered analytics layer for life coaches",
    version="0.1.0",
)

# CORS — allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(sessions.router)


@app.on_event("startup")
def on_startup():
    """Initialize the database on app startup."""
    init_db()


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)