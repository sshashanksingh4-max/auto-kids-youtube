from fastapi import FastAPI
from app.executor import generate_scene_jobs
from app.orchestrator import run_pipeline
from app.services import exa, higgsfield, youtube

app = FastAPI(
    title="Auto Kids YouTube",
    version="0.4.0",
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
            "preview": "/pipeline/preview",
            "pipeline": "/pipeline/run",
            "generate_scenes": "/pipeline/generate-scenes",
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
            "metered_video_generation_allowed": higgsfield.allow_metered_generation,
            "voice_configured": higgsfield.voice_enabled,
            "youtube": youtube.enabled,
        },
    }

@app.get("/pipeline/preview")
def pipeline_preview(topic: str | None = None):
    return run_pipeline(topic)

@app.post("/pipeline/run")
def pipeline_run(topic: str | None = None):
    return run_pipeline(topic)

@app.post("/pipeline/generate-scenes")
async def pipeline_generate_scenes(topic: str | None = None):
    return await generate_scene_jobs(topic)
