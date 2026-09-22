from datetime import datetime, timezone
from app.services import exa, higgsfield, youtube

PIPELINE_STAGES = [
    "trend_research", "content_plan", "story", "characters_and_world",
    "scene_plan", "video_generation", "hindi_voice", "music_and_sfx",
    "thumbnail", "quality_and_safety", "shorts_and_long_video",
    "youtube_publish", "analytics_optimization",
]

def run_pipeline(topic: str | None = None) -> dict:
    chosen_topic = topic or "Hindi kids story: Chintu and the magic mango tree"
    research = {"status": "queued", "provider": "exa", "topic": chosen_topic}
    if exa.api_key:
        research["status"] = "ready"
    return {
        "status": "ready_for_generation" if higgsfield.enabled else "waiting_for_provider_keys",
        "topic": chosen_topic,
        "language": "hi",
        "channel_type": "kids",
        "animation_mode": "fully_animated",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": [
            {
                "name": stage,
                "status": ("ready" if stage == "trend_research" and exa.api_key else "waiting_for_provider")
            }
            for stage in PIPELINE_STAGES
        ],
        "providers": {
            "research": exa.api_key is not None,
            "video_generation": higgsfield.enabled,
            "youtube_upload": youtube.enabled,
        },
        "next_action": (
            "Run research, story, asset, video and publishing jobs once provider credentials are configured."
            if not higgsfield.enabled or not youtube.enabled
            else "Pipeline can execute."
        ),
    }
