from __future__ import annotations

import httpx


class YouTubeBridgePublisher:
    """Calls a user-owned Google Apps Script web app for YouTube publishing."""

    def __init__(self, url: str | None, secret: str | None):
        self.url = url
        self.secret = secret

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.secret)

    async def upload(
        self,
        video_url: str,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        privacy_status: str = "private",
        file_name: str = "kids-video.mp4",
    ) -> dict:
        if not self.enabled:
            return {"enabled": False, "status": "not_configured"}

        payload = {
            "secret": self.secret,
            "videoUrl": video_url,
            "fileName": file_name,
            "title": title,
            "description": description,
            "tags": tags or [],
            "privacyStatus": privacy_status,
        }
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
