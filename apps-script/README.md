# Zero-cost YouTube publisher bridge

This bridge avoids requiring a third-party YouTube publishing connector.

Google Apps Script can access the YouTube Data API through its Advanced YouTube service after you enable it and authorize the script with the Google account that owns the channel.

## One-time setup

1. Open Google Apps Script and create a new project.
2. Add YouTube Data API under Services.
3. Paste youtube_uploader.gs into the editor.
4. In Project Settings -> Script Properties, create UPLOAD_SECRET.
5. Deploy the project as a Web app.
6. Execute the web app as your account and grant access to anyone who has the web-app URL.
7. Run the authorization flow once with the channel-owning Google account.

The endpoint accepts a JSON POST containing secret, videoUrl, title, description, tags, and privacyStatus.

Google documents the YouTube service as an Apps Script Advanced Service for managing videos, playlists and channels. The authorization happens through the Google account running the script, so this route does not depend on Windsor for publishing.
