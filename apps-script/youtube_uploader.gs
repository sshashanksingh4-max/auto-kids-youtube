/**
 * Zero-cost YouTube publisher bridge.
 *
 * Setup:
 * 1. Create a Google Apps Script project.
 * 2. Add the YouTube Data API as an Advanced Google Service.
 * 3. Paste this file into the project.
 * 4. In Script Properties add UPLOAD_SECRET with a long random value.
 * 5. Deploy as Web app, Execute as: Me, access: Anyone with the URL.
 * 6. Authorize the script with the Google/YouTube account that owns the channel.
 *
 * The automation service can POST JSON to the web app:
 * {
 *   "secret": "...",
 *   "videoUrl": "https://...",
 *   "title": "...",
 *   "description": "...",
 *   "tags": ["Hindi kids story", "..."],
 *   "privacyStatus": "private"
 * }
 *
 * Keep privacyStatus="private" for the first connectivity test. You can
 * change it later after the channel/API setup is validated.
 */

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || "{}");
    const props = PropertiesService.getScriptProperties();
    const expected = props.getProperty("UPLOAD_SECRET");

    if (!expected || body.secret !== expected) {
      return json({ ok: false, error: "unauthorized" }, 401);
    }

    if (!body.videoUrl || !body.title) {
      return json({ ok: false, error: "videoUrl and title are required" }, 400);
    }

    const response = UrlFetchApp.fetch(body.videoUrl, {
      muteHttpExceptions: true,
      followRedirects: true,
    });

    if (response.getResponseCode() < 200 || response.getResponseCode() >= 300) {
      return json({
        ok: false,
        error: "video_download_failed",
        httpCode: response.getResponseCode(),
      }, 502);
    }

    const blob = response.getBlob()
      .setContentType("video/mp4")
      .setName(body.fileName || "kids-video.mp4");

    const resource = {
      snippet: {
        title: String(body.title).slice(0, 100),
        description: String(body.description || "").slice(0, 5000),
        tags: Array.isArray(body.tags) ? body.tags.map(String).slice(0, 500) : [],
        categoryId: "24",
        defaultLanguage: "hi",
        defaultAudioLanguage: "hi",
      },
      status: {
        privacyStatus: body.privacyStatus === "public" ? "public"
          : body.privacyStatus === "unlisted" ? "unlisted"
          : "private",
        selfDeclaredMadeForKids: true,
      },
    };

    const uploaded = YouTube.Videos.insert(resource, "snippet,status", blob);

    return json({
      ok: true,
      videoId: uploaded.id,
      watchUrl: "https://youtu.be/" + uploaded.id,
      privacyStatus: uploaded.status && uploaded.status.privacyStatus,
    }, 200);
  } catch (err) {
    return json({
      ok: false,
      error: String(err && err.message ? err.message : err),
    }, 500);
  }
}

function doGet() {
  return json({
    ok: true,
    service: "zero-cost-youtube-publisher",
    message: "YouTube upload bridge is running.",
  }, 200);
}

function json(payload, statusCode) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
