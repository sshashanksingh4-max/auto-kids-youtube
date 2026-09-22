from fastapi import FastAPI
from app.orchestrator import run_pipeline
from app.services import exa, higgsfield, youtube

app = FastAPI(
    title="Auto Kids YouTube",
    version="0.2.0",
    description="Automation backend for original Hindi kids video production."
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "auto-kids-youtube",
        "message": "Auto Kids YouTube API is running.",
        "endpoints": {
            "health": "/health",
            "pipeline": "/pipeline/run",
            "docs": "/docs",
        },
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "auto-kids-youtube",
        "providers": {
            "research": exa.api_key is not None,
            "video": higgsfield.enabled,
            "youtube": youtube.enabled,
        },
    }

@app.post("/pipeline/run")
def pipeline_run(topic: str | None = None):
    return run_pipeline(topic)
