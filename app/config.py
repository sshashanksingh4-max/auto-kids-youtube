from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"

    # Research
    exa_api_key: str | None = None

    # Media providers. Paid providers are optional; the system must not
    # purchase credits automatically.
    higgsfield_api_key_id: str | None = None
    higgsfield_api_key_secret: str | None = None
    higgsfield_video_model: str = "seedance_2.0"
    higgsfield_voice_id: str | None = None
    higgsfield_voice_type: str = "preset"
    pollinations_api_key: str | None = None

    # Direct YouTube OAuth (optional fallback).
    youtube_client_id: str | None = None
    youtube_client_secret: str | None = None
    youtube_refresh_token: str | None = None

    # Zero-cost YouTube Apps Script bridge.
    youtube_bridge_url: str | None = None
    youtube_bridge_secret: str | None = None

    # Optional database.
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
