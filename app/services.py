from app.config import settings
from app.providers.exa import ExaProvider
from app.providers.higgsfield import HiggsfieldProvider
from app.providers.pollinations import PollinationsProvider
from app.providers.youtube import YouTubePublisher
from app.providers.youtube_bridge import YouTubeBridgePublisher

exa = ExaProvider(settings.exa_api_key)

higgsfield = HiggsfieldProvider(
    settings.higgsfield_api_key_id,
    settings.higgsfield_api_key_secret,
    video_model=settings.higgsfield_video_model,
    voice_id=settings.higgsfield_voice_id,
    voice_type=settings.higgsfield_voice_type,
    allow_metered_generation=settings.allow_metered_video_generation,
)

pollinations = PollinationsProvider(settings.pollinations_api_key)

youtube = YouTubePublisher(
    settings.youtube_client_id,
    settings.youtube_client_secret,
    settings.youtube_refresh_token,
)

youtube_bridge = YouTubeBridgePublisher(
    settings.youtube_bridge_url,
    settings.youtube_bridge_secret,
)
