"""Upload natural-voice trial outputs as private YouTube drafts only."""
from __future__ import annotations

import json
import os
from pathlib import Path

from app.config import settings
from app.content_engine import make_metadata
from app.local_render import STORY_TITLE
from app.providers.youtube import YouTubePublisher


def _voice_is_publishable(video_path: Path) -> tuple[bool, str]:
    sidecar = video_path.with_suffix(".voices.json")
    if not sidecar.is_file():
        return False, f"missing voice provenance: {sidecar.name}"
    provenance = json.loads(sidecar.read_text(encoding="utf-8"))
    modes = provenance.get("scene_voice_modes", [])
    if provenance.get("provider") != "svara" or not modes:
        return False, f"{video_path.name} does not use the natural Svara voice path"
    if any(mode != "svara_shared_youthful" for mode in modes):
        return False, f"{video_path.name} has an unapproved voice mode"
    return True, "natural-voice provenance passed"


def main() -> int:
    event = os.getenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    if event not in {"schedule", "workflow_dispatch"}:
        print({"status": "skipped", "reason": "uploads are disabled for pull requests"})
        return 0

    publisher = YouTubePublisher(
        settings.youtube_client_id,
        settings.youtube_client_secret,
        settings.youtube_refresh_token,
    )
    if not publisher.enabled:
        print({"status": "skipped", "reason": "YouTube OAuth secrets are not configured"})
        return 0

    videos = [
        (
            Path(os.getenv("KIDS_OUTPUT", "/tmp/kids-video.mp4")),
            Path(os.getenv("KIDS_THUMBNAIL_OUTPUT", "/tmp/kids-thumbnail.jpg")),
            False,
        ),
        (
            Path(os.getenv("KIDS_SHORT_OUTPUT", "/tmp/kids-short.mp4")),
            None,
            True,
        ),
    ]
    for video_path, _thumbnail, _short in videos:
        if not video_path.is_file():
            raise FileNotFoundError(f"Rendered output is missing: {video_path}")
        passed, reason = _voice_is_publishable(video_path)
        if not passed:
            print({"status": "skipped", "reason": reason})
            return 0

    results = []
    for video_path, thumbnail_path, short in videos:
        metadata = make_metadata({"title": STORY_TITLE}, short=short)
        result = publisher.upload(
            str(video_path),
            metadata["youtube_title"],
            metadata["description"],
            metadata["tags"],
            privacy_status="private",
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
        )
        results.append({
            "format": "short" if short else "long",
            "video_id": result.get("id"),
            "watch_url": f"https://youtu.be/{result['id']}" if result.get("id") else None,
            "privacy_status": result.get("status", {}).get("privacyStatus"),
            "thumbnail_set": bool(result.get("thumbnailSet")),
        })
    print({"status": "uploaded_private_drafts", "results": results})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
