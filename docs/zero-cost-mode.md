# Zero-Cost Trial Mode

The project is designed to avoid new paid spend during the validation phase.

## Cost rules
- Never purchase credits or upgrade a provider automatically.
- Prefer free tiers, free trials, local/open-source tools, and existing connected services.
- Keep generation volume small until the workflow is proven.
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

## Monetization safety
The content engine must create original stories, original character combinations, meaningful narration, and non-repetitive episode structures. Do not reuse source videos or lightly alter copied material.
