from fastapi import FastAPI
from app.orchestrator import run_pipeline

app = FastAPI(
    title="Auto Kids YouTube",
    version="0.1.0",
    description="Automation backend for original Hindi kids video production."
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "auto-kids-youtube"}

@app.post("/pipeline/run")
def pipeline_run(topic: str | None = None):
    return run_pipeline(topic)
