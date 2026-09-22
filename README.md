# Auto Kids YouTube

Free-first tooling for planning and producing original Hindi children's cartoons.

## Current capabilities

- Deterministic Hindi story, metadata, character and scene-plan generation.
- A family-safety precheck for story text and scene prompts.
- A procedural 2D renderer in `app/local_render.py`: per-frame character poses, walking motion, facial reactions, speaking mouths, props, moving garden layers, subtitles and camera push-ins.
- An optional Higgsfield Seedance adapter. It is metered and blocked by default; scheduled runs must not call it unless `ALLOW_METERED_VIDEO_GENERATION=true` is deliberately set.
- YouTube uploader adapters and an Apps Script bridge are present, but no end-to-end upload is wired to the scheduler. A publicly reachable video file and one-time Google authorization are still needed.
- A GitHub Actions trial workflow that renders an MP4 artifact. This is a render trial, not an auto-publishing pipeline.
- A CI video check that requires audio/video streams and movement across one-second samples, so frozen renders fail the trial.

The procedural renderer is a 2D cartoon prototype. It is not 3D or AI-generated video. Its default eSpeak track is a robotic preview and is not suitable for publishing. An opt-in Svara Hindi path is available for the child cast; it uses one shared voice identity and a small pitch lift for a youthful sound. Tinku remains robotic by design. Svara is a public free ZeroGPU demo with shared quotas and no availability guarantee, so a failed request stops the render instead of silently substituting eSpeak. Listen to and approve voice quality before publishing.

## Local render

The Linux trial workflow installs FFmpeg, eSpeak and Noto Devanagari fonts, then runs:

```sh
KIDS_TOPIC="चिंटू और दोस्तों की बगीचे वाली खोज" \
KIDS_OUTPUT="/tmp/kids-video.mp4" \
python -m app.local_render
```

The story beats currently live in `SCENES` in `app/local_render.py`. The current renderer is a visual-quality prototype; it should not publish automatically.

To request Svara voices for Chintu, Mini and Golu, set `KIDS_TTS_PROVIDER=svara`. This makes one request per speaking scene to the public Svara Space. No retries or paid fallback are used. Leave `KIDS_TTS_PROVIDER` unset for the robotic eSpeak preview. Each render writes a `.voices.json` sidecar that records the provider and per-scene voice modes.

## API

- `GET /` and `GET /health` — service status and provider readiness.
- `GET /pipeline/preview` — inspect a planned story and pipeline.
- `POST /pipeline/run` — create a pipeline manifest.
- `POST /pipeline/generate-scenes` — submit scene jobs only when the cost gate is explicitly open and provider credentials are configured.
- `GET /docs` — FastAPI docs.

## Remaining work before publishing

1. Improve the rig artwork, movement, lip-sync and Hindi voice quality; review full-length episodes by eye and ear.
2. Assemble generated/local scenes into both long and vertical cuts, then add music/SFX and thumbnails.
3. Add automated audio, animation and safety quality gates.
4. Connect video hosting to the Apps Script bridge, complete the private YouTube upload flow, and verify the Made-for-Kids setting.
5. Add an analytics feedback loop and verify the complete path before calling the channel automated.

No paid provider is required by the local renderer. Do not add credits, subscriptions or paid services without the user's explicit approval.
