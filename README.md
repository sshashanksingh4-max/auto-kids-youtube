# Auto Kids YouTube

Free-first tooling for planning and producing original Hindi children's cartoons.

## Current capabilities

- Deterministic Hindi story, metadata, character and scene-plan generation.
- A family-safety precheck for story text and scene prompts.
- A procedural 2D renderer in `app/local_render.py`: per-frame character poses, walking motion, facial reactions, speaking mouths, props, moving garden layers, subtitles and camera push-ins.
- An optional Higgsfield Seedance adapter. It is metered and blocked by default; scheduled runs must not call it unless `ALLOW_METERED_VIDEO_GENERATION=true` is deliberately set.
- The GitHub trial workflow can optionally upload natural-voice renders as private YouTube drafts when OAuth secrets are configured; pull-request runs never upload. The Railway scheduler is not connected to publishing, and no real channel upload has been verified.
- Both upload adapters mark videos as Made for Kids; the direct API uploader defaults to private, includes Hindi language metadata, and can attach the episode thumbnail. The Apps Script alternative still requires a publicly reachable video URL.
- A GitHub Actions trial workflow that renders MP4s plus a clean 1280x720 episode thumbnail and a 720x1280 Short poster frame. This is a render trial, not an auto-publishing pipeline.
- The trial renders a six-minute original Hindi episode from 12 authored story beats and a separate 40-second, four-beat Short; the Short preserves its complete 16:9 action over a moving blurred portrait background. Both outputs receive duration, dimensions, audio/video, and motion QA and are uploaded as artifacts.
- A CI video check that requires audio/video streams and movement across one-second samples, so frozen renders fail the trial.
- A focused Python check covers the direct YouTube upload metadata and privacy validation.

The procedural renderer is a 2D cartoon prototype. It is not 3D or AI-generated video. Svara Hindi TTS is the default for every speaking character; all roles use one shared voice identity and identical pitch treatment so the cast does not sound like unrelated voices. Svara is a public free ZeroGPU demo with shared quotas and no availability guarantee, so a failed request stops the render instead of silently substituting eSpeak. eSpeak remains available only as an explicit preview (`KIDS_TTS_PROVIDER=preview`). Listen to and approve voice quality before publishing.

## Local render

The Linux trial workflow installs FFmpeg, eSpeak and Noto Devanagari fonts, then runs:

```sh
KIDS_OUTPUT="/tmp/kids-video.mp4" \
python -m app.local_render
```

The current authored Hindi episode and Short beats are the fixed seed-to-garden story in `SCENES` and `SHORT_SCENES` in `app/local_render.py`. Custom-topic generation is not yet connected to this renderer. The renderer remains a flat 2D prototype; it should not publish automatically.

Chintu, Mini, Golu, Tinku and the narrator all use the same Svara voice identity and the same small pitch lift; character differences come from the script and acting. This makes one request per speaking scene to the public Svara Space. No retries or paid fallback are used. Set `KIDS_TTS_PROVIDER=preview` only when you intentionally want the robotic eSpeak preview. Each render writes a `.voices.json` sidecar that records the provider and per-scene voice modes.

## API

- `GET /` and `GET /health` — service status and provider readiness.
- `GET /pipeline/preview` — inspect a planned story and pipeline.
- `POST /pipeline/run` — create a pipeline manifest.
- `POST /pipeline/generate-scenes` — submit scene jobs only when the cost gate is explicitly open and provider credentials are configured.
- `GET /docs` — FastAPI docs.

## Optional private YouTube upload setup

Manually running the trial workflow selects Svara by default (you can choose preview explicitly). Pull-request checks always use preview. Scheduled runs use Svara only when the repository variable and all YouTube OAuth secrets are configured; otherwise they use preview. The upload helper refuses to upload preview audio. Nothing here changes a video's visibility to public.

For scheduled natural-voice private drafts, add repository Actions secrets named `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN`, then add an Actions variable `KIDS_TTS_PROVIDER` with value `svara`. Create/authorize the OAuth client with the Google account that owns the channel and the `youtube.upload` scope. Never paste these credentials into chat. A manual Svara render does not require YouTube credentials; without them the private upload step skips.

## Remaining work before public publishing

1. Improve the rig artwork, movement, lip-sync and Hindi voice quality; review full-length episodes by eye and ear.
2. Assemble generated/local scenes into both long and vertical cuts, then add music/SFX and improve thumbnail design.
3. Add automated audio, animation and safety quality gates.
4. Complete the one-time Google authorization, verify a real private upload and thumbnail on the channel, and confirm the Made-for-Kids setting. The direct GitHub upload does not need public video hosting.
5. Add an analytics feedback loop and verify the complete path before calling the channel automated.

No paid provider is required by the local renderer. Do not add credits, subscriptions or paid services without the user's explicit approval.
