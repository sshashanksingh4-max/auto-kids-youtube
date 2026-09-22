import httpx

class HiggsfieldProvider:
    def __init__(
        self,
        key_id: str | None,
        key_secret: str | None,
        video_model: str = "seedance_2.0",
        voice_id: str | None = None,
        voice_type: str = "preset",
        allow_metered_generation: bool = False,
    ):
        self.key_id = key_id
        self.key_secret = key_secret
        self.video_model = video_model
        self.voice_id = voice_id
        self.voice_type = voice_type
        self.allow_metered_generation = allow_metered_generation

    @property
    def enabled(self) -> bool:
        return bool(self.key_id and self.key_secret and self.allow_metered_generation)

    @property
    def cost_gate_closed(self) -> bool:
        return not self.allow_metered_generation

    @property
    def voice_enabled(self) -> bool:
        return self.enabled and bool(self.voice_id)

    def headers(self) -> dict:
        return {
            "Authorization": f"Key {self.key_id}:{self.key_secret}",
            "Content-Type": "application/json",
        }

    async def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        generate_audio: bool = True,
    ) -> dict:
        if not self.enabled:
            status = "metered_generation_disabled" if self.cost_gate_closed else "not_configured"
            return {"enabled": False, "status": status}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.higgsfield.ai/bytedance/seedance-2.0/text-to-video",
                headers=self.headers(),
                json={
                    "prompt": prompt,
                    "resolution": resolution,
                    "generate_audio": generate_audio,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                },
            )
            response.raise_for_status()
            return response.json()

    async def request_status(self, request_id: str) -> dict:
        if not self.enabled:
            return {"enabled": False, "status": "not_configured"}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"https://api.higgsfield.ai/requests/{request_id}/status",
                headers=self.headers(),
            )
            response.raise_for_status()
            return response.json()
