# Auto Kids YouTube

Production backend for an automated Hindi kids-video channel.

## Current pipeline
1. Content planning
2. Original Hindi story generation
3. Character and scene planning
4. Deterministic kids-safety precheck
5. Higgsfield scene-video job submission
6. YouTube metadata generation
7. Provider readiness checks
8. YouTube OAuth publishing adapter

## API
- `GET /` — service status
- `GET /health` — provider readiness
- `GET /pipeline/preview` — inspect a generated story/pipeline
- `POST /pipeline/run` — generate a pipeline manifest
- `POST /pipeline/generate-scenes` — submit scene video jobs when Higgsfield credentials are configured
- `GET /docs` — FastAPI docs

## Required production credentials
- Higgsfield API credentials for video generation
- A selected Higgsfield voice ID for automated Hindi narration
- YouTube OAuth credentials for publishing

The system never hard-codes or exposes provider secrets.
