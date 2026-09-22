import unittest
from unittest.mock import patch

from app.providers.youtube import YouTubePublisher


class YouTubeMetadataTests(unittest.TestCase):
    @patch("app.providers.youtube.MediaFileUpload")
    @patch("app.providers.youtube.build")
    @patch("app.providers.youtube.Credentials")
    def test_upload_declares_hindi_and_made_for_kids(self, credentials, build, media):
        publisher = YouTubePublisher("client", "secret", "refresh")
        service = build.return_value
        service.videos.return_value.insert.return_value.execute.return_value = {"id": "video-id"}

        result = publisher.upload("episode.mp4", "कहानी", "विवरण", ["बच्चों की कहानी"])

        self.assertEqual(result["id"], "video-id")
        request = service.videos.return_value.insert.call_args.kwargs
        self.assertEqual(request["body"]["snippet"]["defaultLanguage"], "hi")
        self.assertEqual(request["body"]["snippet"]["defaultAudioLanguage"], "hi")
        self.assertEqual(request["body"]["status"]["privacyStatus"], "private")
        self.assertIs(request["body"]["status"]["selfDeclaredMadeForKids"], True)

    def test_rejects_unknown_privacy_status(self):
        publisher = YouTubePublisher(None, None, None)
        with self.assertRaisesRegex(ValueError, "privacy_status"):
            publisher.upload("episode.mp4", "कहानी", "विवरण", [], "listed")


if __name__ == "__main__":
    unittest.main()
