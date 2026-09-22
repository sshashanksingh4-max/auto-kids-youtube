# Zero-Cost Trial Mode

The project is designed to avoid new paid spend during the validation phase.

## Cost rules
- Never purchase credits or upgrade a provider automatically.
- Prefer free tiers, free trials, local/open-source tools, and existing connected services.
- Keep generation volume small until the workflow is proven.
- Keep `ALLOW_METERED_VIDEO_GENERATION=false` (the default). API credentials alone must never authorize scheduled Seedance jobs.
- Only use a provider's free-generation route when its model, duration and current free allowance are verified; never assume a configured API key is free.
- Never store provider secrets in Git.
- Treat every provider capability as optional and add fallbacks where possible.

## Current trial target
- 1 long-form Hindi kids video per day
- 1 Hindi Short per day
- Increase toward 2+2 only after the workflow is stable.

## Media fallback strategy
1. Use available free AI image generation for character and scene assets.
2. Use local rendering tools such as FFmpeg for assembly, transitions, captions, and packaging.
3. Use local Hindi TTS when an online paid voice provider is unavailable.
4. Use free/open audio or procedural audio for background ambience and simple effects.
5. Only introduce paid generation after channel revenue is available and the user explicitly approves the spend.

## Current generation boundary

The current Higgsfield adapter calls the Seedance text-to-video API. It does not use Higgsfield's Genjutsu free-generation counter. For that reason the Seedance adapter is disabled unless `ALLOW_METERED_VIDEO_GENERATION=true` is set deliberately. The procedural local renderer remains available without provider credits.

## Monetization safety
The content engine must create original stories, original character combinations, meaningful narration, and non-repetitive episode structures. Do not reuse source videos or lightly alter copied material.
