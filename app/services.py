from app.config import settings
from app.providers.exa import ExaProvider
from app.providers.higgsfield import HiggsfieldProvider
from app.providers.youtube import YouTubePublisher

exa = ExaProvider(settings.exa_api_key)
higgsfield = HiggsfieldProvider(
    settings.higgsfield_api_key_id,
    settings.higgsfield_api_key_secret,
    video_model=settings.higgsfield_video_model,
    voice_id=settings.higgsfield_voice_id,
    voice_type=settings.higgsfield_voice_type,
)
youtube = YouTubePublisher(
    settings.youtube_client_id,
    settings.youtube_client_secret,
    settings.youtube_refresh_token,
)
