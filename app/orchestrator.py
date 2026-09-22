from datetime import datetime, timezone

PIPELINE_STAGES = [
    "trend_research",
    "content_plan",
    "story",
    "characters_and_world",
    "scene_plan",
    "video_generation",
    "hindi_voice",
    "music_and_sfx",
    "thumbnail",
    "quality_and_safety",
    "shorts_and_long_video",
    "youtube_publish",
    "analytics_optimization",
]

def run_pipeline(topic: str | None = None) -> dict:
    # Provider adapters are intentionally separated from orchestration.
    # This keeps the workflow testable without exposing API keys in code.
    return {
        "status": "planned",
        "topic": topic,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": [{"name": stage, "status": "pending"} for stage in PIPELINE_STAGES],
    }
