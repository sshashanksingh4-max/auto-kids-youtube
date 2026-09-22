from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.content_engine import make_content_plan, make_metadata, make_scene_plan, make_story, normalize_topic
from app.quality import review_content
from app.services import higgsfield


async def generate_scene_jobs(topic: str | None = None) -> dict:
    chosen = normalize_topic(topic)
    plan = make_content_plan(chosen)
    story = make_story(plan)
    scenes = make_scene_plan(story)
    quality = review_content(story, scenes)

    if quality["status"] != "passed":
        return {
            "status": "blocked_by_quality_review",
            "quality_review": quality,
        }

    if not higgsfield.enabled:
        return {
            "status": "waiting_for_provider_keys",
            "required": ["HIGGSFIELD_API_KEY_ID", "HIGGSFIELD_API_KEY_SECRET"],
            "story": story,
            "scene_plan": scenes,
        }

    async def submit(scene: dict) -> dict:
        result = await higgsfield.text_to_video(
            prompt=scene["prompt"],
            duration=min(int(scene["seconds"]), 30),
            resolution="720p",
            aspect_ratio="16:9",
            generate_audio=True,
        )
        return {
            "scene": scene["scene"],
            "seconds_requested": min(int(scene["seconds"]), 30),
            "result": result,
        }

    jobs = await asyncio.gather(*(submit(scene) for scene in scenes))
    return {
        "status": "scene_generation_submitted",
        "topic": chosen,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": make_metadata(story),
        "story": story,
        "quality_review": quality,
        "jobs": jobs,
        "next_step": "Poll the returned Higgsfield request IDs, download completed media, assemble long/short cuts, then publish after final QC.",
    }
