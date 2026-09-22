from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
    exa_api_key: str | None = None
    higgsfield_api_key_id: str | None = None
    higgsfield_api_key_secret: str | None = None
    youtube_client_id: str | None = None
    youtube_client_secret: str | None = None
    youtube_refresh_token: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
