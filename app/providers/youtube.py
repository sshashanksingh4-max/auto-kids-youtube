from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

class YouTubePublisher:
    def __init__(self, client_id: str | None, client_secret: str | None, refresh_token: str | None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    @property
    def enabled(self) -> bool:
        return bool(self.client_id and self.client_secret and self.refresh_token)

    def upload(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        privacy_status: str = "private",
        thumbnail_path: str | None = None,
    ) -> dict:
        if privacy_status not in {"private", "unlisted", "public"}:
            raise ValueError("privacy_status must be private, unlisted, or public")
        if not self.enabled:
            return {"enabled": False, "status": "not_configured"}

        credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=[YOUTUBE_UPLOAD_SCOPE],
        )
        youtube = build("youtube", "v3", credentials=credentials)
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "24",
                    "defaultLanguage": "hi",
                    "defaultAudioLanguage": "hi",
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": True,
                },
            },
            media_body=MediaFileUpload(str(Path(video_path)), resumable=True),
        )
        uploaded = request.execute()
        if thumbnail_path and uploaded.get("id"):
            thumbnail_request = youtube.thumbnails().set(
                videoId=uploaded["id"],
                media_body=MediaFileUpload(
                    str(Path(thumbnail_path)),
                    mimetype="image/jpeg",
                    resumable=False,
                ),
            )
            thumbnail_request.execute()
            uploaded["thumbnailSet"] = True
        return uploaded
